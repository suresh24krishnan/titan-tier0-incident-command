from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class A2ARequest(BaseModel):
    correlation_id: Optional[str] = Field(default=None)
    sender_agent: str
    target_capability: str
    task: str
    incident_id: str
    payload_classification: str = Field(default="internal-operational")
    context: Dict[str, Any] = Field(default_factory=dict)


class A2AResponse(BaseModel):
    correlation_id: str
    incident_id: str
    responder_agent: str
    capability: str
    task: str
    status: str
    result: Dict[str, Any] = Field(default_factory=dict)


class IncidentStartRequest(BaseModel):
    incident_id: str
    service: str
    severity: str
    region: str
    error_rate: str
    latency: str