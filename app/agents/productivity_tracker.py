from typing import Dict, Any, List
from app.database.db_manager import get_db_connection
from app.plugins.nova_reader import fetch_nova_revenue
from datetime import datetime

def calculate_roi_and_revenue() -> Dict[str, Any]:
    """
    Agrupa receitas do NOVA e calcula Revenue per Employee e ROI por funcionário.
    """
    try:
        current_month = datetime.now().strftime("%Y-%m")
        
        with get_db_connection() as conn:
            employees = conn.execute("SELECT id, salary_annual, benefits_cost FROM employees WHERE is_active = 1").fetchall()
            
            if not employees:
                return {"status": "error", "message": "Nenhum funcionário ativo."}
                
            total_revenue = fetch_nova_revenue(current_month)
            headcount = len(employees)
            
            if headcount == 0:
                return {"status": "error", "message": "Headcount é zero, impossível calcular métricas."}
                
            revenue_per_employee = total_revenue / headcount

            results = []
            for emp in employees:
                monthly_cost = (emp["salary_annual"]/12) + (emp["benefits_cost"]/12)
                # Ensure monthly cost is not negative or zero to avoid division issues or fake high ROI
                monthly_cost = max(monthly_cost, 0.01)
                
                roi_score = (revenue_per_employee / monthly_cost) * 100
                
                conn.execute(
                    """INSERT INTO productivity_metrics (employee_id, metric_month, revenue_attributed, roi_score, benchmark_diff) 
                       VALUES (?, ?, ?, ?, ?)
                       ON CONFLICT(employee_id, metric_month) DO UPDATE SET 
                       revenue_attributed=excluded.revenue_attributed, 
                       roi_score=excluded.roi_score""",
                    (emp["id"], current_month, revenue_per_employee, roi_score, 0.0)
                )
                results.append({"employee_id": emp["id"], "roi": roi_score})
                
            conn.commit()
            
        return {
            "status": "success", 
            "global_revenue_per_employee": revenue_per_employee,
            "employees_processed": headcount
        }
    except Exception as e:
        return {"status": "error", "message": "Erro ao calcular produtividade", "detail": str(e)}
