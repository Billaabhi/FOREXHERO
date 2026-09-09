from __future__ import annotations

import re

from agents import Agent, Runner

from .decision import decide
from .models import MarketSnapshot, TradeDecision

SYSTEM = """You are FX BRAIN, an institutional-style Forex decision engine. Do not predict candles or guarantee profit. Assess whether current evidence supports an asymmetric, risk-controlled opportunity. Be skeptical. Never invent live prices, macro events, positioning, or news. Separate evidence from inference. If evidence is mixed, prefer WAIT."""

macro_agent = Agent(
    name="Macro Specialist",
    instructions=SYSTEM + " Act as the macro specialist. Return a directional macro score from -100 to +100. If no macro evidence is supplied, return 0 and state that macro evidence is missing.",
)

adversarial_agent = Agent(
    name="Adversarial Specialist",
    instructions=SYSTEM + " Try to destroy the proposed trade. Return an adversarial risk score from 0 to 100. Flag overextension, contradictions, volatility, missing catalysts, and weak invalidation levels.",
)


async def analyze(snapshot: MarketSnapshot) -> TradeDecision:
    payload = snapshot.model_dump_json()
    macro = await Runner.run(macro_agent, f"Assess macro backdrop for {snapshot.pair}. Snapshot:\n{payload}")
    adversarial = await Runner.run(adversarial_agent, f"Try to destroy a trade on {snapshot.pair}. Snapshot:\n{payload}")
    macro_score = _score(str(macro.final_output), 0.0, -100, 100)
    adversarial_score = _score(str(adversarial.final_output), 25.0, 0, 100) / 100
    return decide(snapshot, adversarial_score=adversarial_score, macro_score=macro_score)


def _score(text: str, default: float, low: float, high: float) -> float:
    matches = re.findall(r"(?:score|rating)\s*[:=]\s*(-?\d+(?:\.\d+)?)", text, re.I)
    if not matches:
        return default
    return max(low, min(high, float(matches[-1])))
