from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException

from a2a_runtime.shared.schemas import IncidentStartRequest
from a2a_runtime.titan_gateway.orchestrator import run_incident_flow

app = FastAPI(title="TITAN Gateway V2")

LEDGER_PATH = Path("data/ledger.jsonl")


def read_trace_for_incident(incident_id: str) -> list[dict]:
    if not LEDGER_PATH.exists():
        return []

    events: list[dict] = []

    with LEDGER_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if not raw:
                continue

            try:
                event = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if event.get("incident_id") == incident_id:
                events.append(event)

    events.sort(key=lambda x: x.get("timestamp", ""))
    return events


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "titan-gateway-v2",
    }


@app.post("/incidents/start")
def start_incident(request: IncidentStartRequest) -> dict:
    try:
        return run_incident_flow(request.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/incidents/{incident_id}/trace")
def incident_trace(incident_id: str) -> dict:
    try:
        trace = read_trace_for_incident(incident_id)
        return {
            "incident_id": incident_id,
            "trace_available": True,
            "trace": trace,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc