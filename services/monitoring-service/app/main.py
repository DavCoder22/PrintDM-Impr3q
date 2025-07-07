from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import List, Optional, Dict, Any
import uvicorn
import os
import uuid
import asyncio
import httpx
from typing import Optional

app = FastAPI(
    title="Monitoring Service",
    description="""
    ## Microservicio de Monitoreo de Impresoras 3D
    
    Este servicio maneja el monitoreo en tiempo real de las impresoras 3D y sus trabajos de impresión:
    
    ### Funcionalidades Principales:
    - **Gestión de Trabajos de Impresión**: Crear, monitorear y controlar trabajos de impresión
    - **Monitoreo de Estado**: Seguimiento en tiempo real del estado de las impresoras
    - **Sistema de Alertas**: Generación y gestión de alertas del sistema
    - **Métricas de Rendimiento**: Recopilación y consulta de métricas de impresión
    - **Control de Trabajos**: Pausar, reanudar y cancelar trabajos de impresión
    
    ### Integración:
    - Se integra con el **Printers Service** para obtener información de impresoras
    - Se integra con el **Calibration Service** para gestionar alertas de calibración
    - Proporciona endpoints para el dashboard de monitoreo
    
    ### Endpoints Disponibles:
    - `GET /health` - Verificación de salud del servicio
    - `GET /monitoring/status` - Estado general del sistema
    - `POST /monitoring/alerts` - Crear alertas
    - `GET /monitoring/alerts` - Listar alertas
    - `POST /monitoring/metrics` - Registrar métricas
    - `GET /monitoring/metrics` - Consultar métricas
    - `POST /print-jobs` - Crear trabajos de impresión
    - `GET /print-jobs/{job_id}` - Obtener trabajo de impresión
    - `PUT /print-jobs/{job_id}` - Actualizar trabajo de impresión
    - `POST /print-jobs/{job_id}/start` - Iniciar trabajo
    - `POST /print-jobs/{job_id}/pause` - Pausar trabajo
    - `POST /print-jobs/{job_id}/resume` - Reanudar trabajo
    - `POST /print-jobs/{job_id}/cancel` - Cancelar trabajo
    - `GET /printers/{printer_id}/status` - Estado de impresora específica
    """,
    version="1.0.0",
    contact={
        "name": "PrintDM Team",
        "email": "support@printdm.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    tags=[
        {
            "name": "health",
            "description": "Endpoints para verificación de salud del servicio"
        },
        {
            "name": "monitoring",
            "description": "Monitoreo general del sistema y métricas"
        },
        {
            "name": "alerts",
            "description": "Gestión de alertas del sistema"
        },
        {
            "name": "metrics",
            "description": "Recopilación y consulta de métricas"
        },
        {
            "name": "print-jobs",
            "description": "Gestión completa de trabajos de impresión"
        },
        {
            "name": "printer-status",
            "description": "Monitoreo del estado de impresoras específicas"
        }
    ]
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
print_jobs = {}
printer_status = {}

# Configuration
PRINTERS_SERVICE_URL = os.getenv("PRINTERS_SERVICE_URL", "http://printers-service:8000")
CALIBRATION_SERVICE_URL = os.getenv("CALIBRATION_SERVICE_URL", "http://calibration-service:8001")

# HTTP client for inter-service communication
http_client = httpx.AsyncClient()

# Enums
class AlertLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

class PrintJobStatus(str, Enum):
    QUEUED = "queued"
    PREPARING = "preparing"
    PRINTING = "printing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PrinterStatus(str, Enum):
    IDLE = "idle"
    PRINTING = "printing"
    PAUSED = "paused"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"
    CALIBRATION_NEEDED = "calibration_needed"

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
    PRINT_PROGRESS = "print_progress"
    TEMPERATURE = "temperature"
    PRINT_DURATION = "print_duration"

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

# Models
class PrintJob(BaseModel):
    id: str
    printer_id: str
    status: PrintJobStatus
    file_name: str
    file_size: int
    estimated_duration: int  # in seconds
    progress: float = 0.0  # 0.0 to 100.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PrintJobCreate(BaseModel):
    printer_id: str
    file_name: str
    file_size: int
    estimated_duration: int  # in seconds

class PrintJobUpdate(BaseModel):
    status: Optional[PrintJobStatus] = None
    progress: Optional[float] = None
    error_message: Optional[str] = None

# Print Job Management
@app.post("/print-jobs", status_code=status.HTTP_201_CREATED)
async def create_print_job(job: PrintJobCreate):
    """Create a new print job"""
    job_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    # Create the print job
    print_job = PrintJob(
        id=job_id,
        status=PrintJobStatus.QUEUED,
        progress=0.0,
        created_at=now,
        updated_at=now,
        **job.dict()
    )
    
    print_jobs[job_id] = print_job
    
    # Update printer status
    await update_printer_status(
        job.printer_id, 
        PrinterStatus.PRINTING,
        f"Starting print job {job_id}"
    )
    
    return print_job

@app.get("/print-jobs/{job_id}")
async def get_print_job(job_id: str):
    """Get a print job by ID"""
    if job_id not in print_jobs:
        raise HTTPException(status_code=404, detail="Print job not found")
    return print_jobs[job_id]

@app.put("/print-jobs/{job_id}")
async def update_print_job(job_id: str, update: PrintJobUpdate):
    """Update a print job"""
    if job_id not in print_jobs:
        raise HTTPException(status_code=404, detail="Print job not found")
    
    job = print_jobs[job_id]
    update_dict = update.dict(exclude_unset=True)
    
    # Update fields
    for field, value in update_dict.items():
        setattr(job, field, value)
    
    job.updated_at = datetime.utcnow()
    
    # If status changed to printing, set start time
    if update.status == PrintJobStatus.PRINTING and not job.start_time:
        job.start_time = datetime.utcnow()
    
    # If status changed to completed/failed/cancelled, set end time
    if update.status in [PrintJobStatus.COMPLETED, PrintJobStatus.FAILED, PrintJobStatus.CANCELLED]:
        job.end_time = job.end_time or datetime.utcnow()
        
        # If completed, ensure progress is 100%
        if update.status == PrintJobStatus.COMPLETED:
            job.progress = 100.0
    
    return job

@app.post("/print-jobs/{job_id}/start")
async def start_print_job(job_id: str):
    """Mark a print job as started"""
    if job_id not in print_jobs:
        raise HTTPException(status_code=404, detail="Print job not found")
    
    job = print_jobs[job_id]
    job.status = PrintJobStatus.PRINTING
    job.start_time = job.start_time or datetime.utcnow()
    job.updated_at = datetime.utcnow()
    
    return job

@app.post("/print-jobs/{job_id}/pause")
async def pause_print_job(job_id: str):
    """Pause a print job"""
    if job_id not in print_jobs:
        raise HTTPException(status_code=404, detail="Print job not found")
    
    job = print_jobs[job_id]
    job.status = PrintJobStatus.PAUSED
    job.updated_at = datetime.utcnow()
    
    return job

@app.post("/print-jobs/{job_id}/resume")
async def resume_print_job(job_id: str):
    """Resume a paused print job"""
    if job_id not in print_jobs:
        raise HTTPException(status_code=404, detail="Print job not found")
    
    job = print_jobs[job_id]
    if job.status != PrintJobStatus.PAUSED:
        raise HTTPException(status_code=400, detail="Print job is not paused")
    
    job.status = PrintJobStatus.PRINTING
    job.updated_at = datetime.utcnow()
    
    return job

@app.post("/print-jobs/{job_id}/cancel")
async def cancel_print_job(job_id: str):
    """Cancel a print job"""
    if job_id not in print_jobs:
        raise HTTPException(status_code=404, detail="Print job not found")
    
    job = print_jobs[job_id]
    if job.status in [PrintJobStatus.COMPLETED, PrintJobStatus.FAILED, PrintJobStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel a {job.status} print job")
    
    job.status = PrintJobStatus.CANCELLED
    job.end_time = datetime.utcnow()
    job.updated_at = datetime.utcnow()
    
    return job

# Printer Status Management
async def update_printer_status(printer_id: str, status: PrinterStatus, message: str = ""):
    """Update printer status and log the change"""
    now = datetime.utcnow()
    printer_status[printer_id] = {
        "status": status,
        "last_updated": now,
        "message": message
    }
    
    # Log the status change
    alert_id = str(uuid.uuid4())
    alert_level = AlertLevel.INFO
    
    if status in [PrinterStatus.ERROR, PrinterStatus.MAINTENANCE, PrinterStatus.CALIBRATION_NEEDED]:
        alert_level = AlertLevel.WARNING if status == PrinterStatus.CALIBRATION_NEEDED else AlertLevel.ERROR
    
    alerts_db[alert_id] = {
        "id": alert_id,
        "printer_id": printer_id,
        "level": alert_level,
        "message": f"Printer status changed to {status}: {message}",
        "status": AlertStatus.OPEN,
        "created_at": now,
        "updated_at": now
    }
    
    return printer_status[printer_id]

@app.get("/printers/{printer_id}/status")
async def get_printer_status(printer_id: str):
    """Get current status of a printer"""
    status = printer_status.get(printer_id, {
        "status": PrinterStatus.OFFLINE,
        "last_updated": None,
        "message": "Printer status unknown"
    })
    
    # Check if calibration is needed
    try:
        calibration_status = await http_client.get(
            f"{CALIBRATION_SERVICE_URL}/printers/{printer_id}/calibration-status"
        )
        if calibration_status.status_code == 200:
            cal_data = calibration_status.json()
            if cal_data.get("calibration_required"):
                await update_printer_status(
                    printer_id,
                    PrinterStatus.CALIBRATION_NEEDED,
                    "Calibration required after 3 prints"
                )
    except Exception as e:
        print(f"Error checking calibration status: {e}")
    
    return printer_status.get(printer_id, {"status": PrinterStatus.OFFLINE, "message": "Printer not found"})

# Background task to monitor print jobs
async def monitor_print_jobs():
    """Background task to monitor print jobs and update status"""
    while True:
        now = datetime.utcnow()
        
        for job_id, job in list(print_jobs.items()):
            if job.status == PrintJobStatus.PRINTING and job.start_time:
                # Update progress based on elapsed time vs estimated duration
                elapsed = (now - job.start_time).total_seconds()
                progress = min(100.0, (elapsed / job.estimated_duration) * 100)
                job.progress = progress
                
                # If estimated time has passed, check if job is stuck
                if elapsed > job.estimated_duration * 1.1:  # 10% over estimated time
                    job.status = PrintJobStatus.FAILED
                    job.error_message = "Print job exceeded estimated time"
                    job.end_time = now
                    
                    # Update printer status
                    await update_printer_status(
                        job.printer_id,
                        PrinterStatus.ERROR,
                        f"Print job {job_id} failed - exceeded estimated time"
                    )
        
        await asyncio.sleep(10)  # Check every 10 seconds

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize the HTTP client and background tasks on startup"""
    await http_client.__aenter__()
    asyncio.create_task(monitor_print_jobs())

@app.on_event("shutdown")
async def shutdown_event():
    """Close the HTTP client on shutdown"""
    await http_client.aclose()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8002, reload=True)
