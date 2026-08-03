from pydantic import BaseModel


class PayslipSyncRequest(BaseModel):
    """Request model for syncing an encrypted payslip PDF."""
    password: str | None = None
