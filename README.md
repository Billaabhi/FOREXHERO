# Forex Intelligence Constitution — Deployment

A static HTML frontend + one tiny serverless function (`api/claude.js`) that proxies
calls to Claude so your Anthropic API key never reaches the browser.

This package was rebuilt from the full current feature set: TradingView chart,
weighted Trade Plan (ICT/SMC 40%, Price Action 20%, Regime 5%, confirmation 35%),
Hougaard-strictness + Douglas psychology gating on The Last Word, intraday data
via Twelve Data (any pair, 1H candles, with real FVG/swing detection feeding ICT),
economic calendar via Finnhub, intermarket data (DXY/Gold), Daily Risk Budget
tracker, Pre-Trade Checklist, and the trade ledger.

## What's in this folder

```
index.html        the app
api/claude.js      proxy: forwards POST /api/claude -> api.anthropic.com, server-side key
package.json       minimal, lets Vercel recognize the project
```

## Deploy steps (new Vercel project)

1. **Create a GitHub repo** (e.g. `forex-constitution`) and push everything in this
   folder to it:
   ```bash
   git init
   git add .
   git commit -m "Deploy: full feature set"
   git branch -M main
   git remote add origin https://github.com/<your-username>/forex-constitution.git
   git push -u origin main
   ```

2. **Get an Anthropic API key** at console.anthropic.com → API Keys, if you don't
   already have one for this purpose. Calls from the live site bill to this key
   directly — there's no Claude.ai usage pooling once it's deployed.

3. **In Vercel**: "Add New… → Project" → import the GitHub repo you just pushed.
   - Framework preset: leave as "Other" (auto-detected is fine).
   - Before clicking Deploy, open **Environment Variables** and add:
     - `ANTHROPIC_API_KEY` = `<your key from step 2>`
   - Click **Deploy**.

4. Once it finishes, Vercel gives you a `*.vercel.app` URL — that's the live app.
   Open it, paste your Twelve Data and Finnhub keys in the header (same as in
   chat — these stay in-session only, never saved), select a pair, hit
   **Fetch Live Data**, then **Run Full Analysis** to confirm the proxy and the
   external feeds are all wired up correctly.

## What to verify after deploying (in this order)

1. **Run Full Analysis works at all** — confirms the `/api/claude` proxy and
   `ANTHROPIC_API_KEY` are correctly wired. If specialist cards show ERROR
   badges, check the Vercel function logs for the actual error.
2. **The market data status line** (under the header, after Fetch Live Data) —
   tells you immediately whether the Twelve Data and Finnhub keys actually
   work against their real free tiers. These two were never tested against
   live endpoints from the build environment — your browser is the first real
   test. If either fails, it'll show the actual HTTP error now (this was
   fixed to surface real errors instead of generic guesses).
3. **Trade ledger persists across a refresh** — confirms `localStorage` is
   working as expected (it's per-browser, per-device, not synced anywhere).

## Notes

- **Trade ledger** is stored in `localStorage` — it lives in that one browser, on
  that one device. Clearing browser data clears it.
- **No login** is set up — anyone with the URL can use it and it'll bill your
  `ANTHROPIC_API_KEY`. Reasonable for personal use since the URL won't be
  shared publicly; say the word if you want a lightweight password gate added.
- To redeploy after future edits: just push to the `main` branch — Vercel
  auto-deploys on push once the GitHub integration is connected.
