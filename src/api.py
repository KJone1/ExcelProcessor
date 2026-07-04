# pylint: disable=too-many-locals,broad-exception-caught,duplicate-code
import os
import webbrowser
from contextlib import asynccontextmanager
from typing import Annotated

import pypdf
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.core.excel import (
    discard_row_if_amount_missing,
    format_date_column,
    remap_categories,
    sort_by_category,
    standardize_columns,
)
from src.io.actual import import_payslip_to_actual, import_transactions_to_actual
from src.io.filesystem import decrypt_pdf, extract_payslip_data, read_excel, write_csv


@asynccontextmanager
async def lifespan(_app: FastAPI):
    _ = webbrowser.open("http://localhost:8000/ui/index.html")
    yield
    if os.path.exists("actual.csv"):
        os.remove("actual.csv")


app = FastAPI(title="Excel & Payslip Processor API", lifespan=lifespan)

# Serve frontend static files
app.mount("/ui", StaticFiles(directory="ui"), name="ui")


class PayslipSyncRequest(BaseModel):
    """Request model for syncing an encrypted payslip PDF."""
    password: str | None = None


@app.get("/")
def read_root():
    """Redirect root access to the UI dashboard."""
    return RedirectResponse(url="/ui/index.html")


@app.get("/api/data")
def get_data(payslip_password: Annotated[str | None, Query()] = None):
    """
    Auto-detect local files (data.xlsx and payslip.pdf).
    Process excel sheet, calculate summary metrics, and return them.
    If payslip.pdf is encrypted, decrypt with the provided password or environment password.
    """
    excel_exists = os.path.exists("data.xlsx")
    payslip_exists = os.path.exists("payslip.pdf")

    excel_response = None
    payslip_response = None

    if excel_exists:
        try:
            df_raw = read_excel("data.xlsx", skiprows=3)
            df = (
                df_raw.pipe(standardize_columns)
                .pipe(discard_row_if_amount_missing)
                .pipe(format_date_column)
                .pipe(remap_categories)
                .pipe(sort_by_category)
            )

            # Outflows (Amount > 0)
            total_spent = float(df[df["Amount"] > 0]["Amount"].sum()) if not df.empty else 0.0
            avg_trans = float(df["Amount"].mean()) if not df.empty else 0.0
            trans_count = int(len(df))

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
                    "avg_trans": avg_trans,
                    "trans_count": trans_count,
                    "top_category": top_cat,
                    "top_category_amount": top_cat_amt,
                },
                "transactions": transactions
            }
        except Exception as e:
            excel_response = {
                "exists": True,
                "error": f"Failed to process Excel file: {str(e)}"
            }

    if payslip_exists:
        try:
            reader = pypdf.PdfReader("payslip.pdf")
            requires_password = reader.is_encrypted

            payslip_data = None
            error_message = None

            env_pwd = os.getenv("PAYSLIP_PASSWORD")
            password = payslip_password if payslip_password is not None else (env_pwd if env_pwd is not None else "")

            if requires_password and not password:
                # Password required but not supplied yet
                pass
            else:
                try:
                    if requires_password:
                        decrypt_pdf("payslip.pdf", password)
                    extracted = extract_payslip_data("payslip.pdf")
                    payslip_data = {
                        "date": extracted.date.isoformat(),
                        "taxable_income": extracted.taxable_income,
                        "net_to_bank": extracted.net_to_bank
                    }
                except Exception as ex:
                    error_message = f"Decryption failed: {str(ex)}"

            payslip_response = {
                "exists": True,
                "requires_password": requires_password,
                "data": payslip_data,
                "error": error_message
            }
        except Exception as e:
            payslip_response = {
                "exists": True,
                "error": f"Failed to read PDF file: {str(e)}"
            }

    return {
        "excel": excel_response,
        "payslip": payslip_response
    }


@app.post("/api/sync/transactions")
def sync_transactions():
    """Process local data.xlsx to CSV and import transactions to Actual Budget."""
    if not os.path.exists("data.xlsx"):
        raise HTTPException(status_code=404, detail="data.xlsx not found")

    try:
        df_raw = read_excel("data.xlsx", skiprows=3)
        df = (
            df_raw.pipe(standardize_columns)
            .pipe(discard_row_if_amount_missing)
            .pipe(format_date_column)
            .pipe(remap_categories)
            .pipe(sort_by_category)
        )
        csv_path = "actual.csv"
        write_csv(df, csv_path)
        import_transactions_to_actual(csv_path)
        return {"status": "success", "message": "Successfully synchronized transactions to Actual Budget"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Synchronization failed: {str(e)}") from e


@app.post("/api/sync/payslip")
def sync_payslip(request: PayslipSyncRequest):
    """Decrypt the local payslip.pdf and import salary to Actual Budget."""
    if not os.path.exists("payslip.pdf"):
        raise HTTPException(status_code=404, detail="payslip.pdf not found")

    password = request.password or os.getenv("PAYSLIP_PASSWORD", "")

    try:
        reader = pypdf.PdfReader("payslip.pdf")
        if reader.is_encrypted:
            if not password:
                raise HTTPException(status_code=400, detail="Password required for encrypted payslip")
            decrypt_pdf("payslip.pdf", password)

        payslip_data = extract_payslip_data("payslip.pdf")
        import_payslip_to_actual(payslip_data)
        return {"status": "success", "message": "Successfully synchronized payslip to Actual Budget"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Synchronization failed: {str(e)}") from e
