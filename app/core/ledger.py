import json
from pathlib import Path
from typing import List, Dict, Any
from app.schemas.ledger import LedgerEvent


LEDGER_PATH = Path("data/ledger.jsonl")


def write_ledger_event(event: LedgerEvent) -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER_PATH.open("a", encoding="utf-8") as f:
        f.write(event.model_dump_json() + "\n")


def read_incident_trace(incident_id: str) -> List[Dict[str, Any]]:
    if not LEDGER_PATH.exists():
        return []

    events: List[Dict[str, Any]] = []
    with LEDGER_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            event = json.loads(line)
            if event.get("incident_id") == incident_id:
                events.append(event)

    return events