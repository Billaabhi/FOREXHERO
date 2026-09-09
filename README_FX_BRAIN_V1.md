# FX Brain V1

Research-first Forex decision engine. V1 deliberately does **not** place live orders.

## Contract

The engine has exactly three decisions:

- `GO` — setup passes the current gates.
- `NO-GO` — setup is rejected by evidence or a hard risk veto.
- `WAIT` — directional evidence is insufficient.

## Initial universe

EUR/USD, GBP/USD, USD/JPY, AUD/USD, USD/CAD, USD/CHF, NZD/USD.

## Architecture

`market data -> feature engine -> strategy/expert views -> adversarial review -> deterministic risk gate -> decision -> trade ledger -> backtest/evaluation`

The LLM is an evidence synthesizer, not the source of truth for arithmetic, indicators, risk limits, or order permissions. Those remain deterministic code paths.

## V1 safety boundary

No broker credentials. No live order endpoint. No autonomous execution.

## Next build slices

1. Historical OHLC loader + canonical market schema.
2. Technical feature engine: EMA, RSI, ATR, ADX, momentum, regime.
3. Strategy modules: trend, momentum, breakout, mean reversion, carry placeholder.
4. Macro/news adapter interfaces.
5. OpenAI specialist agents with structured outputs.
6. Adversarial agent + decision judge.
7. Backtest engine with walk-forward evaluation and transaction-cost assumptions.
8. Dashboard integration with the existing TradingView frontend.
