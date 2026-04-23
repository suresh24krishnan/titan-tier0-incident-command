from fastapi import APIRouter
from app.core.registry import registry

router = APIRouter(prefix="/registry", tags=["Registry"])

@router.get("/agents")
def get_agents():
    return registry.get_all_agents()