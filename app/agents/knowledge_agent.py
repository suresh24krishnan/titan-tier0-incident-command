from app.schemas.a2a import A2ARequest, A2AResponse


def handle_knowledge(request: A2ARequest) -> A2AResponse:
    finding = request.context.get("finding", "unknown finding")
    service = request.context.get("service", "unknown-service")

    result = {
        "service": service,
        "finding": finding,
        "runbook_id": "RB-117",
        "recommended_action": "restore previous connection pool baseline",
        "evidence": [
            "matched known incident pattern",
            "runbook RB-117 applies to connection pool degradation"
        ],
        "recommended_next_capability": "incident-risk-assessment"
    }

    return A2AResponse(
        correlation_id=request.correlation_id,
        incident_id=request.incident_id,
        responder_agent="knowledge-agent",
        capability="runbook-lookup",
        task=request.task,
        status="completed",
        result=result,
    )