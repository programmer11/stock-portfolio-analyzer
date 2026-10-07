"""Read and check transaction CSVs, and persist the saved transactions file."""

from pathlib import Path

import pandas as pd

COLUMNS = ["date", "symbol", "type", "quantity", "price"]

# Accepted alternative header names in uploaded CSVs.
COLUMN_ALIASES = {
    "date": ["date", "trade date", "trade_date", "transaction date"],
    "symbol": ["symbol", "ticker", "stock", "scrip"],
    "type": ["type", "transaction_type", "transaction type", "side", "action", "buy/sell"],
    "quantity": ["quantity", "qty", "shares", "units"],
    "price": ["price", "rate", "price per share", "unit price"],
}


def empty_transactions() -> pd.DataFrame:
    return pd.DataFrame(columns=COLUMNS)


def normalize_transactions(raw: pd.DataFrame) -> pd.DataFrame:
    """Map an uploaded table onto the standard columns and validate it.

    Raises ValueError with a readable message if required columns are missing
    or rows contain invalid values.
    """
    lookup = {str(c).strip().lower(): c for c in raw.columns}
    rename = {}
    for target, aliases in COLUMN_ALIASES.items():
        match = next((lookup[a] for a in aliases if a in lookup), None)
        if match is None:
            raise ValueError(
                f"Missing column '{target}'. Expected columns: {', '.join(COLUMNS)}."
            )
        rename[match] = target
    df = raw.rename(columns=rename)[COLUMNS].copy()

    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["symbol"] = df["symbol"].astype(str).str.strip().str.upper()
    df["type"] = df["type"].astype(str).str.strip().str.upper()
    df["type"] = df["type"].replace({"B": "BUY", "S": "SELL", "PURCHASE": "BUY", "SALE": "SELL"})
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    bad = (
        df["date"].isna()
        | (df["symbol"] == "")
        | ~df["type"].isin(["BUY", "SELL"])
        | ~(df["quantity"] > 0)
        | ~(df["price"] >= 0)
    )
    if bad.any():
        rows = ", ".join(str(i + 2) for i in df.index[bad][:10])  # +2: header row, 1-based
        raise ValueError(
            f"{int(bad.sum())} row(s) have invalid values (CSV line {rows}). "
            "Check that dates are valid, type is BUY or SELL, and quantity/price are positive numbers."
        )
    return df.sort_values("date", kind="stable").reset_index(drop=True)


def read_transactions_csv(source) -> pd.DataFrame:
    """Read a CSV from a path or file-like object and validate it."""
    return normalize_transactions(pd.read_csv(source))


def load_saved(path: Path) -> pd.DataFrame:
    """Load the saved transactions file, or an empty table if it doesn't exist."""
    if not Path(path).exists():
        return empty_transactions()
    return read_transactions_csv(path)


def save(df: pd.DataFrame, path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
