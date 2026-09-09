from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from fx_brain.brain import analyze
from fx_brain.data import build_snapshot

app = FastAPI(title="FX BRAIN V1", version="0.1.0")


class AnalyzeRequest(BaseModel):
    pair: str = "EUR/USD"
    timeframe: str = "1h"


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "engine": "FX BRAIN V1"}


@app.post("/analyze")
async def analyze_pair(request: AnalyzeRequest) -> dict:
    try:
        snapshot = build_snapshot(request.pair, request.timeframe)
        decision = await analyze(snapshot)
        return {"snapshot": snapshot.model_dump(), "decision": decision.model_dump(mode="json")}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


def main() -> None:
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8000")), reload=False)


if __name__ == "__main__":
    main()
