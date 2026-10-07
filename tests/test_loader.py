import io

import pandas as pd
import pytest

from portfolio.loader import COLUMNS, load_saved, read_transactions_csv, save


def csv(text: str) -> io.StringIO:
    return io.StringIO(text.strip())


def test_sample_file_maps_column_aliases(sample_tx):
    assert list(sample_tx.columns) == COLUMNS
    assert len(sample_tx) == 13
    assert set(sample_tx["symbol"]) == {"AAPL", "MSFT", "TSLA"}
    assert sample_tx["date"].is_monotonic_increasing


def test_normalizes_case_and_short_types():
    tx = read_transactions_csv(csv("""
Date,Ticker,Side,Qty,Price
2024-01-03, aapl ,b,10,185.07
2024-02-03,aapl,Sell,4,190
"""))
    assert tx["symbol"].tolist() == ["AAPL", "AAPL"]
    assert tx["type"].tolist() == ["BUY", "SELL"]


def test_missing_column_is_reported():
    with pytest.raises(ValueError, match="Missing column 'price'"):
        read_transactions_csv(csv("date,ticker,type,quantity\n2024-01-03,AAPL,BUY,1"))


def test_invalid_rows_report_line_numbers():
    with pytest.raises(ValueError, match=r"2 row\(s\).*line 3, 4"):
        read_transactions_csv(csv("""
date,ticker,type,quantity,price
2024-01-03,AAPL,BUY,10,185.07
not-a-date,AAPL,BUY,10,185.07
2024-01-05,AAPL,HOLD,10,185.07
"""))


def test_save_and_load_round_trip(sample_tx, tmp_path):
    path = tmp_path / "data" / "transactions.csv"
    assert load_saved(path).empty
    save(sample_tx, path)
    pd.testing.assert_frame_equal(load_saved(path), sample_tx)
