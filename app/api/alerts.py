from fastapi import APIRouter
from app.database.db_manager import get_db_connection
from app.agents.burnout_risk import analyze_burnout_risks

router = APIRouter()

@router.get("/")
def get_alerts():
    conn = get_db_connection()
    alerts = conn.execute("SELECT a.*, e.name FROM burnout_alerts a JOIN employees e ON a.employee_id = e.id WHERE a.status = 'open' ORDER BY a.risk_score DESC").fetchall()
    conn.close()
    return [dict(a) for a in alerts]

@router.post("/analyze")
def run_burnout_analysis():
    result = analyze_burnout_risks()
    return result
