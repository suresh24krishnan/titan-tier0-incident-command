from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import requests

from app.services.authority_router import route_authority
from a2a_runtime.shared.ids import generate_correlation_id
from a2a_runtime.shared.schemas import A2ARequest
from a2a_runtime.titan_gateway.registry import AGENT_REGISTRY

BASE_DIR = Path(__file__).resolve().parents[2]
LEDGER_PATH = BASE_DIR / "data" / "ledger.jsonl"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_ledger_dir() -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)


def append_ledger_event(event: Dict[str, Any]) -> None:
    _ensure_ledger_dir()
    with LEDGER_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def log_trace_event(
    *,
    correlation_id: str,
    incident_id: str,
    sender_agent: str,
    responder_agent: str,
    target_capability: str,
    task: str,
    status: str,
    summary: str,
    stage: str,
) -> None:
    append_ledger_event(
        {
            "timestamp": _utc_now(),
            "correlation_id": correlation_id,
            "incident_id": incident_id,
            "sender_agent": sender_agent,
            "responder_agent": responder_agent,
            "target_capability": target_capability,
            "task": task,
            "status": status,
            "summary": summary,
            "stage": stage,
        }
    )


def invoke_agent(request: A2ARequest) -> Dict[str, Any]:
    endpoint = AGENT_REGISTRY.get(request.target_capability)
    if not endpoint:
        raise ValueError(f"No endpoint registered for capability '{request.target_capability}'")

    response = requests.post(
        endpoint,
        json=request.model_dump(),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def run_incident_flow(payload: Dict[str, Any]) -> Dict[str, Any]:
    correlation_id = generate_correlation_id()
    incident_id = payload["incident_id"]

    log_trace_event(
        correlation_id=correlation_id,
        incident_id=incident_id,
        sender_agent="incident-intake",
        responder_agent="detection-agent",
        target_capability="incident-detection",
        task="normalize_incident_signal",
        status="completed",
        summary=f"Incident received for service={payload.get('service')} severity={payload.get('severity')}",
        stage="detection",
    )

    diagnostics_request = A2ARequest(
        correlation_id=correlation_id,
        sender_agent="detection-agent",
        target_capability="incident-diagnostics",
        task="analyze_incident",
        incident_id=incident_id,
        payload_classification="internal-operational",
        context=payload,
    )

    try:
        diagnostics_response = invoke_agent(diagnostics_request)
        log_trace_event(
            correlation_id=correlation_id,
            incident_id=incident_id,
            sender_agent="detection-agent",
            responder_agent="diagnostics-agent",
            target_capability="incident-diagnostics",
            task="analyze_incident",
            status=diagnostics_response.get("status", "completed"),
            summary=diagnostics_response.get("result", {}).get("finding", ""),
            stage="diagnostics",
        )
    except Exception as exc:
        log_trace_event(
            correlation_id=correlation_id,
            incident_id=incident_id,
            sender_agent="detection-agent",
            responder_agent="diagnostics-agent",
            target_capability="incident-diagnostics",
            task="analyze_incident",
            status="failed",
            summary=str(exc),
            stage="diagnostics",
        )
        raise

    knowledge_request = A2ARequest(
        correlation_id=correlation_id,
        sender_agent="diagnostics-agent",
        target_capability="runbook-lookup",
        task="lookup_runbook_for_incident",
        incident_id=incident_id,
        payload_classification="internal-operational",
        context={
            "service": diagnostics_response["result"].get("service"),
            "region": diagnostics_response["result"].get("region"),
            "finding": diagnostics_response["result"].get("finding"),
        },
    )

    try:
        knowledge_response = invoke_agent(knowledge_request)
        log_trace_event(
            correlation_id=correlation_id,
            incident_id=incident_id,
            sender_agent="diagnostics-agent",
            responder_agent="knowledge-agent",
            target_capability="runbook-lookup",
            task="lookup_runbook_for_incident",
            status=knowledge_response.get("status", "completed"),
            summary=knowledge_response.get("result", {}).get("runbook_id", ""),
            stage="knowledge",
        )
    except Exception as exc:
        log_trace_event(
            correlation_id=correlation_id,
            incident_id=incident_id,
            sender_agent="diagnostics-agent",
            responder_agent="knowledge-agent",
            target_capability="runbook-lookup",
            task="lookup_runbook_for_incident",
            status="failed",
            summary=str(exc),
            stage="knowledge",
        )
        raise

    risk_request = A2ARequest(
        correlation_id=correlation_id,
        sender_agent="knowledge-agent",
        target_capability="incident-risk-assessment",
        task="assess_incident_risk",
        incident_id=incident_id,
        payload_classification="internal-operational",
        context={
            "service": diagnostics_response["result"].get("service"),
            "region": diagnostics_response["result"].get("region"),
            "recommended_action": knowledge_response["result"].get("recommended_action"),
            "severity": payload.get("severity"),
            "confidence": diagnostics_response["result"].get("confidence", 0.5),
            "finding": diagnostics_response["result"].get("finding"),
            "runbook_id": knowledge_response["result"].get("runbook_id"),
        },
    )

    try:
        risk_response = invoke_agent(risk_request)
        log_trace_event(
            correlation_id=correlation_id,
            incident_id=incident_id,
            sender_agent="knowledge-agent",
            responder_agent="risk-agent",
            target_capability="incident-risk-assessment",
            task="assess_incident_risk",
            status=risk_response.get("status", "completed"),
            summary=risk_response.get("result", {}).get("execution_recommendation", ""),
            stage="risk",
        )
    except Exception as exc:
        log_trace_event(
            correlation_id=correlation_id,
            incident_id=incident_id,
            sender_agent="knowledge-agent",
            responder_agent="risk-agent",
            target_capability="incident-risk-assessment",
            task="assess_incident_risk",
            status="failed",
            summary=str(exc),
            stage="risk",
        )
        raise

    remediation_request = A2ARequest(
        correlation_id=correlation_id,
        sender_agent="risk-agent",
        target_capability="incident-remediation",
        task="prepare_remediation_plan",
        incident_id=incident_id,
        payload_classification="internal-operational",
        context={
            "service": diagnostics_response["result"].get("service"),
            "region": diagnostics_response["result"].get("region"),
            "severity": payload.get("severity"),
            "runbook_id": knowledge_response["result"].get("runbook_id"),
            "recommended_action": knowledge_response["result"].get("recommended_action"),
            "execution_recommendation": risk_response["result"].get("execution_recommendation"),
        },
    )

    try:
        remediation_response = invoke_agent(remediation_request)
        log_trace_event(
            correlation_id=correlation_id,
            incident_id=incident_id,
            sender_agent="risk-agent",
            responder_agent="remediation-agent",
            target_capability="incident-remediation",
            task="prepare_remediation_plan",
            status=remediation_response.get("status", "completed"),
            summary=remediation_response.get("result", {}).get("final_decision", ""),
            stage="remediation",
        )
    except Exception as exc:
        log_trace_event(
            correlation_id=correlation_id,
            incident_id=incident_id,
            sender_agent="risk-agent",
            responder_agent="remediation-agent",
            target_capability="incident-remediation",
            task="prepare_remediation_plan",
            status="failed",
            summary=str(exc),
            stage="remediation",
        )
        raise

    log_trace_event(
        correlation_id=correlation_id,
        incident_id=incident_id,
        sender_agent="titan-gateway",
        responder_agent="titan-governance",
        target_capability="final-decision",
        task="finalize_incident_decision",
        status="completed",
        summary=remediation_response.get("result", {}).get("execution_mode", ""),
        stage="governance",
    )

    # Build decision package for downstream authority routing
    decision_package = {
        "incident_id": incident_id,
        "severity": payload.get("severity"),
        "root_cause": diagnostics_response.get("result", {}).get("finding"),
        "execution_recommendation": risk_response.get("result", {}).get("execution_recommendation"),
        "execution_mode": remediation_response.get("result", {}).get("execution_mode"),
        "final_decision": remediation_response.get("result", {}).get("final_decision"),
        "runbook": knowledge_response.get("result", {}).get("runbook_id"),
        "action_type": remediation_response.get("result", {})
        .get("action_package", {})
        .get("action_type", "config_rollback"),
        "target_service": diagnostics_response.get("result", {}).get("service", payload.get("service")),
        "target_region": diagnostics_response.get("result", {}).get("region", payload.get("region")),
        "technical_risk": risk_response.get("result", {}).get("technical_risk", "medium"),
    }

    authority_result = route_authority(decision_package)

    # Optional trace events for OLYMPUS
    if authority_result.get("olympus_review"):
        olympus_review = authority_result["olympus_review"]
        log_trace_event(
            correlation_id=correlation_id,
            incident_id=incident_id,
            sender_agent="titan-governance",
            responder_agent="olympus-authority",
            target_capability="governance-review",
            task="review_decision_package",
            status=olympus_review.get("status", "completed"),
            summary=olympus_review.get("decision", ""),
            stage="olympus",
        )

    # Optional trace events for SENTINEL
    if authority_result.get("sentinel_execution"):
        sentinel_execution = authority_result["sentinel_execution"]
        log_trace_event(
            correlation_id=correlation_id,
            incident_id=incident_id,
            sender_agent="titan-governance",
            responder_agent="sentinel-authority",
            target_capability="execute-decision-package",
            task="execute_action",
            status=sentinel_execution.get("status", "completed"),
            summary=sentinel_execution.get("summary", ""),
            stage="sentinel",
        )

    return {
        "correlation_id": correlation_id,
        "incident_id": incident_id,
        "detection": {
            "incident_id": incident_id,
            "service": payload.get("service"),
            "severity": payload.get("severity"),
            "region": payload.get("region"),
            "error_rate": payload.get("error_rate"),
            "latency": payload.get("latency"),
        },
        "diagnostics": diagnostics_response,
        "knowledge": knowledge_response,
        "risk": risk_response,
        "remediation": remediation_response,
        "authority_path": authority_result.get("authority_path"),
        "olympus_review": authority_result.get("olympus_review"),
        "sentinel_execution": authority_result.get("sentinel_execution"),
    }