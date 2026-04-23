from app.schemas.a2a import A2ARequest, A2AResponse


def handle_diagnostics(request: A2ARequest) -> A2AResponse:
    service = request.context.get("service", "unknown-service")
    error_rate = request.context.get("error_rate", "unknown")
    latency = request.context.get("latency", "unknown")
    region = request.context.get("region", "unknown")

    finding = {
        "service": service,
        "region": region,
        "observed_error_rate": error_rate,
        "observed_latency": latency,
        "finding": "possible configuration drift or database connection pool issue",
        "confidence": 0.84,
        "recommended_next_capability": "runbook-lookup",
    }

    return A2AResponse(
        correlation_id=request.correlation_id,
        incident_id=request.incident_id,
        responder_agent="diagnostics-agent",
        capability="incident-diagnostics",
        task=request.task,
        status="completed",
        result=finding,
    )