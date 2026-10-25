"""
FastAPI app — Birthday Paradox Monte Carlo demo.

Endpoints:
  GET  /              HTML UI (templates/index.html)
  POST /api/sample    One random group + match check (JSON)
  GET  /stream/monte-carlo?n=23   SSE progress for 100,000 trials

Run: uvicorn main:app --reload --port 3006
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

_DEMO_ROOT = Path(__file__).resolve().parent.parent
if str(_DEMO_ROOT) not in sys.path:
    sys.path.insert(0, str(_DEMO_ROOT))

from birthday_core import (  # noqa: E402
    MAX_GROUP_SIZE,
    MIN_GROUP_SIZE,
    SIMULATION_COUNT,
    monte_carlo_stream,
    run_sample,
    validate_group_size,
)

app = FastAPI(title="Birthday Paradox Simulation")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")


class SampleRequest(BaseModel):
    """Body for POST /api/sample — how many people in the room."""

    num_bdays: int = Field(..., ge=MIN_GROUP_SIZE, le=MAX_GROUP_SIZE)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "min_group": MIN_GROUP_SIZE,
            "max_group": MAX_GROUP_SIZE,
            "simulation_count": SIMULATION_COUNT,
        },
    )


@app.post("/api/sample")
async def api_sample(body: SampleRequest) -> JSONResponse:
    """Generate one set of birthdays and report whether any two match."""
    try:
        return JSONResponse(run_sample(body.num_bdays))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/stream/monte-carlo")
async def stream_monte_carlo(
    n: int = Query(..., ge=MIN_GROUP_SIZE, le=MAX_GROUP_SIZE),
) -> StreamingResponse:
    """
    Server-Sent Events while running SIMULATION_COUNT trials.

    Events: {"type":"progress","completed":N} then {"type":"done", ...}.
    Runs synchronously inside the generator (same as the book loop; may take several seconds).
    """

    def events():
        try:
            validate_group_size(n)
        except ValueError as exc:
            payload = json.dumps({"type": "error", "message": str(exc)})
            yield f"data: {payload}\n\n"
            return
        for message in monte_carlo_stream(n):
            yield f"data: {json.dumps(message)}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")
