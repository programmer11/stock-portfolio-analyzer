"""Lifetime metrics, XIRR and the daily portfolio value series."""

from datetime import date

import pandas as pd


def xirr(cashflows: list[tuple[date, float]]) -> float | None:
    """Annualised internal rate of return for irregular cash flows.

    Investments are negative, proceeds (and current value) positive.
    Returns None when the rate cannot be determined.
    """
    flows = [(d, a) for d, a in cashflows if a != 0]
    if not flows or all(a >= 0 for _, a in flows) or all(a <= 0 for _, a in flows):
        return None
    start = min(d for d, _ in flows)
    years = [((d - start).days / 365.0, a) for d, a in flows]

    def npv(rate):
        return sum(a / (1 + rate) ** t for t, a in years)

    # Bisection: robust where Newton's method can diverge.
    lo, hi = -0.9999, 10.0
    f_lo, f_hi = npv(lo), npv(hi)
    if f_lo * f_hi > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        f_mid = npv(mid)
        if abs(f_mid) < 1e-7:
            break
        if f_lo * f_mid < 0:
            hi, f_hi = mid, f_mid
        else:
            lo, f_lo = mid, f_mid
    return (lo + hi) / 2


def performance_summary(tx: pd.DataFrame, current_value: float, today: date) -> dict:
    """Totals for the Historical Performance tab.

    lifetime_proceeds = cash received from sales + what the remaining holdings are worth.
    total_return      = lifetime_proceeds - total_invested.
    """
    buys = tx[tx["type"] == "BUY"]
    sells = tx[tx["type"] == "SELL"]
    total_invested = float((buys["quantity"] * buys["price"]).sum())
    total_sales = float((sells["quantity"] * sells["price"]).sum())
    lifetime_proceeds = total_sales + current_value
    total_return = lifetime_proceeds - total_invested

    flows = [
        (r.date, -r.quantity * r.price if r.type == "BUY" else r.quantity * r.price)
        for r in tx.itertuples()
    ]
    flows.append((today, current_value))

    return {
        "total_invested": total_invested,
        "total_sales": total_sales,
        "lifetime_proceeds": lifetime_proceeds,
        "current_value": current_value,
        "total_return": total_return,
        "total_return_pct": total_return / total_invested if total_invested else None,
        "xirr": xirr(flows),
    }


def value_over_time(tx: pd.DataFrame, price_history: pd.DataFrame, end: date) -> pd.DataFrame:
    """Daily portfolio value and net amount invested from the first trade to `end`.

    price_history: daily closes, indexed by date, one column per symbol (may be empty
    or missing symbols). Gaps are filled with the most recent transaction price, so
    the chart still works without market data.

    Returns columns: date, value, net_invested.
    """
    tx = tx.sort_values("date", kind="stable")
    days = pd.date_range(pd.Timestamp(tx["date"].min()), pd.Timestamp(end), freq="D")
    signed = tx.assign(
        date=pd.to_datetime(tx["date"]),
        qty=tx["quantity"].where(tx["type"] == "BUY", -tx["quantity"]),
        cash=(tx["quantity"] * tx["price"]).where(tx["type"] == "BUY", -tx["quantity"] * tx["price"]),
    )

    qty = (
        signed.pivot_table(index="date", columns="symbol", values="qty", aggfunc="sum")
        .reindex(days, fill_value=0).fillna(0).cumsum().clip(lower=0)
    )
    trade_px = (
        signed.pivot_table(index="date", columns="symbol", values="price", aggfunc="last")
        .reindex(days).ffill()
    )
    market_px = pd.DataFrame(index=days)
    if not price_history.empty:
        hist = price_history.copy()
        hist.index = pd.to_datetime(hist.index).tz_localize(None).normalize()
        market_px = hist[~hist.index.duplicated()].reindex(days).ffill()
    px = market_px.reindex(columns=qty.columns).combine_first(trade_px)[qty.columns].ffill()

    net_invested = signed.groupby("date")["cash"].sum().reindex(days, fill_value=0).cumsum()
    return pd.DataFrame({
        "date": days,
        "value": (qty * px).sum(axis=1).values,
        "net_invested": net_invested.values,
    })
