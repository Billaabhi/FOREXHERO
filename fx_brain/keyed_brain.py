from __future__ import annotations

import re

from agents import Agent, Runner, set_default_openai_key

from .decision import decide
from .models import MarketSnapshot, TradeDecision

SYSTEM = """You are FX BRAIN, an institutional-style Forex decision engine. Do not predict candles or guarantee profit. Assess whether current evidence supports an asymmetric, risk-controlled opportunity. Be skeptical. Never invent live prices, macro events, positioning, or news. Separate evidence from inference. If evidence is mixed, prefer WAIT. Return a score explicitly."""


def _agents() -> tuple[Agent, Agent]:
    macro = Agent(
        name="Macro Specialist",
        instructions=SYSTEM + " Act as the macro specialist. Return a directional macro score from -100 to +100. No supplied macro evidence means 0.",
    )
    adversarial = Agent(
        name="Adversarial Specialist",
        instructions=SYSTEM + " Try to destroy the trade. Return an adversarial risk score from 0 to 100. Flag contradictions, overextension, volatility, missing catalysts and weak invalidation.",
    )
    return macro, adversarial


async def analyze_with_key(snapshot: MarketSnapshot, openai_api_key: str) -> TradeDecision:
    if not openai_api_key or len(openai_api_key) < 20:
        raise RuntimeError("OpenAI API key is missing")
    set_default_openai_key(openai_api_key, use_for_tracing=True)
    macro_agent, adversarial_agent = _agents()
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
