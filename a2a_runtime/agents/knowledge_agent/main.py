from fastapi import FastAPI
from a2a_runtime.shared.schemas import A2ARequest

app = FastAPI(title="Knowledge Agent")


def lookup_runbook(finding: str) -> dict:
    lowered = str(finding).lower()

    if any(x in lowered for x in ["connection pool", "database"]):
        return {
            "runbook_id": "RB-117",
            "recommended_action": "restore previous connection pool baseline",
            "evidence": [
                "matched known incident pattern for pooled connection degradation",
                "runbook RB-117 applies to database connection pool saturation",
            ],
        }

    if any(x in lowered for x in ["configuration drift", "config drift", "recent change"]):
        return {
            "runbook_id": "RB-203",
            "recommended_action": "restore last known good configuration baseline",
            "evidence": [
                "change-correlated degradation pattern detected",
                "runbook RB-203 applies to configuration drift and post-change instability",
            ],
        }

    if any(x in lowered for x in ["network", "dependency", "dns", "packet loss", "downstream"]):
        return {
            "runbook_id": "RB-315",
            "recommended_action": "validate downstream dependency health and initiate controlled traffic failover if needed",
            "evidence": [
                "dependency/network instability signature detected",
                "runbook RB-315 applies to network path instability and downstream degradation",
            ],
        }

    if any(x in lowered for x in ["memory pressure", "compute saturation", "capacity"]):
        return {
            "runbook_id": "RB-411",
            "recommended_action": "scale capacity and recycle unhealthy runtime instances",
            "evidence": [
                "high-latency low-error profile aligns with capacity or memory pressure",
                "runbook RB-411 applies to memory and compute saturation events",
            ],
        }

    return {
        "runbook_id": "RB-099",
        "recommended_action": "perform guided operator triage and validate the leading runtime indicators",
        "evidence": [
            "no exact pattern match found in operational memory",
            "runbook RB-099 provides generic governed triage guidance",
        ],
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "agent": "knowledge-agent",
        "capability": "runbook-lookup",
    }


@app.post("/a2a/invoke")
def lookup_runbook_for_incident(request: A2ARequest):
    context = request.context or {}

    service = context.get("service", "unknown-service")
    region = context.get("region", "unknown")
    finding = context.get("finding", "root cause hypothesis under evaluation")

    runbook = lookup_runbook(finding)

    return {
        "correlation_id": request.correlation_id,
        "incident_id": request.incident_id,
        "responder_agent": "knowledge-agent",
        "capability": "runbook-lookup",
        "task": request.task,
        "status": "completed",
        "result": {
            "service": service,
            "region": region,
            "finding": finding,
            "runbook_id": runbook["runbook_id"],
            "recommended_action": runbook["recommended_action"],
            "evidence": runbook["evidence"],
            "recommended_next_capability": "incident-risk-assessment",
        },
    }