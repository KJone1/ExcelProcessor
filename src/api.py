# pylint: disable=too-many-locals,broad-exception-caught,duplicate-code
import os
import webbrowser
from contextlib import asynccontextmanager
from typing import Annotated

import pypdf
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.core.excel import (
    discard_row_if_amount_missing,
    format_date_column,
    remap_categories,
    sort_by_category,
    standardize_columns,
)
from src.io.actual import import_payslip_to_actual, import_transactions_to_actual
from src.io.filesystem import decrypt_pdf, extract_payslip_data, read_excel, write_csv
from src.schemas.payslip import PayslipSyncRequest
from src.settings import settings


@asynccontextmanager
async def lifespan(_app: FastAPI):
    _ = webbrowser.open(
        f"http://{settings.server_host}:{settings.server_port}/ui/index.html"
    )
    yield
    if os.path.exists(settings.csv_file):
        os.remove(settings.csv_file)


app = FastAPI(title="Excel & Payslip Processor API", lifespan=lifespan)

# Serve frontend static files
app.mount("/ui", StaticFiles(directory="ui"), name="ui")


@app.get("/")
def read_root():
    """Redirect root access to the UI dashboard."""
    return RedirectResponse(url="/ui/index.html")


@app.get("/api/data")
def get_data(payslip_password: Annotated[str | None, Query()] = None):
    """
    Auto-detect the configured Excel and payslip files.
    Process excel sheet, calculate summary metrics, and return them.
    If the payslip is encrypted, decrypt with the provided password or environment password.
    """
    excel_exists = os.path.exists(settings.excel_file)
    payslip_exists = os.path.exists(settings.payslip_file)

    excel_response = None
    payslip_response = None

    if excel_exists:
        try:
            df_raw = read_excel(settings.excel_file)
            df = (
                df_raw.pipe(standardize_columns)
                .pipe(discard_row_if_amount_missing)
                .pipe(format_date_column)
                .pipe(remap_categories)
                .pipe(sort_by_category)
            )

            # Outflows (Amount > 0)
            total_spent = float(df[df["Amount"] > 0]["Amount"].sum()) if not df.empty else 0.0
            trans_count = len(df)

            spent_by_cat = df[df["Amount"] > 0].groupby("Category")["Amount"].sum()
            if not spent_by_cat.empty:
                top_cat = str(spent_by_cat.idxmax())
                top_cat_amt = float(spent_by_cat.max())
            else:
                top_cat = "N/A"
                top_cat_amt = 0.0

            transactions = df.to_dict(orient="records")

            excel_response = {
                "exists": True,
                "metrics": {
                    "total_spent": total_spent,
                    "trans_count": trans_count,
                    "top_category": top_cat,
                    "top_category_amount": top_cat_amt,
                },
                "transactions": transactions
            }
        except Exception as e:  # noqa: BLE001
            excel_response = {
                "exists": True,
                "error": f"Failed to process Excel file: {e!s}"
            }

    if payslip_exists:
        try:
            reader = pypdf.PdfReader(settings.payslip_file)
            requires_password = reader.is_encrypted

            payslip_data = None
            error_message = None

            password = (
                payslip_password
                if payslip_password is not None
                else settings.payslip_password
            )

            if requires_password and not password:
                # Password required but not supplied yet
                pass
            else:
                try:
                    if requires_password:
                        decrypt_pdf(settings.payslip_file, password)
                    extracted = extract_payslip_data(settings.payslip_file)
                    payslip_data = {
                        "date": extracted.date.isoformat(),
                        "taxable_income": extracted.taxable_income,
                        "net_to_bank": extracted.net_to_bank
                    }
                except Exception as ex:  # noqa: BLE001
                    error_message = f"Decryption failed: {ex!s}"

            payslip_response = {
                "exists": True,
                "requires_password": requires_password,
                "data": payslip_data,
                "error": error_message
            }
        except Exception as e:  # noqa: BLE001
            payslip_response = {
                "exists": True,
                "error": f"Failed to read PDF file: {e!s}"
            }

    return {
        "files": {
            "excel": settings.excel_file,
            "payslip": settings.payslip_file,
        },
        "excel": excel_response,
        "payslip": payslip_response
    }


@app.post("/api/sync/transactions")
def sync_transactions():
    """Process the configured Excel file and import transactions to Actual Budget."""
    if not os.path.exists(settings.excel_file):
        raise HTTPException(status_code=404, detail=f"{settings.excel_file} not found")

    try:
        df_raw = read_excel(settings.excel_file)
        df = (
            df_raw.pipe(standardize_columns)
            .pipe(discard_row_if_amount_missing)
            .pipe(format_date_column)
            .pipe(remap_categories)
            .pipe(sort_by_category)
        )
        write_csv(df, settings.csv_file)
        import_transactions_to_actual(settings.csv_file)
        return {"status": "success", "message": "Successfully synchronized transactions to Actual Budget"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Synchronization failed: {e!s}") from e


@app.post("/api/sync/payslip")
def sync_payslip(request: PayslipSyncRequest):
    """Decrypt the configured payslip and import salary to Actual Budget."""
    if not os.path.exists(settings.payslip_file):
        raise HTTPException(status_code=404, detail=f"{settings.payslip_file} not found")

    password = request.password or settings.payslip_password

    try:
        reader = pypdf.PdfReader(settings.payslip_file)
        if reader.is_encrypted:
            if not password:
                raise HTTPException(status_code=400, detail="Password required for encrypted payslip")
            decrypt_pdf(settings.payslip_file, password)

        payslip_data = extract_payslip_data(settings.payslip_file)
        import_payslip_to_actual(payslip_data)
        return {"status": "success", "message": "Successfully synchronized payslip to Actual Budget"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Synchronization failed: {e!s}") from e
