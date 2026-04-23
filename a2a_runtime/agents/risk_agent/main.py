from fastapi import FastAPI

from a2a_runtime.shared.schemas import A2ARequest, A2AResponse

app = FastAPI(title="Risk Agent")


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "agent": "risk-agent",
        "capability": "incident-risk-assessment",
    }


@app.post("/a2a/invoke", response_model=A2AResponse)
def invoke(request: A2ARequest) -> A2AResponse:
    service = request.context.get("service", "unknown-service")
    region = request.context.get("region", "unknown")
    recommended_action = request.context.get("recommended_action", "unknown")
    severity = str(request.context.get("severity", "medium")).lower()
    confidence = float(request.context.get("confidence", 0.5))

    if severity == "critical":
        business_impact = "critical"
        technical_risk = "high"
        execution_recommendation = "olympus-review"
    elif confidence < 0.75:
        business_impact = "high"
        technical_risk = "medium"
        execution_recommendation = "human-review"
    else:
        business_impact = "high"
        technical_risk = "low"
        execution_recommendation = "allow_with_audit"

    result = {
        "service": service,
        "region": region,
        "business_impact": business_impact,
        "technical_risk": technical_risk,
        "recommended_action": recommended_action,
        "execution_recommendation": execution_recommendation,
        "recommended_next_capability": "incident-remediation",
    }

    return A2AResponse(
        correlation_id=request.correlation_id or "missing-correlation-id",
        incident_id=request.incident_id,
        responder_agent="risk-agent",
        capability="incident-risk-assessment",
        task=request.task,
        status="completed",
        result=result,
    )