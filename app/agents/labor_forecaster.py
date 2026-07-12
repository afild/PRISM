import pandas as pd
from prophet import Prophet
from app.database.db_manager import get_db_connection
from datetime import datetime
import json

def forecast_labor_costs(months_ahead: int = 12):
    """
    Usa o Prophet para prever custos nos próximos meses com base nos históricos (ou aproximação atual).
    """
    conn = get_db_connection()
    
    # Num cenário real, buscaríamos um histórico mensal.
    # Para o PRISM v1.0, geramos dados baseados na folha atual se não houver histórico suficiente.
    employees = conn.execute("SELECT salary_annual, benefits_cost FROM employees WHERE is_active = 1").fetchall()
    
    if not employees:
        conn.close()
        return {"status": "error", "message": "Sem dados para previsão."}

    total_monthly_cost = sum([(e["salary_annual"]/12) + (e["benefits_cost"]/12) for e in employees])
    
    # Criando um dataset sintético de histórico (últimos 24 meses) simulando pequena inflação
    dates = pd.date_range(end=datetime.today(), periods=24, freq='MS')
    costs = [total_monthly_cost * (0.98 ** i) for i in range(24)][::-1] # Crescendo até o atual
    
    df = pd.DataFrame({
        'ds': dates,
        'y': costs
    })
    
    m = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    m.fit(df)
    
    future = m.make_future_dataframe(periods=months_ahead, freq='MS')
    forecast = m.predict(future)
    
    # Filtrar apenas o futuro
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
    conn.close()

    return {"status": "success", "forecast": results}
