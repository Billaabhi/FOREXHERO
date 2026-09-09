from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from fx_brain.keyed_brain import analyze_with_key
from fx_brain.keyed_data import build_snapshot_with_key

app = FastAPI(title="FX BRAIN", version="0.3.0")


class KeyedAnalyzeRequest(BaseModel):
    pair: str = "EUR/USD"
    timeframe: str = "1h"
    twelve_data_api_key: str = Field(min_length=8)
    finnhub_api_key: str | None = None


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "engine": "FX BRAIN", "version": "0.3.0"}


@app.get("/fx-brain")
def fx_brain_console():
    return FileResponse(Path(__file__).with_name("fx-brain-console.html"))


@app.post("/analyze-with-keys")
async def analyze_with_keys(request: KeyedAnalyzeRequest) -> dict:
    try:
        snapshot = build_snapshot_with_key(request.pair, request.timeframe, request.twelve_data_api_key)
        # Finnhub is accepted now so the UI contract is stable; its event/news adapter
        # will be connected to the macro/catalyst layer in the next data iteration.
        decision = await analyze_with_key(snapshot)
        return {"snapshot": snapshot.model_dump(), "decision": decision.model_dump(mode="json")}
    except Exception as exc:
        raise HTTPException(status_code=502, detail="FX Brain analysis failed: " + str(exc)) from exc


def main() -> None:
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8000")), reload=False)


if __name__ == "__main__":
    main()
