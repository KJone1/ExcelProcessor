# pylint: disable=too-many-locals,broad-exception-caught
import os
import webbrowser
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, cast

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.actual import ActualUploader
from src.payslip import PayslipData
from src.settings import settings


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    _ = webbrowser.open(
        f"http://{settings.server_host}:{settings.server_port}/ui/index.html"
    )
    yield
    if os.path.exists(settings.csv_file):
        os.remove(settings.csv_file)


app = FastAPI(title="Excel & Payslip Processor API", lifespan=lifespan)
app.mount("/ui", StaticFiles(directory="ui"), name="ui")


@app.get("/")
def read_root() -> RedirectResponse:
    return RedirectResponse(url="/ui/index.html")


@app.get("/api/data")
def get_data(request: Request) -> dict[str, Any]:
    excel_response: dict[str, Any] | None = None
    payslip_response: dict[str, Any] | None = None

    if os.path.exists(settings.csv_file):
        try:
            df = pd.read_csv(
                settings.csv_file,
                dtype={"Date": str, "Payee": str, "Category": str},
                keep_default_na=False,
            )
            total_spent = (
                float(df[df["Amount"] > 0]["Amount"].sum()) if not df.empty else 0.0
            )
            trans_count = len(df)

            spent_by_cat = df[df["Amount"] > 0].groupby("Category")["Amount"].sum()
            if not spent_by_cat.empty:
                top_cat = str(spent_by_cat.idxmax())
                top_cat_amt = float(spent_by_cat.max())
            else:
                top_cat = "N/A"
                top_cat_amt = 0.0

            excel_response = {
                "exists": True,
                "metrics": {
                    "total_spent": total_spent,
                    "trans_count": trans_count,
                    "top_category": top_cat,
                    "top_category_amount": top_cat_amt,
                },
                "transactions": df.to_dict(orient="records"),
            }
        except Exception as error:
            excel_response = {
                "exists": True,
                "error": f"Failed to read CSV file: {error!s}",
            }

    payslip_data = cast(PayslipData | None, request.app.state.payslip_data)
    if payslip_data is not None:
        payslip_response = {
            "exists": True,
            "requires_password": False,
            "data": {
                "date": payslip_data.date.isoformat(),
                "taxable_income": payslip_data.taxable_income,
                "net_to_bank": payslip_data.net_to_bank,
            },
            "error": None,
        }

    return {
        "files": {
            "excel": settings.csv_file,
            "payslip": settings.payslip_file,
        },
        "excel": excel_response,
        "payslip": payslip_response,
    }


@app.post("/api/sync/transactions")
def sync_transactions() -> dict[str, str]:
    if not os.path.exists(settings.csv_file):
        raise HTTPException(status_code=404, detail=f"{settings.csv_file} not found")

    try:
        ActualUploader().import_transactions(settings.csv_file)
        return {
            "status": "success",
            "message": "Successfully synchronized transactions to Actual Budget",
        }
    except Exception as error:
        raise HTTPException(
            status_code=500, detail=f"Synchronization failed: {error!s}"
        ) from error


@app.post("/api/sync/payslip")
def sync_payslip(request: Request) -> dict[str, str]:
    payslip_data = cast(PayslipData | None, request.app.state.payslip_data)
    if payslip_data is None:
        raise HTTPException(status_code=404, detail="Payslip not available")

    try:
        ActualUploader().import_payslip(payslip_data)
        return {
            "status": "success",
            "message": "Successfully synchronized payslip to Actual Budget",
        }
    except Exception as error:
        raise HTTPException(
            status_code=500, detail=f"Synchronization failed: {error!s}"
        ) from error
