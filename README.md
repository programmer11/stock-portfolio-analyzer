# Stock Portfolio Analyzer

A Streamlit app that analyzes a stock portfolio from its transaction history.
Market prices come from yfinance.

📖 **Documentation:** https://programmer11.github.io/stock-portfolio-analyzer/
(see also the [architecture diagram](https://programmer11.github.io/stock-portfolio-analyzer/architecture.html))

## Run

```bash
uv sync                          # install dependencies into .venv
uv run streamlit run app.py      # start the app at http://localhost:8501
uv run pytest                    # run the tests (no internet needed)
```

## Video demo

Watch the [American-voice walkthrough](demo/stock-portfolio-american.mp4) (1 minute 45 seconds),
or open the [video player with chapters](demo/american-demo.html).
The demo uses sample transactions and last-trade prices with live pricing off.

The editable [Remotion project](remotion-demo/README.md) includes the selected narration
and saved voice alternatives. Previewing or regenerating the video needs Node.js 20+;
the Python helper scripts in `demo/` and `remotion-demo/` need the optional `demo` dependencies:

```bash
uv sync --group demo                 # Pillow, Playwright, imageio-ffmpeg
uv run playwright install chromium   # only for demo/capture.py
```

```bash
cd remotion-demo
npm ci
npm run dev -- --no-open
npx remotion render src/index.ts StockPortfolioDemo ../demo/stock-portfolio-american.mp4
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
docs/                documentation site (GitHub Pages)
```

Saved transactions live in `data/transactions.csv` (git-ignored).
