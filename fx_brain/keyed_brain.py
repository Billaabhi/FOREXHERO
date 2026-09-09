from __future__ import annotations

import os

from agents import Agent, Runner, set_default_openai_key

from .brain import run_brain
from .decision import decide
from .models import MarketSnapshot, TradeDecision


def _configure_openai() -> None:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not configured on the server")
    set_default_openai_key(key, use_for_tracing=False)


async def analyze_with_key(snapshot: MarketSnapshot) -> TradeDecision:
    _configure_openai()
    return await run_brain(snapshot)
