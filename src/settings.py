from functools import cache
from typing import Annotated, ClassVar

from pydantic import AfterValidator, Field, SecretStr
from pydantic.networks import IPvAnyAddress
from pydantic_settings import BaseSettings, SettingsConfigDict


class ExcelSettings(BaseSettings):
    """Fields for reading and exporting credit card statements."""

    excel_skiprows: Annotated[int, Field(ge=0)] = 4
    excel_file: Annotated[str, Field(min_length=1)] = "data.xlsx"
    csv_file: Annotated[str, Field(min_length=1)] = "actual.csv"


class ActualSettings(BaseSettings):
    """Fields for connecting to Actual Budget."""

    actual_server_url: Annotated[str, Field(min_length=1)]
    actual_budget_id: Annotated[str, Field(min_length=1)]
    actual_password_secret: Annotated[
        SecretStr,
        Field(validation_alias="ACTUAL_PASSWORD", min_length=1, repr=False),
    ]

    @property
    def actual_password(self) -> str:
        return self.actual_password_secret.get_secret_value()


class PayslipSettings(BaseSettings):
    """Fields for reading and decrypting payslips."""

    payslip_file: Annotated[str, Field(min_length=1)] = "payslip.pdf"
    payslip_password_secret: Annotated[
        SecretStr, Field(validation_alias="PAYSLIP_PASSWORD", repr=False)
    ] = SecretStr("")

    @property
    def payslip_password(self) -> str:
        return self.payslip_password_secret.get_secret_value()


class Settings(ExcelSettings, ActualSettings, PayslipSettings):
    """Combined application settings and server configuration."""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        hide_input_in_errors=True,
    )

    server_host: Annotated[str, IPvAnyAddress, AfterValidator(str)] = "127.0.0.1"
    server_port: Annotated[int, Field(ge=1, le=65535)] = 4455


@cache
def get_settings() -> Settings:
    return Settings.model_validate({})


settings = get_settings()
