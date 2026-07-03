from fastapi import APIRouter
from app.api import employees, productivity, forecasts, schedules, alerts, system

api_router = APIRouter()

api_router.include_router(employees.router, prefix="/employees", tags=["employees"])
api_router.include_router(productivity.router, prefix="/productivity", tags=["productivity"])
api_router.include_router(forecasts.router, prefix="/forecast", tags=["forecast"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
api_router.include_router(alerts.router, prefix="/burnout", tags=["burnout"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
