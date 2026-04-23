from fastapi import FastAPI
from app.config import settings

from app.api.routes_health import router as health_router
from app.api.routes_registry import router as registry_router
from app.api.routes_gateway import router as gateway_router
from app.api.routes_incidents import router as incident_router

app = FastAPI(title=settings.APP_NAME)

app.include_router(health_router)
app.include_router(registry_router)
app.include_router(gateway_router)
app.include_router(incident_router)