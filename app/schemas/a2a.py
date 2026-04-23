from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class A2ARequest(BaseModel):
    sender_agent: str = Field(..., description="Agent initiating the request")
    target_capability: str = Field(..., description="Capability requested from TITAN")
    task: str = Field(..., description="Task to be performed")
    incident_id: str = Field(..., description="Incident identifier")
    payload_classification: str = Field(
        default="internal-operational",
        description="Data classification for the payload",
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured task context passed between agents",
    )
    correlation_id: Optional[str] = Field(
        default=None,
        description="Optional correlation ID; TITAN will create one if absent",
    )


class A2AResponse(BaseModel):
    correlation_id: str
    incident_id: str
    responder_agent: str
    capability: str
    task: str
    status: str
    result: Dict[str, Any] = Field(default_factory=dict)