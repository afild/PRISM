import pandas as pd
from prophet import Prophet
from typing import Dict, Any, List
from app.database.db_manager import get_db_connection
from datetime import datetime
import json

def forecast_labor_costs(months_ahead: int = 12) -> Dict[str, Any]:
    """
    Usa o Prophet para prever custos nos próximos meses com base nos históricos (ou aproximação atual).
    """
    try:
        with get_db_connection() as conn:
            employees = conn.execute("SELECT salary_annual, benefits_cost FROM employees WHERE is_active = 1").fetchall()
            
            if not employees:
                return {"status": "error", "message": "Sem dados para previsão."}

            total_monthly_cost = sum([(e["salary_annual"]/12) + (e["benefits_cost"]/12) for e in employees])
            
            dates = pd.date_range(end=datetime.today(), periods=24, freq='MS')
            costs = [total_monthly_cost * (0.98 ** i) for i in range(24)][::-1]
            
            df = pd.DataFrame({
                'ds': dates,
                'y': costs
            })
            
            m = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
            m.fit(df)
            
            future = m.make_future_dataframe(periods=months_ahead, freq='MS')
            forecast = m.predict(future)
            
            future_forecast = forecast[forecast['ds'] > df['ds'].max()].copy()
            
            results = []
            for _, row in future_forecast.iterrows():
                f_month = row['ds'].strftime("%Y-%m")
                conn.execute(
                    """INSERT INTO labor_forecasts (forecast_month, predicted_cost, confidence_lower, confidence_upper) 
                       VALUES (?, ?, ?, ?)
                       ON CONFLICT(forecast_month) DO UPDATE SET 
                       predicted_cost=excluded.predicted_cost, 
                       confidence_lower=excluded.confidence_lower, 
                       confidence_upper=excluded.confidence_upper""",
                    (f_month, row['yhat'], row['yhat_lower'], row['yhat_upper'])
                )
                results.append({
                    "month": f_month,
                    "predicted": row['yhat'],
                    "lower": row['yhat_lower'],
                    "upper": row['yhat_upper']
                })
                
            conn.commit()

        return {"status": "success", "forecast": results}
    except Exception as e:
        return {"status": "error", "message": "Falha no motor de previsão Prophet", "detail": str(e)}
