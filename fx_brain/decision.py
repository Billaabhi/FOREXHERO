from .models import Decision, Direction, MarketSnapshot, TradeDecision


def technical_vote(snapshot: MarketSnapshot) -> tuple[Direction, float]:
    score = 0.0
    if snapshot.ema_fast is not None and snapshot.ema_slow is not None:
        score += 30 if snapshot.ema_fast > snapshot.ema_slow else -30
    score += max(-25, min(25, snapshot.trend_score * 0.25))
    score += max(-20, min(20, snapshot.momentum * 0.20 if snapshot.momentum is not None else 0))
    if snapshot.rsi is not None:
        if snapshot.rsi > 70:
            score -= 10
        elif snapshot.rsi < 30:
            score += 10
    if score > 15:
        return Direction.LONG, score
    if score < -15:
        return Direction.SHORT, score
    return Direction.FLAT, score


def hard_risk_gate(snapshot: MarketSnapshot, confidence: float, risk_reward: float | None) -> list[str]:
    vetoes: list[str] = []
    if risk_reward is not None and risk_reward < 1.8:
        vetoes.append("Risk/reward below 1.8")
    if snapshot.spread_pips is not None and snapshot.spread_pips > 3.0:
        vetoes.append("Spread too wide")
    if snapshot.atr is not None and snapshot.price > 0 and snapshot.atr / snapshot.price > 0.01:
        vetoes.append("Extreme short-term volatility")
    if confidence < 0.70:
        vetoes.append("Confidence below 70% threshold")
    return vetoes


def decide(snapshot: MarketSnapshot, adversarial_score: float = 0.0) -> TradeDecision:
    direction, raw = technical_vote(snapshot)
    confidence = min(0.99, max(0.01, 0.50 + abs(raw) / 100 * 0.45))
    if adversarial_score >= 0.50:
        confidence *= 0.85

    risk_reward = 2.0 if direction != Direction.FLAT else None
    vetoes = hard_risk_gate(snapshot, confidence, risk_reward)

    if direction == Direction.FLAT:
        decision = Decision.WAIT
    elif vetoes:
        decision = Decision.NO_GO
    else:
        decision = Decision.GO

    return TradeDecision(
        pair=snapshot.pair,
        decision=decision,
        direction=direction,
        confidence=confidence,
        entry=snapshot.price if decision == Decision.GO else None,
        risk_reward=risk_reward,
        risk_percent=0.75 if decision == Decision.GO else 0,
        regime="TRENDING" if abs(snapshot.trend_score) >= 40 else "RANGE/UNCLEAR",
        thesis="Technical evidence is aligned with the selected direction." if direction != Direction.FLAT else "Evidence is not sufficiently directional.",
        invalidation="Reversal through the structural setup or material new macro information.",
        catalyst="Price/momentum confirmation.",
        adversarial_score=adversarial_score,
        reasons=[f"Technical score: {raw:.1f}"],
        vetoes=vetoes,
    )
