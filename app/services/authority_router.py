from __future__ import annotations

from typing import Any, Dict

from app.services.olympus_simulator import review_decision_package
from app.services.sentinel_simulator import execute_decision_package


def route_authority(decision_package: Dict[str, Any]) -> Dict[str, Any]:
    severity = str(decision_package.get("severity", "")).lower()
    execution_mode = str(decision_package.get("execution_mode", "")).lower()
    execution_recommendation = str(decision_package.get("execution_recommendation", "")).lower()

    # 🔷 Route to OLYMPUS
    if (
        execution_mode == "olympus-review"
        or execution_recommendation == "escalate"
        or severity == "critical"
    ):
        olympus_result = review_decision_package(decision_package)

        # 🔁 If OLYMPUS approves → go to SENTINEL
        if olympus_result["decision"] == "approve_for_execution":
            sentinel_result = execute_decision_package(decision_package)

            return {
                "authority_path": "olympus_then_sentinel",
                "olympus_review": olympus_result,
                "sentinel_execution": sentinel_result,
            }

        # ❌ Otherwise stop at OLYMPUS
        return {
            "authority_path": "olympus_only",
            "olympus_review": olympus_result,
        }

    # 🔷 Direct SENTINEL path
    sentinel_result = execute_decision_package(decision_package)

    return {
        "authority_path": "sentinel_only",
        "sentinel_execution": sentinel_result,
    }