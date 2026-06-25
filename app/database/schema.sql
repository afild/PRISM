-- app/database/schema.sql

CREATE TABLE IF NOT EXISTS employees (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT NOT NULL,
    role                TEXT NOT NULL,
    department          TEXT NOT NULL,
    salary_annual       REAL NOT NULL,
    hourly_rate         REAL,
    benefits_cost       REAL DEFAULT 0.0,
    hire_date           DATE NOT NULL,
    naics_code          TEXT,
    is_active           INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS work_logs (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id         INTEGER REFERENCES employees(id),
    log_date            DATE NOT NULL,
    hours_worked        REAL NOT NULL,
    overtime_hours      REAL DEFAULT 0.0,
    tasks_completed     INTEGER DEFAULT 0,
    notes               TEXT, -- Analisado pelo Burnout Risk Agent
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS productivity_metrics (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id         INTEGER REFERENCES employees(id),
    metric_month        TEXT NOT NULL, -- formato YYYY-MM
    revenue_attributed  REAL NOT NULL DEFAULT 0.0,
    roi_score           REAL,
    benchmark_diff      REAL,
    calculated_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(employee_id, metric_month)
);

CREATE TABLE IF NOT EXISTS labor_forecasts (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    forecast_month      TEXT NOT NULL, -- formato YYYY-MM
    predicted_cost      REAL NOT NULL,
    confidence_lower    REAL,
    confidence_upper    REAL,
    generated_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(forecast_month)
);

CREATE TABLE IF NOT EXISTS schedules (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id         INTEGER REFERENCES employees(id),
    schedule_date       DATE NOT NULL,
    shift_start         TEXT, -- HH:MM
    shift_end           TEXT, -- HH:MM
    is_optimized        INTEGER DEFAULT 0,
    status              TEXT DEFAULT 'draft', -- draft|approved
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS burnout_alerts (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id         INTEGER REFERENCES employees(id),
    alert_date          DATE NOT NULL,
    risk_score          REAL NOT NULL, -- 0-100
    risk_factors        TEXT, -- JSON list
    status              TEXT DEFAULT 'open', -- open|reviewed|dismissed
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);
