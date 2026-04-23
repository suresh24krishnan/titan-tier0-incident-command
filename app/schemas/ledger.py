from typing import Any, Dict
from pydantic import BaseModel, Field


class LedgerEvent(BaseModel):
    correlation_id: str
    incident_id: str
    sender_agent: str
    target_capability: str
    task: str
    timestamp: str
    status: str
    details: Dict[str, Any] = Field(default_factory=dict)