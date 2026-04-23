from __future__ import annotations

import uuid
from typing import Any, Dict


def review_decision_package(decision_package: Dict[str, Any]) -> Dict[str, Any]:
    review_id = f"oly-{uuid.uuid4().hex[:8]}"

    severity = str(decision_package.get("severity", "")).lower()
    technical_risk = str(decision_package.get("technical_risk", "")).lower()
    root_cause = decision_package.get("root_cause", "unknown")

    if severity == "critical":
        decision = "require_human_review"
        rationale = (
            "Critical incident exceeded autonomous execution threshold and requires elevated governance review."
        )
        next_action = "Await human approval before release to execution authority."

    elif technical_risk in {"high", "severe"}:
        decision = "request_more_evidence"
        rationale = "Additional evidence required before approving execution."
        next_action = "Collect more telemetry and resubmit."

    else:
        decision = "approve_for_execution"
        rationale = f"Escalation approved. Root cause validated: {root_cause}."
        next_action = "Release decision package to SENTINEL."

    return {
        "review_id": review_id,
        "status": "completed",
        "decision": decision,
        "rationale": rationale,
        "next_action": next_action,
    }