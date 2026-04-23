from fastapi import APIRouter
from app.schemas.incident import IncidentStartRequest
from app.services.orchestrator import run_incident_flow
from app.core.ledger import read_incident_trace

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("/ping")
def incidents_ping():
    return {"status": "incidents ok"}


@router.post("/start")
def start_incident(request: IncidentStartRequest):
    return run_incident_flow(request)


@router.get("/{incident_id}/trace")
def get_incident_trace(incident_id: str):
    return {
        "incident_id": incident_id,
        "trace": read_incident_trace(incident_id)
    }