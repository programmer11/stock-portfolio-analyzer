"""Replay trades into positions: quantity, average cost and realized profit."""

import pandas as pd

POSITION_COLUMNS = ["symbol", "quantity", "avg_cost", "invested", "realized_pnl"]


def compute_positions(tx: pd.DataFrame) -> pd.DataFrame:
    """Replay every trade in date order using the average-cost method.

    Returns one row per symbol ever traded, including fully sold ones:
      quantity     shares still held
      avg_cost     average cost per held share (0 when nothing is held)
      invested     cost basis of the shares still held
      realized_pnl profit from sales: (sell price - average cost) x shares sold
    Sells larger than the shares held are capped at the shares held.
    """
    state = {}  # symbol -> [quantity, cost basis, realized pnl]
    for row in tx.sort_values("date", kind="stable").itertuples():
        qty, cost, realized = state.get(row.symbol, [0.0, 0.0, 0.0])
        if row.type == "BUY":
            qty += row.quantity
            cost += row.quantity * row.price
        else:
            sell_qty = min(row.quantity, qty)
            if qty > 0:
                avg = cost / qty
                realized += (row.price - avg) * sell_qty
                cost -= avg * sell_qty
            qty -= sell_qty
        state[row.symbol] = [qty, cost, realized]

    rows = []
    for symbol, (qty, cost, realized) in state.items():
        held = qty > 1e-9
        rows.append({
            "symbol": symbol,
            "quantity": qty if held else 0.0,
            "avg_cost": cost / qty if held else 0.0,
            "invested": cost if held else 0.0,
            "realized_pnl": realized,
        })
    return pd.DataFrame(rows, columns=POSITION_COLUMNS)


def open_positions(tx: pd.DataFrame) -> pd.DataFrame:
    """Positions with shares still held."""
    positions = compute_positions(tx)
    return positions[positions["quantity"] > 0].reset_index(drop=True)


def last_trade_prices(tx: pd.DataFrame) -> dict:
    """Most recent transaction price per symbol, used when live prices are unavailable."""
    latest = tx.sort_values("date", kind="stable").groupby("symbol").last()
    return latest["price"].to_dict()
