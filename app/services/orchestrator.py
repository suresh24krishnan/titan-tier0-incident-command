from app.schemas.a2a import A2ARequest, A2AResponse
from app.schemas.incident import IncidentStartRequest
from app.schemas.ledger import LedgerEvent
from app.agents.detection_agent import handle_detection
from app.core.router import route_a2a_request
from app.core.ledger import write_ledger_event
from app.utils.ids import generate_correlation_id
from app.utils.timestamps import utc_now_iso


def log_step_received(request: A2ARequest) -> None:
    write_ledger_event(
        LedgerEvent(
            correlation_id=request.correlation_id,
            incident_id=request.incident_id,
            sender_agent=request.sender_agent,
            target_capability=request.target_capability,
            task=request.task,
            timestamp=utc_now_iso(),
            status="received",
            details={
                "payload_classification": request.payload_classification,
                "context": request.context,
            },
        )
    )


def log_step_completed(response: A2AResponse) -> None:
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


def execute_step(request: A2ARequest) -> A2AResponse:
    log_step_received(request)
    response = route_a2a_request(request)
    log_step_completed(response)
    return response


def run_incident_flow(start_request: IncidentStartRequest) -> dict:
    correlation_id = generate_correlation_id()

    # Step 1: Detection Agent normalizes incoming incident
    incident_package = handle_detection(start_request)
    incident_id = incident_package.incident_id

    write_ledger_event(
        LedgerEvent(
            correlation_id=correlation_id,
            incident_id=incident_id,
            sender_agent="system",
            target_capability="incident-detection",
            task="normalize_incident",
            timestamp=utc_now_iso(),
            status="completed",
            details=incident_package.model_dump(),
        )
    )

    # Step 2: Diagnostics
    diagnostics_request = A2ARequest(
        sender_agent="detection-agent",
        target_capability="incident-diagnostics",
        task="analyze_incident",
        incident_id=incident_id,
        payload_classification="internal-operational",
        correlation_id=correlation_id,
        context=incident_package.model_dump(),
    )
    diagnostics_response = execute_step(diagnostics_request)

    # Step 3: Knowledge
    knowledge_request = A2ARequest(
        sender_agent="diagnostics-agent",
        target_capability="runbook-lookup",
        task="lookup_runbook_for_incident",
        incident_id=incident_id,
        payload_classification="internal-operational",
        correlation_id=correlation_id,
        context={
            "service": diagnostics_response.result.get("service"),
            "region": diagnostics_response.result.get("region"),
            "finding": diagnostics_response.result.get("finding"),
        },
    )
    knowledge_response = execute_step(knowledge_request)

    # Step 4: Risk
    risk_request = A2ARequest(
        sender_agent="knowledge-agent",
        target_capability="incident-risk-assessment",
        task="assess_incident_risk",
        incident_id=incident_id,
        payload_classification="internal-operational",
        correlation_id=correlation_id,
        context={
            "service": diagnostics_response.result.get("service"),
            "region": diagnostics_response.result.get("region"),
            "recommended_action": knowledge_response.result.get("recommended_action"),
            "severity": incident_package.severity,
            "confidence": diagnostics_response.result.get("confidence", 0.5),
        },
    )
    risk_response = execute_step(risk_request)

    # Step 5: Remediation
    remediation_request = A2ARequest(
        sender_agent="risk-agent",
        target_capability="incident-remediation",
        task="prepare_remediation_plan",
        incident_id=incident_id,
        payload_classification="internal-operational",
        correlation_id=correlation_id,
        context={
            "service": diagnostics_response.result.get("service"),
            "region": diagnostics_response.result.get("region"),
            "recommended_action": knowledge_response.result.get("recommended_action"),
            "execution_recommendation": risk_response.result.get("execution_recommendation"),
        },
    )
    remediation_response = execute_step(remediation_request)

    write_ledger_event(
        LedgerEvent(
            correlation_id=correlation_id,
            incident_id=incident_id,
            sender_agent="orchestrator",
            target_capability="incident-summary",
            task="complete_incident_flow",
            timestamp=utc_now_iso(),
            status="completed",
            details={
                "final_decision": remediation_response.result.get("final_decision"),
                "execution_mode": remediation_response.result.get("execution_mode"),
            },
        )
    )

    return {
        "correlation_id": correlation_id,
        "incident_id": incident_id,
        "detection": incident_package.model_dump(),
        "diagnostics": diagnostics_response.model_dump(),
        "knowledge": knowledge_response.model_dump(),
        "risk": risk_response.model_dump(),
        "remediation": remediation_response.model_dump(),
    }