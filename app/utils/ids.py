import uuid


def generate_correlation_id() -> str:
    return f"corr-{uuid.uuid4().hex[:12]}"