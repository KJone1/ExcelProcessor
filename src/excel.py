# pylint: disable=too-few-public-methods
from configparser import ConfigParser
from configparser import Error as ConfigParserError

import pandas as pd

from src.settings import settings


class ExcelProcessor:
    def __init__(self) -> None:
        self.categories: dict[str, list[str]] = self._load_categories()

    def process(self) -> None:
        df = pd.read_excel(settings.excel_file, skiprows=settings.excel_skiprows)
        df = (
            df.pipe(self._prepare_transactions)
            .pipe(self._format_date_column)
            .pipe(self._remap_categories)
            .sort_values(by="Category")
        )
        df.to_csv(settings.csv_file, index=False)

    @staticmethod
    def _prepare_transactions(dataframe: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "Date": dataframe["תאריך\nעסקה"],
                "Payee": dataframe["שם בית עסק"],
                "Amount": dataframe["סכום\nחיוב"],
                "Category": dataframe["ענף"],
            }
        ).dropna(subset=["Amount"])

    def _remap_categories(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        new_df = dataframe.copy()
        amounts = new_df["Amount"]
        mapped: pd.Series = pd.Series(None, index=new_df.index, dtype="object")

        reimbursable = amounts.lt(0)
        mapped.loc[reimbursable] = "Reimburseable"

        if mapped.isna().any():
            payees = new_df["Payee"].str.lower()
            rent = payees.str.contains("paybox", regex=False, na=False) & (
                amounts.between(2900, 3100) | amounts.between(800, 900)
            )
            mapped.loc[rent] = "Home & Decor"

        unmatched = mapped.isna()
        if unmatched.any():
            mapped.loc[unmatched] = new_df.loc[unmatched].apply(
                self._map_category, axis=1
            )
        new_df["Category"] = mapped
        return new_df

    @staticmethod
    def _format_date_column(
        dataframe: pd.DataFrame,
        column_name: str = "Date",
        date_format: str = "%Y-%m-%d",
    ) -> pd.DataFrame:
        new_df = dataframe.copy()
        if column_name in new_df.columns:
            new_df[column_name] = pd.to_datetime(new_df[column_name]).dt.strftime(
                date_format
            )
        return new_df

    @staticmethod
    def _load_categories() -> dict[str, list[str]]:
        parser = ConfigParser(
            allow_no_value=True,
            delimiters=("=",),
            interpolation=None,
        )
        parser.optionxform = lambda optionstr: optionstr  # type: ignore[method-assign]
        try:
            with open(settings.categories_file, "r", encoding="utf-8") as f:
                parser.read_file(f)
            return {category: list(parser[category]) for category in parser.sections()}
        except (OSError, ConfigParserError):
            pass
        return {}

    def _check_keywords(
        self,
        row: pd.Series,
        category: str,
        *,
        match_payee: bool,
        match_source_category: bool,
    ) -> str | None:
        name = row["Payee"].lower()
        cat = row["Category"]
        keywords = self.categories.get(category, [])
        for keyword in keywords:
            if keyword.startswith("e:"):
                if match_payee and name == keyword[2:]:
                    return category
            elif (match_payee and keyword in name) or (
                match_source_category and cat == keyword
            ):
                return category
        return None

    def _map_category(self, row: pd.Series) -> str:
        for category in self.categories:
            res = self._check_keywords(
                row,
                category,
                match_payee=True,
                match_source_category=False,
            )
            if res:
                return res

        for category in self.categories:
            res = self._check_keywords(
                row,
                category,
                match_payee=False,
                match_source_category=True,
            )
            if res:
                return res

        return "Misc & One-offs"
