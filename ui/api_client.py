import os
import requests

BASE_URL = os.getenv("TITAN_API_BASE_URL", "http://127.0.0.1:8010")


def start_incident(payload: dict) -> dict:
    response = requests.post(f"{BASE_URL}/incidents/start", json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def get_incident_trace(incident_id: str) -> dict:
    response = requests.get(f"{BASE_URL}/incidents/{incident_id}/trace", timeout=30)
    if response.status_code == 404:
        return {
            "incident_id": incident_id,
            "trace": [],
            "trace_available": False,
        }
    response.raise_for_status()
    data = response.json()
    if "trace_available" not in data:
        data["trace_available"] = True
    return data


def get_base_url() -> str:
    return BASE_URL