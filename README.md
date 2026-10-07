# Stock Portfolio Analyzer

A Streamlit app that analyzes a stock portfolio from its transaction history.
Market prices come from yfinance.

## Run

```bash
uv sync                          # install dependencies into .venv
uv run streamlit run app.py      # start the app at http://localhost:8501
uv run pytest                    # run the tests (no internet needed)
```

## Tabs

1. **Input Transactions**: upload a CSV (see `sample_data.csv`) or add trades manually.
2. **Current Portfolio**: allocation pie chart and per-stock breakdown (quantity,
   average cost basis, current price, profit and gains, realized profit).
3. **Historical Performance**: lifetime investment, sales, proceeds, current value,
   total return, XIRR and a portfolio value trend line.

CSV columns: `ticker, date, transaction_type, quantity, price` (`transaction_type` is BUY or SELL).

## Structure

```
app.py               the three tabs (screen layout only)
portfolio/
  loader.py          read and check the CSV, save/load transactions
  holdings.py        replay trades -> positions, average cost, realized profit
  prices.py          yfinance calls, cached
  performance.py     lifetime metrics, XIRR, daily value series
tests/               tests for the math, no internet needed
```

Saved transactions live in `data/transactions.csv` (git-ignored).
