from pydantic import BaseModel, Field


class IncidentStartRequest(BaseModel):
    incident_id: str = Field(..., description="Unique incident identifier")
    service: str = Field(..., description="Affected service name")
    severity: str = Field(..., description="Incident severity")
    region: str = Field(..., description="Affected region")
    error_rate: str = Field(..., description="Observed error rate")
    latency: str = Field(..., description="Observed latency")


class IncidentPackage(BaseModel):
    incident_id: str
    service: str
    severity: str
    region: str
    error_rate: str
    latency: str