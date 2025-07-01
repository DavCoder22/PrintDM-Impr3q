from fastapi import FastAPI, HTTPException, status, Query, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Dict, Any
import uvicorn
import uuid
import httpx
from typing import Optional
import os

app = FastAPI(
    title="Calibration Service",
    description="Microservice for managing printer calibration processes",
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
calibrations_db = {}
calibration_profiles_db = {}
print_counters = {}  # Track print counts per printer

# Configuration
PRINTERS_SERVICE_URL = os.getenv("PRINTERS_SERVICE_URL", "http://printers-service:8000")
MAX_PRINTS_BEFORE_CALIBRATION = 3  # Number of prints before calibration is required

# HTTP client for inter-service communication
http_client = httpx.AsyncClient()

# Models
class CalibrationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRED = "required"  # New status indicating calibration is needed

class CalibrationType(str, Enum):
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    ROUTINE = "routine"

class CalibrationProfileCreate(BaseModel):
    name: str
    description: Optional[str] = None
    printer_model: str
    parameters: Dict[str, Any]
    is_default: bool = False

class CalibrationProfile(CalibrationProfileCreate):
    id: str
    created_at: datetime
    updated_at: datetime

class CalibrationCreate(BaseModel):
    printer_id: str
    profile_id: str
    calibration_type: CalibrationType
    notes: Optional[str] = None

class Calibration(CalibrationCreate):
    id: str
    status: CalibrationStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    results: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

# Routes
@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/calibration/start", status_code=status.HTTP_201_CREATED)
async def start_calibration(calibration: CalibrationCreate):
    """Start a new calibration process"""
    calibration_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    # In a real implementation, we would validate the printer_id and profile_id
    
    db_calibration = {
        "id": calibration_id,
        **calibration.dict(),
        "status": CalibrationStatus.IN_PROGRESS,
        "started_at": now,
        "created_at": now,
        "updated_at": now
    }
    
    calibrations_db[calibration_id] = db_calibration
    
    # In a real implementation, we would start the calibration process asynchronously
    
    return db_calibration

@app.get("/calibration/{calibration_id}")
async def get_calibration(calibration_id: str):
    """Get calibration status and details"""
    if calibration_id not in calibrations_db:
        raise HTTPException(status_code=404, detail="Calibration not found")
    return calibrations_db[calibration_id]

@app.get("/calibration/printer/{printer_id}")
async def get_printer_calibrations(printer_id: str):
    """Get calibration history for a specific printer"""
    printer_calibrations = [
        cal for cal in calibrations_db.values() 
        if cal["printer_id"] == printer_id
    ]
    return {"calibrations": printer_calibrations, "count": len(printer_calibrations)}

@app.post("/calibration/profiles", status_code=status.HTTP_201_CREATED)
async def create_calibration_profile(profile: CalibrationProfileCreate):
    """Create a new calibration profile"""
    profile_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    # If this is set as default, unset any existing default for this printer model
    if profile.is_default:
        for existing_id, existing_profile in calibration_profiles_db.items():
            if (existing_profile["printer_model"] == profile.printer_model and 
                existing_profile["is_default"]):
                calibration_profiles_db[existing_id]["is_default"] = False
    
    db_profile = {
        "id": profile_id,
        **profile.dict(),
        "created_at": now,
        "updated_at": now
    }
    
    calibration_profiles_db[profile_id] = db_profile
    return db_profile

@app.get("/calibration/profiles/{profile_id}")
async def get_calibration_profile(profile_id: str):
    """Get details of a specific calibration profile"""
    if profile_id not in calibration_profiles_db:
        raise HTTPException(status_code=404, detail="Profile not found")
    return calibration_profiles_db[profile_id]

@app.get("/calibration/profiles")
async def list_calibration_profiles(
    printer_model: Optional[str] = None,
    is_default: Optional[bool] = None
):
    """List calibration profiles with optional filtering"""
    profiles = list(calibration_profiles_db.values())
    
    if printer_model:
        profiles = [p for p in profiles if p["printer_model"] == printer_model]
    if is_default is not None:
        profiles = [p for p in profiles if p["is_default"] == is_default]
        
    return {"profiles": profiles, "count": len(profiles)}

async def check_calibration_required(printer_id: str) -> bool:
    """Check if calibration is required for a printer"""
    print_count = print_counters.get(printer_id, 0)
    return print_count >= MAX_PRINTS_BEFORE_CALIBRATION

async def reset_print_counter(printer_id: str):
    """Reset the print counter for a printer after calibration"""
    print_counters[printer_id] = 0

async def notify_calibration_required(printer_id: str):
    """Send notification that calibration is required"""
    # In a real implementation, this would send a notification to the monitoring service
    print(f"[CALIBRATION] Printer {printer_id} requires calibration after {MAX_PRINTS_BEFORE_CALIBRATION} prints")
    
    # Create a calibration record
    calibration_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    calibration = {
        "id": calibration_id,
        "printer_id": printer_id,
        "status": CalibrationStatus.REQUIRED,
        "calibration_type": "automatic",
        "created_at": now,
        "updated_at": now,
        "notes": f"Automatic calibration required after {MAX_PRINTS_BEFORE_CALIBRATION} prints"
    }
    
    calibrations_db[calibration_id] = calibration
    return calibration

@app.post("/printers/{printer_id}/print-completed")
async def record_print_completed(
    printer_id: str,
    background_tasks: BackgroundTasks,
    volume_cm3: float = 0.0
):
    """Record that a print job has completed"""
    # Increment print counter
    current_count = print_counters.get(printer_id, 0) + 1
    print_counters[printer_id] = current_count
    
    # Check if calibration is needed
    if current_count >= MAX_PRINTS_BEFORE_CALIBRATION:
        background_tasks.add_task(notify_calibration_required, printer_id)
    
    return {
        "printer_id": printer_id,
        "print_count": current_count,
        "calibration_required": current_count >= MAX_PRINTS_BEFORE_CALIBRATION,
        "remaining_prints": max(0, MAX_PRINTS_BEFORE_CALIBRATION - current_count)
    }

@app.get("/printers/{printer_id}/calibration-status")
async def get_calibration_status(printer_id: str):
    """Get the current calibration status for a printer"""
    print_count = print_counters.get(printer_id, 0)
    calibration_required = print_count >= MAX_PRINTS_BEFORE_CALIBRATION
    
    # Find the most recent calibration
    latest_calibration = None
    for cal in calibrations_db.values():
        if cal["printer_id"] == printer_id:
            if latest_calibration is None or cal["created_at"] > latest_calibration["created_at"]:
                latest_calibration = cal
    
    return {
        "printer_id": printer_id,
        "print_count": print_count,
        "calibration_required": calibration_required,
        "remaining_prints": max(0, MAX_PRINTS_BEFORE_CALIBRATION - print_count),
        "last_calibration": latest_calibration
    }

@app.post("/printers/{printer_id}/calibrate")
async def perform_calibration(
    printer_id: str,
    calibration_type: CalibrationType = CalibrationType.ROUTINE,
    notes: Optional[str] = None
):
    """Perform calibration for a printer"""
    calibration_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    # In a real implementation, this would trigger the actual calibration process
    calibration = {
        "id": calibration_id,
        "printer_id": printer_id,
        "status": CalibrationStatus.IN_PROGRESS,
        "calibration_type": calibration_type,
        "started_at": now,
        "created_at": now,
        "updated_at": now,
        "notes": notes or ""
    }
    
    calibrations_db[calibration_id] = calibration
    
    # Reset the print counter
    await reset_print_counter(printer_id)
    
    # In a real implementation, you would have a background task to complete the calibration
    return {
        "calibration_id": calibration_id,
        "status": "calibration_started",
        "message": "Calibration process has started"
    }

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize the HTTP client on startup"""
    await http_client.__aenter__()

@app.on_event("shutdown")
async def shutdown_event():
    """Close the HTTP client on shutdown"""
    await http_client.aclose()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
