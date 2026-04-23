import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME = os.getenv("APP_NAME", "TITAN Incident Command Platform")
    ENV = os.getenv("APP_ENV", "dev")
    REGISTRY_PATH = os.getenv("AGENT_REGISTRY_PATH", "data/agents_registry.json")

settings = Settings()