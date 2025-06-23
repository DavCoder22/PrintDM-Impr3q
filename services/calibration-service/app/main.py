from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
import uvicorn
import uuid

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

# Models
class CalibrationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

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

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
