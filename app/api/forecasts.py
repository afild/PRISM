from fastapi import APIRouter
from app.database.db_manager import get_db_connection
from app.agents.labor_forecaster import forecast_labor_costs

router = APIRouter()

@router.get("/labor-costs")
def get_labor_costs():
    conn = get_db_connection()
    forecasts = conn.execute("SELECT * FROM labor_forecasts ORDER BY forecast_month ASC").fetchall()
    conn.close()
    return [dict(f) for f in forecasts]

@router.post("/generate")
def generate_forecasts():
    result = forecast_labor_costs(months_ahead=12)
    return result
