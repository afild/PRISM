import uvicorn
import os
import sqlite3
from app.database.db_manager import init_db

def main():
    print("Iniciando setup do PRISM...")
    
    # Initialize the local database schema
    init_db()

    print("Banco de dados local prism_workforce.db garantido com sucesso.")
    print("Iniciando PRISM na porta 8004...")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8004,
        reload=True
    )

if __name__ == "__main__":
    main()
