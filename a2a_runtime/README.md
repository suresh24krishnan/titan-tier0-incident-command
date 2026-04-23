# TITAN A2A Runtime V2

This is the parallel production-style A2A runtime for TITAN.

## Services
- TITAN Gateway: port 8000
- Diagnostics Agent: port 8001
- Knowledge Agent: port 8002

## Run commands

```powershell
uvicorn a2a_runtime.agents.diagnostics_agent.main:app --port 8001 --reload
uvicorn a2a_runtime.agents.knowledge_agent.main:app --port 8002 --reload
uvicorn a2a_runtime.titan_gateway.main:app --port 8000 --reload