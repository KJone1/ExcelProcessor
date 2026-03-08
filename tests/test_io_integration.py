import pandas as pd
import os
from src.io.filesystem import read_excel
from src.core.excel import discard_row_if_amount_missing
from tests.generate_mock_excel import generate_mock_excel

GOLDEN_FILE = "golden_statement.xlsx"
VALUE_COL = "סכום\nחיוב"
DATE_COL = "תאריך\nעסקה"

def test_read_golden_excel():
    if not os.path.exists(GOLDEN_FILE):
        generate_mock_excel(GOLDEN_FILE)
        
    assert os.path.exists(GOLDEN_FILE), "Golden file missing"
    
    result = read_excel(GOLDEN_FILE, skiprows=3)
    df = result.unwrap()
    
    df = discard_row_if_amount_missing(df, VALUE_COL)
    
    assert not df.empty
    assert "שם בית עסק" in df.columns
    assert "ענף" in df.columns
    assert VALUE_COL in df.columns
    
    categories = df["ענף"].unique()
    assert "מסעדות" in categories or "תקשורת ומחשבים" in categories
    
    if not pd.api.types.is_datetime64_any_dtype(df[DATE_COL]):
        df[DATE_COL] = pd.to_datetime(df[DATE_COL])
        
    assert pd.api.types.is_datetime64_any_dtype(df[DATE_COL])
    assert df[DATE_COL].iloc[0].year == 2026
