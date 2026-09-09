from __future__ import annotations

import requests

from .data import PAIR_MAP
from .indicators import score_market
from .models import MarketSnapshot


def build_snapshot_with_key(pair: str, interval: str, api_key: str) -> MarketSnapshot:
    symbol = PAIR_MAP.get(pair, pair)
    response = requests.get(
        "https://api.twelvedata.com/time_series",
        params={
            "symbol": symbol,
            "interval": interval,
            "outputsize": 200,
            "apikey": api_key,
            "format": "JSON",
        },
        timeout=15,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("status") == "error":
        raise RuntimeError(payload.get("message", "Twelve Data error"))
    values = list(reversed(payload.get("values", [])))
    if len(values) < 60:
        raise RuntimeError(f"Insufficient candles: {len(values)}")
    closes = [float(x["close"]) for x in values]
    highs = [float(x["high"]) for x in values]
    lows = [float(x["low"]) for x in values]
    stats = score_market(closes, highs, lows)
    return MarketSnapshot(pair=pair, timeframe=interval, price=closes[-1], **stats)
