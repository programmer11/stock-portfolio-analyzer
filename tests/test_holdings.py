"""Expected values are worked out by hand from sample_data.csv (average-cost method).

AAPL: buy 10 @ 185.07, sell 7 @ 215.80 (+215.11), buy 6 @ 169.23,
      sell 4 @ 195.58 (avg 174.51 -> +84.28), buy 5 @ 190.27 -> 10 held, avg 182.39
MSFT: buy 10 @ 420.30, sell 3 @ 400.38 (-59.76), buy 7 @ 410.69,
      sell 5 @ 425.82 (avg 415.495 -> +51.625) -> 9 held, avg 415.495
TSLA: buy 13 @ 246.53, sell 10 @ 260.86 (+143.30), buy 9 @ 180.31,
      sell 8 @ 175.71 (avg 196.865 -> -169.24) -> 4 held, avg 196.865
"""

import pandas as pd
import pytest

from portfolio.holdings import compute_positions, last_trade_prices, open_positions


def by_symbol(df):
    return df.set_index("symbol")


def test_quantities_and_average_cost(sample_tx):
    pos = by_symbol(open_positions(sample_tx))
    assert pos["quantity"].to_dict() == {"AAPL": 10, "MSFT": 9, "TSLA": 4}
    assert pos.loc["AAPL", "avg_cost"] == pytest.approx(182.39)
    assert pos.loc["MSFT", "avg_cost"] == pytest.approx(415.495)
    assert pos.loc["TSLA", "avg_cost"] == pytest.approx(196.865)
    assert pos.loc["AAPL", "invested"] == pytest.approx(1823.90)
    assert pos.loc["MSFT", "invested"] == pytest.approx(3739.455)
    assert pos.loc["TSLA", "invested"] == pytest.approx(787.46)


def test_realized_profit(sample_tx):
    pos = by_symbol(compute_positions(sample_tx))
    assert pos.loc["AAPL", "realized_pnl"] == pytest.approx(215.11 + 84.28)
    assert pos.loc["MSFT", "realized_pnl"] == pytest.approx(-59.76 + 51.625)
    assert pos.loc["TSLA", "realized_pnl"] == pytest.approx(143.30 - 169.24)


def test_fully_sold_position_is_closed_but_keeps_realized_profit():
    tx = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01", "2024-06-01"]).date,
        "symbol": ["XYZ", "XYZ"], "type": ["BUY", "SELL"],
        "quantity": [5.0, 5.0], "price": [100.0, 120.0],
    })
    assert open_positions(tx).empty
    pos = by_symbol(compute_positions(tx))
    assert pos.loc["XYZ", "quantity"] == 0
    assert pos.loc["XYZ", "realized_pnl"] == pytest.approx(100.0)


def test_oversell_is_capped_at_shares_held():
    tx = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01", "2024-06-01"]).date,
        "symbol": ["XYZ", "XYZ"], "type": ["BUY", "SELL"],
        "quantity": [5.0, 8.0], "price": [100.0, 120.0],
    })
    pos = by_symbol(compute_positions(tx))
    assert pos.loc["XYZ", "quantity"] == 0
    assert pos.loc["XYZ", "realized_pnl"] == pytest.approx(100.0)


def test_last_trade_prices(sample_tx):
    assert last_trade_prices(sample_tx) == {"AAPL": 190.27, "MSFT": 425.82, "TSLA": 175.71}
