from fastapi import APIRouter
from app.database.db_manager import get_db_connection
from app.agents.productivity_tracker import calculate_roi_and_revenue

router = APIRouter()

@router.get("/revenue-per-employee")
def get_revenue_per_employee():
    conn = get_db_connection()
    metrics = conn.execute("SELECT * FROM productivity_metrics ORDER BY metric_month DESC LIMIT 10").fetchall()
    conn.close()
    return [dict(m) for m in metrics]

@router.get("/roi-ranking")
def get_roi_ranking():
    conn = get_db_connection()
    query = """
        SELECT e.name, e.department, p.roi_score, p.metric_month 
        FROM productivity_metrics p
        JOIN employees e ON p.employee_id = e.id
        ORDER BY p.roi_score DESC
        LIMIT 10
    """
    ranking = conn.execute(query).fetchall()
    conn.close()
    return [dict(r) for r in ranking]

@router.post("/calculate")
def trigger_productivity_tracker():
    result = calculate_roi_and_revenue()
    return result
