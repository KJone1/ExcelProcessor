import pandas as pd

from src.core.categories import map_category


def standardize_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    new_df = dataframe.copy()
    column_mapping = {
        "תאריך\nעסקה": "Date",
        "שם בית עסק": "Payee",
        "סכום\nחיוב": "Amount",
        "ענף": "Category",
    }
    return new_df[list(column_mapping.keys())].rename(columns=column_mapping)


def discard_row_if_amount_missing(
    dataframe: pd.DataFrame, column_name: str = "Amount"
) -> pd.DataFrame:
    new_df = dataframe.copy()
    if column_name in new_df.columns:
        new_df = new_df.dropna(subset=[column_name])
    return new_df


def sort_by_category(
    dataframe: pd.DataFrame, column_name: str = "Category"
) -> pd.DataFrame:
    if column_name not in dataframe.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame")
    return dataframe.sort_values(by=[column_name])


def remap_categories(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    new_df = dataframe.copy()
    new_df["Category"] = new_df.apply(map_category, axis=1)
    return new_df


def format_date_column(
    dataframe: pd.DataFrame, column_name: str = "Date", date_format: str = "%Y-%m-%d"
) -> pd.DataFrame:
    new_df = dataframe.copy()
    if column_name in new_df.columns:
        new_df[column_name] = pd.to_datetime(new_df[column_name]).dt.strftime(
            date_format
        )
    return new_df
