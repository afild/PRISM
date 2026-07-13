import pulp
from typing import Dict, Any, List
from app.database.db_manager import get_db_connection

def optimize_schedule(target_date: str, required_staff: int) -> Dict[str, Any]:
    """
    Usa programação linear (PuLP) para agendar turnos minimizando as horas extras.
    """
    try:
        with get_db_connection() as conn:
            employees = conn.execute("SELECT id, name, hourly_rate FROM employees WHERE is_active = 1").fetchall()

        if not employees:
            return {"status": "error", "message": "Nenhum funcionário ativo."}

        prob = pulp.LpProblem("Schedule_Optimization", pulp.LpMinimize)

        employee_vars = {}
        for emp in employees:
            employee_vars[emp["id"]] = pulp.LpVariable(f"emp_{emp['id']}", cat="Binary")

        prob += pulp.lpSum([employee_vars[emp["id"]] * (emp["hourly_rate"] or 15.0) * 8 for emp in employees])

        prob += pulp.lpSum([employee_vars[emp["id"]] for emp in employees]) >= required_staff

        prob.solve(pulp.PULP_CBC_CMD(msg=0))

        if pulp.LpStatus[prob.status] != 'Optimal':
            return {"status": "error", "message": "Solução ótima não encontrada pelo solver PuLP."}

        schedule_result = []
        for emp in employees:
            if employee_vars[emp["id"]].varValue == 1.0:
                schedule_result.append({
                    "employee_id": emp["id"],
                    "name": emp["name"],
                    "shift_start": "09:00",
                    "shift_end": "17:00",
                    "date": target_date
                })

        with get_db_connection() as conn:
            for s in schedule_result:
                conn.execute(
                    "INSERT INTO schedules (employee_id, schedule_date, shift_start, shift_end, is_optimized) VALUES (?, ?, ?, ?, ?)",
                    (s["employee_id"], s["date"], s["shift_start"], s["shift_end"], 1)
                )
            conn.commit()

        return {"status": "success", "schedule": schedule_result}
    except Exception as e:
        return {"status": "error", "message": "Erro fatal no otimizador de escala", "detail": str(e)}
