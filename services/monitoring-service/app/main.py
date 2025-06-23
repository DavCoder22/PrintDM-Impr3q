from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import List, Optional
import uvicorn
import os

app = FastAPI(
    title="Monitoring Service",
    description="Microservice for monitoring printer status and metrics",
    version="0.1.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (replace with database in production)
alerts_db = {}
metrics_db = {}

# Models
class AlertLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

class AlertCreate(BaseModel):
    printer_id: str
    level: AlertLevel
    message: str
    details: Optional[dict] = None

class Alert(AlertCreate):
    id: str
    status: AlertStatus = AlertStatus.OPEN
    created_at: datetime
    updated_at: datetime

class MetricType(str, Enum):
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    PRINT_QUEUE = "print_queue"

class MetricCreate(BaseModel):
    printer_id: str
    metric_type: MetricType
    value: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Metric(MetricCreate):
    id: str

# Routes
@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/monitoring/status")
async def get_system_status():
    """Get current system status overview"""
    return {
        "status": "operational",
        "active_alerts": len([a for a in alerts_db.values() if a["status"] == "open"]),
        "total_printers": 0,  # Would come from printers service
        "last_updated": datetime.utcnow()
    }

@app.post("/monitoring/alerts", status_code=status.HTTP_201_CREATED)
async def create_alert(alert: AlertCreate):
    """Create a new alert"""
    alert_id = str(len(alerts_db) + 1)
    now = datetime.utcnow()
    db_alert = {
        "id": alert_id,
        **alert.dict(),
        "status": AlertStatus.OPEN,
        "created_at": now,
        "updated_at": now
    }
    alerts_db[alert_id] = db_alert
    return db_alert

@app.get("/monitoring/alerts", response_model=List[dict])
async def list_alerts(status: Optional[AlertStatus] = None):
    """List all alerts, optionally filtered by status"""
    alerts = list(alerts_db.values())
    if status:
        alerts = [a for a in alerts if a["status"] == status]
    return alerts

@app.post("/monitoring/metrics", status_code=status.HTTP_201_CREATED)
async def record_metric(metric: MetricCreate):
    """Record a new metric"""
    metric_id = str(len(metrics_db) + 1)
    db_metric = {"id": metric_id, **metric.dict()}
    metrics_db[metric_id] = db_metric
    return db_metric

@app.get("/monitoring/metrics")
async def get_metrics(
    printer_id: Optional[str] = None,
    metric_type: Optional[MetricType] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
):
    """Query metrics with optional filters"""
    metrics = list(metrics_db.values())
    
    if printer_id:
        metrics = [m for m in metrics if m["printer_id"] == printer_id]
    if metric_type:
        metrics = [m for m in metrics if m["metric_type"] == metric_type]
    if start_time:
        metrics = [m for m in metrics if m["timestamp"] >= start_time]
    if end_time:
        metrics = [m for m in metrics if m["timestamp"] <= end_time]
        
    return {"metrics": metrics, "count": len(metrics)}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
