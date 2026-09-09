from fx_brain.decision import decide
from fx_brain.models import Direction, MarketSnapshot


def test_unclear_market_waits():
    snapshot = MarketSnapshot(pair="EUR/USD", price=1.17)
    result = decide(snapshot)
    assert result.direction == Direction.FLAT
    assert result.decision.value == "WAIT"


def test_strong_trend_can_go():
    snapshot = MarketSnapshot(
        pair="EUR/USD", price=1.17, ema_fast=1.171, ema_slow=1.168,
        momentum=0.8, trend_score=80, volatility_score=10, atr=0.002,
    )
    result = decide(snapshot)
    assert result.decision.value == "GO"
    assert result.risk_reward >= 1.8
