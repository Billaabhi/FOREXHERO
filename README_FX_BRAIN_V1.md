# FX BRAIN V1

Research-first Forex decision engine built on the existing FOREXHERO foundation.

## Tonight's usable milestone

`market data -> technical evidence -> macro specialist -> adversarial specialist -> deterministic risk gate -> GO / NO-GO / WAIT`

V1 deliberately **does not place live orders**.

### Supported pairs

EUR/USD, GBP/USD, USD/JPY, AUD/USD, USD/CAD, USD/CHF, NZD/USD.

### Decision contract

- `GO` — directional setup passes the hard gates.
- `NO-GO` — directional idea exists but a risk/evidence veto blocks it.
- `WAIT` — evidence is not sufficiently directional.

Hard gates currently include confidence >= 70%, R:R >= 1.8, spread protection, extreme-volatility protection, and adversarial-risk protection.

## Architecture

- `fx_brain/data.py` — Twelve Data candle ingestion.
- `fx_brain/indicators.py` — EMA, RSI, ATR, ADX, momentum and trend/volatility scoring.
- `fx_brain/brain.py` — OpenAI Agents SDK specialist orchestration.
- `fx_brain/decision.py` — deterministic technical vote and hard risk gate.
- `fx_brain/models.py` — Pydantic market and trade contracts.
- `main.py` — FastAPI `/health` and `/analyze` endpoints.
- `tests/test_decision.py` — deterministic smoke tests.

The LLM synthesizes evidence; it does **not** own arithmetic, risk limits, or order permissions.

## Run

```bash
uv run python main.py
```

Then call:

```bash
curl -X POST http://localhost:8000/analyze \
  -H 'content-type: application/json' \
  -d '{"pair":"EUR/USD","timeframe":"1h"}'
```

Required environment variables:

```text
OPENAI_API_KEY
TWELVE_DATA_API_KEY
```

## Safety boundary

No broker credentials, no live order endpoint, and no autonomous execution in V1. Real-money execution is a later stage after backtesting and paper-trading validation.

## Next slices

1. Economic-calendar/news adapter with event lockout.
2. Currency-strength matrix across the core seven currencies.
3. Historical backtest + walk-forward evaluation.
4. Trade ledger and outcome learning loop.
5. Existing TradingView dashboard integration.
