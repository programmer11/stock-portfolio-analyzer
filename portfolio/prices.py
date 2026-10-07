"""Market prices from yfinance, cached so the app doesn't refetch on every interaction."""

from datetime import date

import pandas as pd
import streamlit as st
import yfinance as yf

from portfolio.holdings import last_trade_prices


@st.cache_data(ttl=900, show_spinner="Fetching live prices…")
def fetch_live_prices(symbols: tuple[str, ...]) -> dict:
    """Latest close per symbol; symbols that fail are omitted."""
    prices = {}
    for sym in symbols:
        try:
            hist = yf.Ticker(sym).history(period="5d")
            if not hist.empty:
                prices[sym] = float(hist["Close"].dropna().iloc[-1])
        except Exception:
            pass
    return prices


@st.cache_data(ttl=3600, show_spinner="Fetching price history…")
def fetch_price_history(symbols: tuple[str, ...], start: date) -> pd.DataFrame:
    """Daily closes since `start`, one column per symbol; empty if unavailable."""
    try:
        data = yf.download(list(symbols), start=start, auto_adjust=False,
                           progress=False, threads=True)
    except Exception:
        return pd.DataFrame()
    if data.empty or "Close" not in data:
        return pd.DataFrame()
    return data["Close"].dropna(axis=1, how="all")


def clear_cache() -> None:
    fetch_live_prices.clear()
    fetch_price_history.clear()


def current_prices(tx: pd.DataFrame, symbols: list[str], use_live: bool) -> tuple[dict, dict]:
    """Return (price per symbol, source per symbol), falling back to the last trade price."""
    fallback = last_trade_prices(tx)
    live = fetch_live_prices(tuple(sorted(symbols))) if use_live and symbols else {}
    prices, sources = {}, {}
    for s in symbols:
        if s in live:
            prices[s], sources[s] = live[s], "Live"
        else:
            prices[s], sources[s] = fallback.get(s, 0.0), "Last trade"
    return prices, sources
