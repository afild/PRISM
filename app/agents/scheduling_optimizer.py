import pulp
import datetime
from app.database.db_manager import get_db_connection

def optimize_schedule(target_date: str, required_staff: int):
    """
    Usa programação linear (PuLP) para agendar turnos minimizando as horas extras.
    """
    conn = get_db_connection()
    employees = conn.execute("SELECT id, name, hourly_rate FROM employees WHERE is_active = 1").fetchall()
    conn.close()

    if not employees:
        return {"status": "error", "message": "Nenhum funcionário ativo."}

    # Inicializar o problema de minimização
    prob = pulp.LpProblem("Schedule_Optimization", pulp.LpMinimize)

    # Variáveis: se o funcionário i trabalha no turno
    employee_vars = {}
    for emp in employees:
        employee_vars[emp["id"]] = pulp.LpVariable(f"emp_{emp['id']}", cat="Binary")

    # Função Objetivo: Minimizar custo (hourly rate)
    # Assumimos turno de 8h por simplicidade
    prob += pulp.lpSum([employee_vars[emp["id"]] * (emp["hourly_rate"] or 15.0) * 8 for emp in employees])

    # Restrição: Mínimo de staff requerido
    prob += pulp.lpSum([employee_vars[emp["id"]] for emp in employees]) >= required_staff

    # Resolver
    prob.solve(pulp.PULP_CBC_CMD(msg=0))

    if pulp.LpStatus[prob.status] != 'Optimal':
        return {"status": "error", "message": "Solução ótima não encontrada."}

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

    # Gravar no BD
    conn = get_db_connection()
    for s in schedule_result:
        conn.execute(
            "INSERT INTO schedules (employee_id, schedule_date, shift_start, shift_end, is_optimized) VALUES (?, ?, ?, ?, ?)",
            (s["employee_id"], s["date"], s["shift_start"], s["shift_end"], 1)
        )
    conn.commit()
    conn.close()

    return {"status": "success", "schedule": schedule_result}
