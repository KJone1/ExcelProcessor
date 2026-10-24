from pathlib import Path

import uvicorn

from src.api import app
from src.excel import ExcelProcessor
from src.payslip import PayslipData, PayslipProcessor
from src.settings import settings


def main() -> None:
    if Path(settings.excel_file).exists():
        ExcelProcessor().process()

    payslip_data: PayslipData | None = None
    if Path(settings.payslip_file).exists():
        payslip_data = PayslipProcessor().process()
    app.state.payslip_data = payslip_data

    print(
        f"Starting FastAPI backend on http://{settings.server_host}:{settings.server_port} ..."
    )
    uvicorn.run(
        app,
        host=settings.server_host,
        port=settings.server_port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
