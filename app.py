"""Stock Portfolio Analyzer: the three tabs (screen layout only).

All calculations live in the `portfolio` package. Run with:  uv run streamlit run app.py
"""

from datetime import date
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from portfolio import loader, prices
from portfolio.holdings import compute_positions, open_positions
from portfolio.loader import normalize_transactions, read_transactions_csv
from portfolio.performance import performance_summary, value_over_time

DATA_FILE = Path(__file__).parent / "data" / "transactions.csv"
SAMPLE_FILE = Path(__file__).parent / "sample_data.csv"


# ---------- state ----------

def save_transactions(df: pd.DataFrame) -> None:
    loader.save(df, DATA_FILE)
    st.session_state.tx = df


def add_transactions(new: pd.DataFrame) -> None:
    combined = pd.concat([st.session_state.tx, new], ignore_index=True)
    save_transactions(combined.sort_values("date", kind="stable").reset_index(drop=True))


# ---------- formatting ----------

def money(x: float) -> str:
    return f"{x:,.2f}"


def pct(x: float | None) -> str:
    return "—" if x is None else f"{x * 100:,.2f}%"


# ---------- app ----------

st.set_page_config(page_title="Stock Portfolio Analyzer", page_icon="📈", layout="wide")

if "tx" not in st.session_state:
    try:
        st.session_state.tx = loader.load_saved(DATA_FILE)
    except ValueError as e:
        st.error(f"Could not read saved transactions: {e}")
        st.session_state.tx = loader.empty_transactions()

with st.sidebar:
    st.header("Settings")
    use_live = st.toggle(
        "Use live prices (Yahoo Finance)",
        value=True,
        help="Use exchange suffixes for non-US stocks, e.g. RELIANCE.NS or TCS.BO. "
        "If a price can't be fetched, the last transaction price is used.",
    )
    if st.button("Refresh prices"):
        prices.clear_cache()

st.title("📈 Stock Portfolio Analyzer")

tx = st.session_state.tx
holdings = open_positions(tx)
if not holdings.empty:
    price_map, sources = prices.current_prices(tx, holdings["symbol"].tolist(), use_live)
    holdings["price"] = holdings["symbol"].map(price_map)
    holdings["value"] = holdings["quantity"] * holdings["price"]
    holdings["pnl"] = holdings["value"] - holdings["invested"]
    holdings["pnl_pct"] = holdings["pnl"] / holdings["invested"]
    holdings["price_source"] = holdings["symbol"].map(sources)
current_value = float(holdings["value"].sum()) if not holdings.empty else 0.0

tab1, tab2, tab3 = st.tabs(["Input Transactions", "Current Portfolio", "Historical Performance"])

# ----- Tab 1: Input Transactions -----
with tab1:
    st.subheader("Input Transactions")
    col_csv, col_manual = st.columns(2, gap="large")

    with col_csv:
        with st.container(border=True):
            st.markdown("#### CSV Upload")
            st.caption("Upload your historical transactions. Expected columns: "
                       "`ticker, date, transaction_type, quantity, price` "
                       "(transaction_type is BUY or SELL).")
            uploaded = st.file_uploader("Upload historical transactions (CSV)", type=["csv"])
            s1, s2 = st.columns(2)
            s1.download_button("Download sample CSV", SAMPLE_FILE.read_bytes(),
                               file_name="sample_data.csv", mime="text/csv", width="stretch")
            if s2.button("Load sample data", width="stretch"):
                save_transactions(read_transactions_csv(SAMPLE_FILE))
                st.success("Loaded sample_data.csv.")
                st.rerun()
            if uploaded is not None:
                try:
                    parsed = read_transactions_csv(uploaded)
                except ValueError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Could not read the file: {e}")
                else:
                    st.dataframe(parsed, hide_index=True, width="stretch", height=200)
                    replace = st.checkbox("Replace existing transactions", value=False)
                    if st.button(f"Import {len(parsed)} transactions", type="primary"):
                        if replace:
                            save_transactions(parsed)
                        else:
                            add_transactions(parsed)
                        st.success(f"Imported {len(parsed)} transactions.")
                        st.rerun()

    with col_manual:
        with st.container(border=True):
            st.markdown("#### Manual Upload")
            with st.form("manual_entry", clear_on_submit=True):
                c1, c2 = st.columns(2)
                tx_date = c1.date_input("Date", value=date.today(), max_value=date.today())
                tx_type = c2.selectbox("Type", ["BUY", "SELL"])
                symbol = st.text_input("Symbol", placeholder="e.g. AAPL or RELIANCE.NS")
                c3, c4 = st.columns(2)
                qty = c3.number_input("Quantity", min_value=0.0, step=1.0)
                price = c4.number_input("Price per share", min_value=0.0, step=0.01, format="%.2f")
                if st.form_submit_button("Add transaction", type="primary"):
                    try:
                        row = normalize_transactions(pd.DataFrame([{
                            "date": tx_date, "symbol": symbol, "type": tx_type,
                            "quantity": qty, "price": price,
                        }]))
                    except ValueError:
                        st.error("Enter a symbol and a quantity greater than 0.")
                    else:
                        add_transactions(row)
                        st.success(f"Added {tx_type} {qty:g} {row.at[0, 'symbol']}.")
                        st.rerun()

    st.markdown("#### All transactions")
    if tx.empty:
        st.info("No transactions yet. Upload a CSV or add one manually. "
                "A sample file is included: sample_data.csv")
    else:
        edited = st.data_editor(
            tx,
            hide_index=True,
            width="stretch",
            num_rows="dynamic",
            column_config={
                "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                "symbol": st.column_config.TextColumn("Symbol"),
                "type": st.column_config.SelectboxColumn("Type", options=["BUY", "SELL"]),
                "quantity": st.column_config.NumberColumn("Quantity", min_value=0),
                "price": st.column_config.NumberColumn("Price", min_value=0, format="%.2f"),
            },
            key="tx_editor",
        )
        c1, c2, _ = st.columns([1, 1, 4])
        if c1.button("Save edits"):
            try:
                save_transactions(normalize_transactions(edited.dropna(how="all")))
            except ValueError as e:
                st.error(str(e))
            else:
                st.success("Saved.")
                st.rerun()
        if c2.button("Clear all"):
            save_transactions(loader.empty_transactions())
            st.rerun()

# ----- Tab 2: Current Portfolio -----
with tab2:
    st.subheader("Current Portfolio")
    if holdings.empty:
        st.info("No open positions. Add transactions in the Input Transactions tab.")
    else:
        total_pnl = holdings["pnl"].sum()
        total_cost = holdings["invested"].sum()
        realized = compute_positions(tx)["realized_pnl"].sum()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Current Value", money(current_value))
        m2.metric("Cost Basis", money(total_cost))
        m3.metric("Profit & Gains", money(total_pnl),
                  delta=pct(total_pnl / total_cost if total_cost else None),
                  help="Unrealized: current value of shares you hold minus what they cost.")
        m4.metric("Realized Profit", money(realized),
                  help="Profit already locked in from sales, including stocks you no longer hold.")

        st.markdown("#### Portfolio Allocation")
        fig = px.pie(holdings, names="symbol", values="value")
        fig.update_traces(
            textinfo="label+percent",
            hovertemplate="%{label}<br>Value: %{value:,.2f}<br>%{percent}<extra></extra>",
        )
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=380)
        st.plotly_chart(fig, width="stretch")

        st.markdown("#### Stock Price Breakdown")
        table = holdings.assign(weight=holdings["value"] / current_value)[
            ["symbol", "quantity", "avg_cost", "price", "pnl", "pnl_pct",
             "realized_pnl", "invested", "value", "weight", "price_source"]
        ]
        gain_color = lambda v: f"color: {'#16a34a' if v > 0 else '#dc2626' if v < 0 else 'inherit'}"
        styled = (
            table.style
            .format({"quantity": "{:g}", "avg_cost": "{:,.2f}", "price": "{:,.2f}",
                     "pnl": "{:+,.2f}", "pnl_pct": "{:+.2%}", "realized_pnl": "{:+,.2f}", "invested": "{:,.2f}",
                     "value": "{:,.2f}", "weight": "{:.1%}"})
            .map(gain_color, subset=["pnl", "pnl_pct", "realized_pnl"])
        )
        st.dataframe(
            styled,
            hide_index=True,
            width="stretch",
            column_config={
                "symbol": "Ticker Symbol",
                "quantity": "Current Quantity",
                "avg_cost": "Average Cost Basis",
                "price": "Current Price",
                "pnl": "Profit & Gains",
                "pnl_pct": "Profit & Gains %",
                "realized_pnl": "Realized Profit",
                "invested": "Total Cost",
                "value": "Market Value",
                "weight": "Allocation",
                "price_source": "Price Source",
            },
        )
        if (holdings["price_source"] == "Last trade").any():
            st.caption("Some prices use the last transaction price because a live price "
                       "wasn't available. Check the symbol (e.g. add .NS for NSE stocks).")

# ----- Tab 3: Historical Performance -----
with tab3:
    st.subheader("Historical Performance")
    if tx.empty:
        st.info("No transactions yet. Add transactions in the Input Transactions tab.")
    else:
        perf = performance_summary(tx, current_value, date.today())
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Lifetime Investment", money(perf["total_invested"]),
                  help="Total cash spent on all BUY transactions.")
        c2.metric("Total Sales", money(perf["total_sales"]),
                  help="Total cash received from all SELL transactions.")
        c3.metric("Lifetime Proceeds", money(perf["lifetime_proceeds"]),
                  help="Total Sales + Current Portfolio Value: everything the "
                       "portfolio has returned to you or is still worth.")
        c4, c5, c6 = st.columns(3)
        c4.metric("Current Portfolio Value", money(perf["current_value"]))
        c5.metric("Total Return", money(perf["total_return"]),
                  delta=pct(perf["total_return_pct"]),
                  help="Lifetime Proceeds − Total Lifetime Investment.")
        c6.metric("XIRR", pct(perf["xirr"]),
                  help="Annualised return that accounts for the timing of every buy and sell.")

        st.markdown("#### Portfolio Value Over Time")
        symbols = tuple(sorted(tx["symbol"].unique()))
        history = prices.fetch_price_history(symbols, tx["date"].min()) if use_live else pd.DataFrame()
        trend = value_over_time(tx, history, date.today())
        fig = px.line(
            trend.melt(id_vars="date", value_vars=["value", "net_invested"],
                       var_name="series", value_name="amount")
            .replace({"series": {"value": "Portfolio value", "net_invested": "Net invested"}}),
            x="date", y="amount", color="series",
            color_discrete_map={"Portfolio value": "#2563eb", "Net invested": "#9ca3af"},
        )
        fig.update_traces(selector=dict(name="Net invested"), line=dict(dash="dash", shape="hv"))
        fig.update_layout(
            height=420, margin=dict(t=10, b=10, l=10, r=10), hovermode="x unified",
            xaxis_title=None, yaxis_title=None, legend_title_text=None,
            legend=dict(orientation="h", y=1.08, x=0),
        )
        fig.update_yaxes(tickformat=",.0f")
        st.plotly_chart(fig, width="stretch")
        missing = [s for s in symbols if s not in history.columns]
        if missing:
            st.caption("No market price history for " + ", ".join(missing) +
                       "; the chart uses their transaction prices instead.")
        st.caption("Portfolio value = shares held on each day × that day's closing price. "
                   "Net invested = cash put in through buys minus cash taken out through sales.")
