from __future__ import annotations

import os
import requests

from .models import MarketSnapshot
from .indicators import score_market


PAIR_MAP = {
    "EUR/USD": "EUR/USD", "GBP/USD": "GBP/USD", "USD/JPY": "USD/JPY",
    "AUD/USD": "AUD/USD", "USD/CAD": "USD/CAD", "USD/CHF": "USD/CHF",
    "NZD/USD": "NZD/USD", "EUR/GBP": "EUR/GBP", "EUR/JPY": "EUR/JPY",
    "GBP/JPY": "GBP/JPY", "XAU/USD": "XAU/USD",
}


def fetch_candles(pair: str, interval: str = "1h", outputsize: int = 200) -> list[dict]:
    key = os.environ.get("TWELVE_DATA_API_KEY")
    if not key:
        raise RuntimeError("TWELVE_DATA_API_KEY is not configured")
    symbol = PAIR_MAP.get(pair, pair)
    response = requests.get(
        "https://api.twelvedata.com/time_series",
        params={"symbol": symbol, "interval": interval, "outputsize": outputsize, "apikey": key, "format": "JSON"},
        timeout=15,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("status") == "error":
        raise RuntimeError(payload.get("message", "Twelve Data error"))
    values = list(reversed(payload.get("values", [])))
    if len(values) < 60:
        raise RuntimeError(f"Insufficient candles: {len(values)}")
    return values


def build_snapshot(pair: str, interval: str = "1h") -> MarketSnapshot:
    candles = fetch_candles(pair, interval)
    closes = [float(x["close"]) for x in candles]
    highs = [float(x["high"]) for x in candles]
    lows = [float(x["low"]) for x in candles]
    stats = score_market(closes, highs, lows)
    return MarketSnapshot(pair=pair, timeframe=interval, price=closes[-1], **stats)
