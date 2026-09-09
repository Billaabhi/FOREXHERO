from __future__ import annotations

from agents import Agent, Runner

from .decision import decide
from .models import AdversarialReview, ExpertView, MarketSnapshot, TradeDecision

SYSTEM = """You are part of FX BRAIN, an institutional-style Forex decision engine. Never predict candles or guarantee profit. Never invent prices, macro events, positioning or news. Use only the supplied snapshot. Separate evidence from inference. If evidence is missing, say so. Be skeptical and prefer WAIT when evidence is mixed."""

macro_agent = Agent(
    name="Macro Council",
    instructions=SYSTEM + " Return a structured expert view. Think like a macro trader: central-bank divergence, rates, liquidity, policy expectations and asymmetric opportunity. The snapshot may not contain macro data; in that case score 0 and explicitly state macro evidence is missing.",
    output_type=ExpertView,
)

adversarial_agent = Agent(
    name="Adversarial Judge",
    instructions=SYSTEM + " Try to destroy the proposed trade. Return a risk score from 0 to 100. Identify the strongest counterargument, concrete failure conditions, contradictions, overextension and missing catalysts. A high score means the trade is fragile.",
    output_type=AdversarialReview,
)


def _quant_experts(snapshot: MarketSnapshot) -> list[ExpertView]:
    trend = snapshot.trend_score
    momentum = snapshot.momentum or 0
    vol = snapshot.volatility_score
    direction_score = max(-100, min(100, 0.55 * trend + 0.45 * momentum))
    return [
        ExpertView(name="Tudor Jones — Trend / Asymmetry", score=direction_score, thesis="Follow confirmed directional movement and demand asymmetric payoff.", supports=[f"Trend score {trend:.1f}"], contradicts=["No structural trend confirmation"] if abs(trend) < 40 else []),
        ExpertView(name="Seykota — Systematic Momentum", score=momentum, thesis="Stay with persistent momentum and avoid forecasting reversals.", supports=[f"Momentum {momentum:.1f}"], contradicts=["Momentum is weak"] if abs(momentum) < 20 else []),
        ExpertView(name="Turtle — Breakout / Volatility", score=direction_score * 0.9, thesis="Prefer clean expansion and volatility-adjusted risk.", supports=["ATR available"] if snapshot.atr else [], contradicts=["ATR unavailable"] if snapshot.atr is None else []),
        ExpertView(name="Raschke — Market Structure", score=trend * 0.8, thesis="Assess continuation versus failed move using price structure.", supports=["Trend structure measured from the price series"], contradicts=[]),
        ExpertView(name="Wilder — Trend / RSI / ATR", score=trend * 0.6, thesis="Use trend strength, momentum and ATR to contextualize the setup.", supports=[f"ADX {snapshot.adx:.1f}"] if snapshot.adx is not None else [], contradicts=[]),
        ExpertView(name="Bollinger — Volatility Regime", score=0 if vol < 0 else min(100, vol), thesis="Volatility should be neither dead nor disorderly for a clean setup.", supports=[f"Volatility score {vol:.1f}"], contradicts=["Extreme volatility"] if vol >= 60 else []),
        ExpertView(name="Douglas — Execution Discipline", score=100 if abs(direction_score) >= 30 else 0, thesis="Process quality matters more than prediction; no trade is valid without a defined invalidation.", supports=["Deterministic risk gate present"], contradicts=[]),
    ]


async def run_brain(snapshot: MarketSnapshot) -> TradeDecision:
    payload = snapshot.model_dump_json()
    macro_result = await Runner.run(macro_agent, f"Assess the macro framework for {snapshot.pair}. Snapshot:\n{payload}")
    macro_view = macro_result.final_output

    quant_views = _quant_experts(snapshot)
    direction_hint = max(quant_views, key=lambda x: abs(x.score)).thesis
    adversarial_result = await Runner.run(
        adversarial_agent,
        f"Proposed setup for {snapshot.pair}: {direction_hint}. Snapshot:\n{payload}\nExpert views:\n{[v.model_dump() for v in quant_views]}\nMacro view:\n{macro_view.model_dump()}",
    )
    review = adversarial_result.final_output
    return decide(
        snapshot,
        adversarial_score=review.risk_score / 100,
        macro_score=macro_view.score,
        expert_views=[macro_view, *quant_views],
        adversarial_review=review,
    )


async def analyze(snapshot: MarketSnapshot) -> TradeDecision:
    return await run_brain(snapshot)
