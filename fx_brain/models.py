from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class Decision(str, Enum):
    GO = "GO"
    NO_GO = "NO-GO"
    WAIT = "WAIT"


class Direction(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    FLAT = "FLAT"


class MarketSnapshot(BaseModel):
    pair: str
    timeframe: str = "1h"
    price: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    spread_pips: Optional[float] = None
    ema_fast: Optional[float] = None
    ema_slow: Optional[float] = None
    rsi: Optional[float] = None
    atr: Optional[float] = None
    adx: Optional[float] = None
    momentum: Optional[float] = None
    trend_score: float = Field(default=0, ge=-100, le=100)
    volatility_score: float = Field(default=0, ge=-100, le=100)
    notes: List[str] = Field(default_factory=list)


class ExpertView(BaseModel):
    name: str
    score: float = Field(ge=-100, le=100)
    thesis: str
    supports: List[str] = Field(default_factory=list)
    contradicts: List[str] = Field(default_factory=list)


class TradeDecision(BaseModel):
    pair: str
    decision: Decision
    direction: Direction
    confidence: float = Field(ge=0, le=1)
    entry: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    risk_reward: Optional[float] = None
    risk_percent: float = Field(default=0, ge=0, le=2)
    regime: str = "UNKNOWN"
    thesis: str
    invalidation: str
    catalyst: str
    adversarial_score: float = Field(ge=0, le=1)
    reasons: List[str] = Field(default_factory=list)
    vetoes: List[str] = Field(default_factory=list)
