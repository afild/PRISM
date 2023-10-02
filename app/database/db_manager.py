import os
import sqlite3
from sqlalchemy import create_engine
from app.config import settings

engine = create_engine(
    settings.database_url, connect_args={"check_same_thread": False}
)

def init_db():
    # If using sqlite:///, we extract the file path
    db_path = settings.database_url.replace("sqlite:///", "")
    
    # We will execute the schema.sql using python sqlite3 directly to ensure all statements run
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            sql_script = f.read()
            
        with sqlite3.connect(db_path) as conn:
            conn.executescript(sql_script)
            conn.commit()
    else:
        print("Aviso: schema.sql não encontrado.")

def get_db_connection():
    db_path = settings.database_url.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
