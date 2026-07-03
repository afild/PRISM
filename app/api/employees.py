from fastapi import APIRouter
from pydantic import BaseModel
from app.database.db_manager import get_db_connection
from typing import List

router = APIRouter()

class EmployeeCreate(BaseModel):
    name: str
    role: str
    department: str
    salary_annual: float
    hourly_rate: float
    benefits_cost: float = 0.0
    hire_date: str
    naics_code: str = "default"

class WorkLogCreate(BaseModel):
    employee_id: int
    log_date: str
    hours_worked: float
    overtime_hours: float = 0.0
    tasks_completed: int = 0
    notes: str = ""

@router.get("/")
def get_employees():
    conn = get_db_connection()
    employees = conn.execute("SELECT * FROM employees WHERE is_active = 1").fetchall()
    conn.close()
    return [dict(e) for e in employees]

@router.post("/")
def create_employee(emp: EmployeeCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO employees (name, role, department, salary_annual, hourly_rate, benefits_cost, hire_date, naics_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (emp.name, emp.role, emp.department, emp.salary_annual, emp.hourly_rate, emp.benefits_cost, emp.hire_date, emp.naics_code)
    )
    conn.commit()
    emp_id = cursor.lastrowid
    conn.close()
    return {"id": emp_id, "status": "created"}

@router.post("/work-logs")
def create_work_log(log: WorkLogCreate):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO work_logs (employee_id, log_date, hours_worked, overtime_hours, tasks_completed, notes) VALUES (?, ?, ?, ?, ?, ?)",
        (log.employee_id, log.log_date, log.hours_worked, log.overtime_hours, log.tasks_completed, log.notes)
    )
    conn.commit()
    conn.close()
    return {"status": "created"}
