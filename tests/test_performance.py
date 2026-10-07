"""Hand-worked figures from sample_data.csv, valued at last trade prices
(AAPL 190.27, MSFT 425.82, TSLA 175.71) so no internet is needed.

Total invested = 15,722.94   Total sales = 9,637.44
Current value  = 10 x 190.27 + 9 x 425.82 + 4 x 175.71 = 6,437.92
"""

from datetime import date

import pandas as pd
import pytest

from portfolio.holdings import compute_positions, open_positions
from portfolio.performance import performance_summary, value_over_time, xirr

TODAY = date(2026, 10, 7)
CURRENT_VALUE = 6437.92


def test_lifetime_metrics(sample_tx):
    perf = performance_summary(sample_tx, CURRENT_VALUE, TODAY)
    assert perf["total_invested"] == pytest.approx(15722.94)
    assert perf["total_sales"] == pytest.approx(9637.44)
    assert perf["lifetime_proceeds"] == pytest.approx(9637.44 + 6437.92)
    assert perf["total_return"] == pytest.approx(9637.44 + 6437.92 - 15722.94)
    assert perf["total_return_pct"] == pytest.approx(352.42 / 15722.94)


def test_total_return_equals_realized_plus_unrealized(sample_tx):
    perf = performance_summary(sample_tx, CURRENT_VALUE, TODAY)
    realized = compute_positions(sample_tx)["realized_pnl"].sum()
    unrealized = CURRENT_VALUE - open_positions(sample_tx)["invested"].sum()
    assert perf["total_return"] == pytest.approx(realized + unrealized)


def test_xirr_simple_one_year():
    assert xirr([(date(2025, 1, 1), -100), (date(2026, 1, 1), 110)]) == pytest.approx(0.10, abs=1e-6)


def test_xirr_loss():
    assert xirr([(date(2025, 1, 1), -100), (date(2026, 1, 1), 80)]) == pytest.approx(-0.20, abs=1e-6)


def test_xirr_undefined_without_both_signs():
    assert xirr([]) is None
    assert xirr([(date(2025, 1, 1), -100)]) is None


def test_xirr_for_sample_is_small_positive(sample_tx):
    perf = performance_summary(sample_tx, CURRENT_VALUE, TODAY)
    # Small gain (352.42) spread over ~2.75 years of varying capital.
    assert 0 < perf["xirr"] < 0.05


def test_value_series_without_market_data(sample_tx):
    series = value_over_time(sample_tx, pd.DataFrame(), TODAY)
    first, last = series.iloc[0], series.iloc[-1]
    assert first["date"] == pd.Timestamp("2024-01-03")
    assert first["value"] == pytest.approx(1850.70)
    assert first["net_invested"] == pytest.approx(1850.70)
    assert last["date"] == pd.Timestamp(TODAY)
    assert last["value"] == pytest.approx(CURRENT_VALUE)
    assert last["net_invested"] == pytest.approx(15722.94 - 9637.44)


def test_value_series_uses_market_prices_when_given(sample_tx):
    history = pd.DataFrame(
        {"AAPL": [200.0], "MSFT": [400.0], "TSLA": [300.0]},
        index=pd.to_datetime(["2026-10-01"]),
    )
    last = value_over_time(sample_tx, history, TODAY).iloc[-1]
    assert last["value"] == pytest.approx(10 * 200 + 9 * 400 + 4 * 300)
