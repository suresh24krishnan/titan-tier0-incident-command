from app.schemas.incident import IncidentStartRequest, IncidentPackage


def handle_detection(request: IncidentStartRequest) -> IncidentPackage:
    return IncidentPackage(
        incident_id=request.incident_id,
        service=request.service,
        severity=request.severity,
        region=request.region,
        error_rate=request.error_rate,
        latency=request.latency,
    )