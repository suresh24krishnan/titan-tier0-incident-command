from fastapi import APIRouter
from app.schemas.a2a import A2ARequest
from app.schemas.ledger import LedgerEvent
from app.core.router import route_a2a_request
from app.core.ledger import write_ledger_event
from app.utils.timestamps import utc_now_iso
from app.utils.ids import generate_correlation_id

router = APIRouter(prefix="/gateway", tags=["Gateway"])


@router.get("/ping")
def gateway_ping():
    return {"status": "gateway ok"}


@router.post("/route")
def route_request(request: A2ARequest):
    if not request.correlation_id:
        request.correlation_id = generate_correlation_id()

    write_ledger_event(
        LedgerEvent(
            correlation_id=request.correlation_id,
            incident_id=request.incident_id,
            sender_agent=request.sender_agent,
            target_capability=request.target_capability,
            task=request.task,
            timestamp=utc_now_iso(),
            status="received",
            details={"payload_classification": request.payload_classification},
        )
    )

    response = route_a2a_request(request)

    write_ledger_event(
        LedgerEvent(
            correlation_id=response.correlation_id,
            incident_id=response.incident_id,
            sender_agent=response.responder_agent,
            target_capability=response.capability,
            task=response.task,
            timestamp=utc_now_iso(),
            status=response.status,
            details=response.result,
        )
    )

    return response