from fastapi import FastAPI
from a2a_runtime.shared.schemas import A2ARequest

app = FastAPI(title="Diagnostics Agent")


def _parse_percent(value: str) -> float:
    try:
        return float(str(value).replace("%", "").strip())
    except Exception:
        return 0.0


def _parse_seconds(value: str) -> float:
    raw = str(value).strip().lower()
    try:
        if raw.endswith("ms"):
            return float(raw.replace("ms", "").strip()) / 1000.0
        if raw.endswith("s"):
            return float(raw.replace("s", "").strip())
        return float(raw)
    except Exception:
        return 0.0


def infer_finding(service: str, severity: str, error_rate: str, latency: str) -> tuple[str, float]:
    sev = str(severity).lower()
    err = _parse_percent(error_rate)
    lat = _parse_seconds(latency)
    svc = str(service).lower()

    if err >= 15 and lat >= 3.5 and ("payment" in svc or "api" in svc):
        return "possible database connection pool issue", 0.84

    if sev == "critical" and err >= 20 and 1.0 <= lat < 3.5:
        return "possible configuration drift after recent change", 0.80

    if err >= 8 and lat >= 2.0 and ("gateway" in svc or "edge" in svc):
        return "possible downstream dependency or network path instability", 0.76

    if lat >= 5.5 and err < 10:
        return "possible memory pressure or compute saturation", 0.72

    if err >= 5 or lat >= 1.5:
        return "possible service-side performance degradation", 0.68

    return "root cause hypothesis under evaluation", 0.60


@app.get("/health")
def health():
    return {
        "status": "ok",
        "agent": "diagnostics-agent",
        "capability": "incident-diagnostics",
    }


@app.post("/a2a/invoke")
def analyze_incident(request: A2ARequest):
    context = request.context or {}

    service = context.get("service", "unknown-service")
    severity = context.get("severity", "unknown")
    region = context.get("region", "unknown")
    error_rate = context.get("error_rate", "0%")
    latency = context.get("latency", "0s")

    finding, confidence = infer_finding(
        service=service,
        severity=severity,
        error_rate=error_rate,
        latency=latency,
    )

    return {
        "correlation_id": request.correlation_id,
        "incident_id": request.incident_id,
        "responder_agent": "diagnostics-agent",
        "capability": "incident-diagnostics",
        "task": request.task,
        "status": "completed",
        "result": {
            "service": service,
            "region": region,
            "observed_error_rate": error_rate,
            "observed_latency": latency,
            "finding": finding,
            "confidence": confidence,
            "recommended_next_capability": "runbook-lookup",
        },
    }