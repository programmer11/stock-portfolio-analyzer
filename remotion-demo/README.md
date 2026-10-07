# Stock Portfolio Analyzer — Remotion demo

Selected version: the American voice demo, with Samantha at 175 words per minute.
Eight narrated scenes, 1920 × 1080, 30 fps, approximately 105 seconds.
Uses real app captures with animated highlights. Each scene has its own Studio timeline.
The sample uses last transaction prices with live pricing off.
The manual-entry scene demonstrates preparing a trade, not saving it.

```sh
npm ci
npm run dev -- --no-open
npm run lint
```

Open `StockPortfolioDemo` for the selected demo. The original comparison link
`StockPortfolioDemoAmericanBackup` remains available with the same content.
Audio is in `public/audio/american`. Edit `voiceover.json`, then run
`uv run python generate_voiceover.py` on macOS (it uses the built-in `say` command;
run `uv sync --group demo` in the parent folder first) to regenerate it and update timing.

Other narration variants are preserved in `public/audio/teacher` and
`public/audio/female-upbeat`, with script and timing snapshots in `backups`.
The upbeat version's scene sources are saved in `backups/female-upbeat/src`.
All voices are locally synthesized.

To export:

```sh
npx remotion render src/index.ts StockPortfolioDemo ../demo/stock-portfolio-american.mp4
```

The selected export is linked from the main project README. Open
`../demo/american-demo.html` to watch it with chapter navigation.

On macOS versions older than 15, the bundled Remotion encoder may not work.
Render an image sequence and assemble it with the parent app's FFmpeg instead:

```sh
npx remotion render src/index.ts StockPortfolioDemo out/american-frames --sequence --image-format=jpeg --muted --browser-executable="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --concurrency=4
uv run python encode_frames.py
```

The fallback exports the full Remotion animation at 30 fps and pads each narration
track to its scene duration, keeping the selected American voice synchronized.
