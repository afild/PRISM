from sentence_transformers import SentenceTransformer, util
import json
from typing import Dict, Any, List
from app.database.db_manager import get_db_connection
from datetime import datetime, timedelta

# Inicializar modelo offline local
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    burnout_keywords = ["tired", "overwhelmed", "exhausted", "too many hours", "stress", "missed deadline", "can't sleep", "burned out"]
    burnout_embeddings = model.encode(burnout_keywords, convert_to_tensor=True)
except Exception:
    model = None
    burnout_embeddings = None

def analyze_burnout_risks() -> Dict[str, Any]:
    """
    Avalia risco de burnout analisando NLP de 'notes' e horas extras na tabela 'work_logs'.
    """
    if model is None:
        return {"status": "error", "message": "Modelo SentenceTransformer não inicializado"}
        
    try:
        last_week = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        with get_db_connection() as conn:
            logs = conn.execute(
                "SELECT id, employee_id, notes, overtime_hours FROM work_logs WHERE log_date >= ? AND notes IS NOT NULL AND notes != ''",
                (last_week,)
            ).fetchall()
            
            alerts = []
            for log in logs:
                text = str(log["notes"])
                log_embedding = model.encode(text, convert_to_tensor=True)
                
                cosine_scores = util.cos_sim(log_embedding, burnout_embeddings)
                max_score = float(cosine_scores.max())
                
                overtime = float(log["overtime_hours"])
                if max_score > 0.65 or overtime >= 10.0:
                    risk_score = min(max_score * 100 + (overtime * 2), 100.0)
                    factors = []
                    if max_score > 0.65:
                        factors.append("NLP: Linguagem de exaustão detectada")
                    if overtime >= 10.0:
                        factors.append("Carga Horária: Excesso de horas extras na semana")
                        
                    conn.execute(
                        "INSERT INTO burnout_alerts (employee_id, alert_date, risk_score, risk_factors) VALUES (?, ?, ?, ?)",
                        (log["employee_id"], datetime.now().strftime("%Y-%m-%d"), risk_score, json.dumps(factors))
                    )
                    alerts.append({"employee_id": log["employee_id"], "score": risk_score})
                    
            conn.commit()
            
        return {"status": "success", "alerts_generated": len(alerts), "details": alerts}
    except Exception as e:
        return {"status": "error", "message": "Erro ao analisar riscos de burnout via NLP", "detail": str(e)}
