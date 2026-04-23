# ============================================
# TITAN A2A Runtime Launcher (v2)
# Starts all agent services + gateway
# ============================================

Write-Host "🚀 Starting TITAN A2A Runtime..." -ForegroundColor Cyan

# Project root (adjust if needed)
$PROJECT_PATH = "C:\Users\sures\OneDrive\Personal Folders\AI Learning\Google ADK\GoogleADK\titan-incident-command"

# Activate venv command
$VENV_ACTIVATE = "$PROJECT_PATH\.venv\Scripts\Activate.ps1"

# Helper to launch a new PowerShell window
function Start-ServiceWindow($name, $command) {
    Write-Host "▶ Starting $name..." -ForegroundColor Yellow

    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "cd '$PROJECT_PATH'; & '$VENV_ACTIVATE'; $command"
    )
}

# ============================================
# Start Agents
# ============================================

Start-ServiceWindow "Diagnostics Agent (8001)" `
"uvicorn a2a_runtime.agents.diagnostics_agent.main:app --port 8001 --reload"

Start-ServiceWindow "Knowledge Agent (8002)" `
"uvicorn a2a_runtime.agents.knowledge_agent.main:app --port 8002 --reload"

Start-ServiceWindow "Risk Agent (8003)" `
"uvicorn a2a_runtime.agents.risk_agent.main:app --port 8003 --reload"

Start-ServiceWindow "Remediation Agent (8004)" `
"uvicorn a2a_runtime.agents.remediation_agent.main:app --port 8004 --reload"

# ============================================
# Start TITAN Gateway
# ============================================

Start-ServiceWindow "TITAN Gateway (8010)" `
"uvicorn a2a_runtime.titan_gateway.main:app --port 8010 --reload"

Write-Host "✅ All services launched!" -ForegroundColor Green
Write-Host "👉 Next: run Streamlit UI" -ForegroundColor Cyan