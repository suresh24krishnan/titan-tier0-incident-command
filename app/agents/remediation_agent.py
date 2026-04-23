from app.schemas.a2a import A2ARequest, A2AResponse


def handle_remediation(request: A2ARequest) -> A2AResponse:
    service = request.context.get("service", "unknown-service")
    region = request.context.get("region", "unknown")
    recommended_action = request.context.get("recommended_action", "unknown")
    execution_recommendation = request.context.get("execution_recommendation", "human-review")

    if execution_recommendation == "allow_with_audit":
        execution_mode = "sentinel-ready"
        final_decision = "recommend_rollback"
    elif execution_recommendation == "olympus-review":
        execution_mode = "olympus-review"
        final_decision = "escalate_for_consensus"
    else:
        execution_mode = "human-review"
        final_decision = "recommend_manual_review"

    result = {
        "final_decision": final_decision,
        "execution_mode": execution_mode,
        "action_package": {
            "action_type": "config_rollback",
            "target_service": service,
            "target_region": region,
            "approved_runbook": "RB-117",
            "recommended_action": recommended_action
        }
    }

    return A2AResponse(
        correlation_id=request.correlation_id,
        incident_id=request.incident_id,
        responder_agent="remediation-agent",
        capability="incident-remediation",
        task=request.task,
        status="completed",
        result=result,
    )