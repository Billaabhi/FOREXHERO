from __future__ import annotations

from math import sqrt
from statistics import mean


def sma(values: list[float], period: int) -> float | None:
    if len(values) < period:
        return None
    return mean(values[-period:])


def ema(values: list[float], period: int) -> float | None:
    if len(values) < period:
        return None
    k = 2 / (period + 1)
    value = mean(values[:period])
    for price in values[period:]:
        value = price * k + value * (1 - k)
    return value


def rsi(values: list[float], period: int = 14) -> float | None:
    if len(values) <= period:
        return None
    gains: list[float] = []
    losses: list[float] = []
    for a, b in zip(values[-period - 1:-1], values[-period:]):
        change = b - a
        gains.append(max(change, 0))
        losses.append(max(-change, 0))
    avg_gain = mean(gains)
    avg_loss = mean(losses)
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def atr(highs: list[float], lows: list[float], closes: list[float], period: int = 14) -> float | None:
    if len(closes) <= period:
        return None
    trs: list[float] = []
    for i in range(1, len(closes)):
        trs.append(max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1])))
    return mean(trs[-period:])


def adx(highs: list[float], lows: list[float], closes: list[float], period: int = 14) -> float | None:
    if len(closes) < period * 2 + 1:
        return None
    plus_dm, minus_dm, tr = [], [], []
    for i in range(1, len(closes)):
        up = highs[i] - highs[i - 1]
        down = lows[i - 1] - lows[i]
        plus_dm.append(up if up > down and up > 0 else 0)
        minus_dm.append(down if down > up and down > 0 else 0)
        tr.append(max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1])))
    dx: list[float] = []
    for i in range(period, len(tr)):
        atr_v = mean(tr[i - period:i])
        if atr_v == 0:
            continue
        pdi = 100 * mean(plus_dm[i - period:i]) / atr_v
        mdi = 100 * mean(minus_dm[i - period:i]) / atr_v
        denom = pdi + mdi
        dx.append(100 * abs(pdi - mdi) / denom if denom else 0)
    return mean(dx[-period:]) if len(dx) >= period else None


def zscore(values: list[float], period: int = 20) -> float | None:
    if len(values) < period:
        return None
    window = values[-period:]
    mu = mean(window)
    variance = mean((x - mu) ** 2 for x in window)
    sd = sqrt(variance)
    return 0.0 if sd == 0 else (window[-1] - mu) / sd


def score_market(closes: list[float], highs: list[float], lows: list[float]) -> dict:
    fast = ema(closes, 20)
    slow = ema(closes, 50)
    rsi_v = rsi(closes)
    atr_v = atr(highs, lows, closes)
    adx_v = adx(highs, lows, closes)
    momentum = ((closes[-1] / closes[-11]) - 1) * 100 if len(closes) >= 11 else 0.0

    trend_score = 0.0
    if fast and slow:
        trend_score += 45 if fast > slow else -45
    if len(closes) >= 6:
        trend_score += 25 if closes[-1] > closes[-6] else -25
    if adx_v is not None:
        trend_score += min(30, max(0, adx_v - 20)) * (1 if trend_score >= 0 else -1)
    trend_score = max(-100, min(100, trend_score))

    volatility_score = 0.0
    if atr_v and closes[-1]:
        atr_pct = atr_v / closes[-1] * 100
        volatility_score = max(-100, min(100, (atr_pct - 0.25) * 120))

    return {
        "ema_fast": fast,
        "ema_slow": slow,
        "rsi": rsi_v,
        "atr": atr_v,
        "adx": adx_v,
        "momentum": momentum,
        "trend_score": trend_score,
        "volatility_score": volatility_score,
    }
