from pydantic import BaseModel
from typing import List


class Agent(BaseModel):
    agent_id: str
    name: str
    capability: str
    endpoint: str
    status: str
    allowed_callers: List[str]