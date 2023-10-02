from fastapi import APIRouter
from app.database.db_manager import get_db_connection
from app.agents.orchestrator import orchestrate_end_of_month

router = APIRouter()

@router.get("/health")
def health_check():
    # Simple db ping
    conn = get_db_connection()
    conn.execute("SELECT 1")
    conn.close()
    return {"status": "ok", "service": "PRISM"}

@router.post("/end-of-month")
def trigger_end_of_month_orchestration():
    result = orchestrate_end_of_month()
    return result
