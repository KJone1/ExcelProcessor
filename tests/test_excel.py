import pandas as pd
import pytest
import os
from src.core.excel import (
    standardize_columns,
    discard_row_if_amount_missing, 
    sort_by_category
)
from src.io.filesystem import read_excel
from tests.generate_mock_excel import generate_mock_excel

GOLDEN_FILE = "tests/data/golden_statement.xlsx"

@pytest.fixture(scope="module")
def raw_df():
    if not os.path.exists(GOLDEN_FILE):
        os.makedirs(os.path.dirname(GOLDEN_FILE), exist_ok=True)
        generate_mock_excel(GOLDEN_FILE)
    
    return read_excel(GOLDEN_FILE).unwrap()

@pytest.fixture(scope="module")
def prepared_df(raw_df):
    return standardize_columns(raw_df)

def test_standardize_columns(raw_df):
    df = standardize_columns(raw_df)
    expected_columns = ["Date", "Payee", "Amount", "Category"]
    assert all(col in df.columns for col in expected_columns)
    assert len(df.columns) == len(expected_columns)

def test_discard_row_if_amount_missing(prepared_df):
    processed_df = discard_row_if_amount_missing(prepared_df)
    
    assert len(processed_df) == 980
    assert not processed_df["Amount"].isna().any()

def test_sort_by_category(prepared_df):
    df = discard_row_if_amount_missing(prepared_df)
    sorted_df = sort_by_category(df)
    
    categories = sorted_df["Category"].dropna().tolist()
    assert categories == sorted(categories)

def test_sort_by_category_missing_col(prepared_df):
    with pytest.raises(ValueError):
        sort_by_category(prepared_df, "missing_col")
