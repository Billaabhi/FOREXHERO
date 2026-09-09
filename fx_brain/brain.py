from __future__ import annotations

import json
import os
from typing import Any

from agents import Agent, Runner

from .decision import decide
from .models import MarketSnapshot, TradeDecision


SYSTEM = """You are FX BRAIN, an institutional-style Forex decision engine.\n\nYour job is NOT to predict candles or guarantee profit. Assess whether the current evidence supports an asymmetric, risk-controlled opportunity. Be skeptical. Separate evidence from inference. Never invent live prices, macro events, positioning, or news.\n\nYou are given a structured market snapshot. Produce concise reasoning that can be used by a deterministic risk gate. Focus on regime, trend, momentum, volatility, contradictions, catalyst, and invalidation. If evidence is mixed, prefer WAIT.\n"""

macro_agent = Agent(
    name="Macro Specialist",
    instructions=SYSTEM + "\nAct as the macro specialist. Score the directional macro backdrop from -100 to +100. Do not invent economic releases; if no macro evidence is supplied, score 0 and say that macro evidence is missing.",
)

adversarial_agent = Agent(
    name="Adversarial Specialist",
    instructions=SYSTEM + "\nAct as the trade destroyer. Look for overextension, weak evidence, volatility risk, contradictory signals, poor R:R, and missing catalysts. Return an adversarial risk score from 0 to 1, where 1 means kill the trade.",
)

judge_agent = Agent(
    name="FX Brain Judge",
    instructions=SYSTEM + "\nYou are the final judge. You may summarize the evidence, but the deterministic hard risk gate in Python has final authority over GO/NO-GO/WAIT. Never override a veto.",
)


async def analyze(snapshot: MarketSnapshot) -> TradeDecision:
    payload = snapshot.model_dump_json()
    macro = await Runner.run(macro_agent, f"Assess macro backdrop for {snapshot.pair}. Snapshot:\n{payload}")
    macro_text = str(macro.final_output)
    adversarial = await Runner.run(adversarial_agent, f"Try to destroy a {snapshot.pair} trade using this snapshot:\n{payload}")
    adversarial_text = str(adversarial.final_output)

    macro_score = _extract_score(macro_text, default=0.0)
    adversarial_score = _extract_score(adversarial_text, default=0.25, scale_100=True)
    return decide(snapshot, adversarial_score=adversarial_score, macro_score=macro_score)


def _extract_score(text: str, default: float, scale_100: bool = False) -> float:
    import re
    matches = re.findall(r"(?:score|rating)\s*[:=]\s*(-?\d+(?:\.\d+)?)", text, re.I)
    if not matches:
        return default
    value = float(matches[-1])
    if scale_100:
        return max(0.0, min(1.0, abs(value) / 100))
    return max(-100.0, min(100.0, value))


def analyze_sync(snapshot: MarketSnapshot) -> TradeDecision:
    return __import__("asyncio").run(analyze(snapshot))
