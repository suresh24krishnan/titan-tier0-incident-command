from fastapi import FastAPI
from a2a_runtime.shared.schemas import A2ARequest

app = FastAPI(title="Remediation Agent")


def derive_action_type(recommended_action: str, execution_recommendation: str) -> str:
    action = str(recommended_action).lower()
    recommendation = str(execution_recommendation).lower()

    if recommendation == "human_review":
        return "manual_review_required"

    if recommendation == "olympus-review":
        if "config" in action or "baseline" in action:
            return "governed_config_restore"
        if "failover" in action or "traffic" in action:
            return "governed_failover_review"
        if "scale" in action or "capacity" in action or "memory" in action:
            return "governed_capacity_review"
        return "governed_consensus_review"

    if "connection pool" in action or "database" in action:
        return "config_rollback"

    if "configuration" in action or "config" in action or "baseline" in action:
        return "config_restore"

    if "failover" in action or "traffic" in action or "network" in action or "dependency" in action:
        return "traffic_failover"

    if "scale" in action or "capacity" in action or "memory" in action or "recycle" in action:
        return "capacity_scale"

    return "guided_remediation"


def build_action_package(
    service: str,
    region: str,
    runbook_id: str,
    recommended_action: str,
    execution_recommendation: str,
) -> dict:
    action_type = derive_action_type(recommended_action, execution_recommendation)

    return {
        "action_type": action_type,
        "target_service": service,
        "target_region": region,
        "approved_runbook": runbook_id,
        "recommended_action": recommended_action,
    }


def resolve_final_decision_and_mode(execution_recommendation: str) -> tuple[str, str]:
    recommendation = str(execution_recommendation).lower()

    if recommendation == "allow_with_audit":
        return "recommend_rollback", "sentinel-ready"

    if recommendation == "olympus-review":
        return "escalate_for_consensus", "olympus-review"

    if recommendation == "human_review":
        return "recommend_manual_review", "human-review"

    return "recommend_manual_review", "human-review"


@app.get("/health")
def health():
    return {
        "status": "ok",
        "agent": "remediation-agent",
        "capability": "incident-remediation",
    }


@app.post("/a2a/invoke")
def prepare_remediation_plan(request: A2ARequest):
    context = request.context or {}

    service = context.get("service", "unknown-service")
    region = context.get("region", "unknown")
    severity = context.get("severity", "unknown")
    runbook_id = context.get("runbook_id", "RB-000")
    recommended_action = context.get(
        "recommended_action",
        "perform guided operator triage and validate the leading runtime indicators",
    )
    execution_recommendation = context.get("execution_recommendation", "human_review")

    final_decision, execution_mode = resolve_final_decision_and_mode(
        execution_recommendation
    )

    action_package = build_action_package(
        service=service,
        region=region,
        runbook_id=runbook_id,
        recommended_action=recommended_action,
        execution_recommendation=execution_recommendation,
    )

    return {
        "correlation_id": request.correlation_id,
        "incident_id": request.incident_id,
        "responder_agent": "remediation-agent",
        "capability": "incident-remediation",
        "task": "prepare_remediation_plan",
        "status": "completed",
        "result": {
            "service": service,
            "region": region,
            "severity": severity,
            "runbook_id": runbook_id,
            "recommended_action": recommended_action,
            "execution_recommendation": execution_recommendation,
            "final_decision": final_decision,
            "execution_mode": execution_mode,
            "action_package": action_package,
        },
    }