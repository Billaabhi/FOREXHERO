from .models import Decision, Direction, MarketSnapshot, TradeDecision

MIN_CONFIDENCE = 0.70
MIN_RR = 1.8
MAX_RISK = 0.75


def technical_vote(snapshot: MarketSnapshot) -> tuple[Direction, float]:
    score = 0.0
    if snapshot.ema_fast is not None and snapshot.ema_slow is not None:
        score += 30 if snapshot.ema_fast > snapshot.ema_slow else -30
    score += max(-25, min(25, snapshot.trend_score * 0.25))
    score += max(-20, min(20, (snapshot.momentum or 0) * 0.20))
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


def hard_risk_gate(snapshot: MarketSnapshot, confidence: float, risk_reward: float | None, adversarial_score: float) -> list[str]:
    vetoes: list[str] = []
    if risk_reward is not None and risk_reward < MIN_RR:
        vetoes.append("Risk/reward below 1.8")
    if snapshot.spread_pips is not None and snapshot.spread_pips > 3.0:
        vetoes.append("Spread too wide")
    if snapshot.atr is not None and snapshot.price > 0 and snapshot.atr / snapshot.price > 0.01:
        vetoes.append("Extreme short-term volatility")
    if confidence < MIN_CONFIDENCE:
        vetoes.append("Confidence below 70% threshold")
    if adversarial_score >= 0.70:
        vetoes.append("Adversarial risk too high")
    return vetoes


def decide(snapshot: MarketSnapshot, adversarial_score: float = 0.0, macro_score: float = 0.0) -> TradeDecision:
    direction, raw = technical_vote(snapshot)
    confidence = min(0.99, max(0.01, 0.50 + abs(raw) / 100 * 0.45 + macro_score / 500))
    if adversarial_score >= 0.50:
        confidence *= 0.85

    risk_reward = 2.0 if direction != Direction.FLAT else None
    vetoes = hard_risk_gate(snapshot, confidence, risk_reward, adversarial_score)
    decision = Decision.WAIT if direction == Direction.FLAT else (Decision.NO_GO if vetoes else Decision.GO)

    return TradeDecision(
        pair=snapshot.pair,
        decision=decision,
        direction=direction,
        confidence=confidence,
        entry=snapshot.price if decision == Decision.GO else None,
        stop_loss=(snapshot.price - 1.5 * snapshot.atr if direction == Direction.LONG and snapshot.atr else snapshot.price + 1.5 * snapshot.atr if direction == Direction.SHORT and snapshot.atr else None),
        take_profit=(snapshot.price + 3.0 * snapshot.atr if direction == Direction.LONG and snapshot.atr else snapshot.price - 3.0 * snapshot.atr if direction == Direction.SHORT and snapshot.atr else None),
        risk_reward=risk_reward,
        risk_percent=MAX_RISK if decision == Decision.GO else 0,
        regime="TRENDING" if abs(snapshot.trend_score) >= 40 else "RANGE/UNCLEAR",
        thesis="Technical and macro evidence support the selected direction." if direction != Direction.FLAT else "Evidence is not sufficiently directional.",
        invalidation="Reversal through the structural setup or material new macro information.",
        catalyst="Price/momentum confirmation and macro alignment.",
        adversarial_score=adversarial_score,
        reasons=[f"Technical score: {raw:.1f}", f"Macro score: {macro_score:.1f}"],
        vetoes=vetoes,
    )
