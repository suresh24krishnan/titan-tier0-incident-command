import json
from typing import List, Optional
from app.schemas.registry import Agent
from app.config import settings


class AgentRegistry:
    def __init__(self):
        self._agents: List[Agent] = []
        self.load_agents()

    def load_agents(self) -> None:
        with open(settings.REGISTRY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._agents = [Agent(**item) for item in data]

    def get_all_agents(self) -> List[Agent]:
        return self._agents

    def get_agent_by_capability(self, capability: str) -> Optional[Agent]:
        for agent in self._agents:
            if agent.capability == capability:
                return agent
        return None


registry = AgentRegistry()