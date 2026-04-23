from fastapi import HTTPException
from app.core.registry import registry
from app.schemas.a2a import A2ARequest, A2AResponse
from app.agents.diagnostics_agent import handle_diagnostics
from app.agents.knowledge_agent import handle_knowledge
from app.agents.risk_agent import handle_risk
from app.agents.remediation_agent import handle_remediation
from app.utils.ids import generate_correlation_id


def route_a2a_request(request: A2ARequest) -> A2AResponse:
    if not request.correlation_id:
        request.correlation_id = generate_correlation_id()

    target_agent = registry.get_agent_by_capability(request.target_capability)

    if not target_agent:
        raise HTTPException(
            status_code=404,
            detail=f"No agent found for capability '{request.target_capability}'",
        )

    if request.sender_agent not in target_agent.allowed_callers:
        raise HTTPException(
            status_code=403,
            detail=(
                f"Sender '{request.sender_agent}' is not allowed to call "
                f"capability '{request.target_capability}'"
            ),
        )

    if target_agent.status.lower() != "active":
        raise HTTPException(
            status_code=409,
            detail=f"Target agent '{target_agent.agent_id}' is not active",
        )

    if request.target_capability == "incident-diagnostics":
        return handle_diagnostics(request)

    if request.target_capability == "runbook-lookup":
        return handle_knowledge(request)

    if request.target_capability == "incident-risk-assessment":
        return handle_risk(request)

    if request.target_capability == "incident-remediation":
        return handle_remediation(request)

    raise HTTPException(
        status_code=501,
        detail=f"Capability '{request.target_capability}' is not implemented yet",
    )