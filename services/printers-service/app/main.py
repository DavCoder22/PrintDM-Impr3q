from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uvicorn
import os
from enum import Enum

app = FastAPI(
    title="Printers Service",
    description="Microservice for managing printers and their operations",
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
printers_db = {}
print_job_counter = {}

# Models
class PrinterStatus(str, Enum):
    IDLE = "idle"
    PRINTING = "printing"
    PAUSED = "paused"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"

class PrinterSpecs(BaseModel):
    max_volume_mm: Dict[str, float] = Field(
        {"x": 200, "y": 200, "z": 200},  # Default max volume in mm
        description="Maximum printable volume in millimeters (x, y, z)"
    )
    supported_materials: List[str] = ["PLA", "ABS", "PETG"]
    layer_resolution_mm: float = Field(0.2, ge=0.05, le=0.4)
    has_heated_bed: bool = True

class PrinterBase(BaseModel):
    name: str
    model: str
    ip_address: str
    location: str
    status: PrinterStatus = PrinterStatus.OFFLINE
    print_volume_tolerance: float = Field(
        100.0,  # Default tolerance in cm³
        ge=0,
        description="Maximum allowed print volume in cubic centimeters before requiring maintenance"
    )
    specs: PrinterSpecs = Field(default_factory=PrinterSpecs)
    current_print_volume: float = Field(0.0, ge=0, description="Current accumulated print volume in cm³")
    last_calibration_date: Optional[datetime] = None
    
    @validator('ip_address')
    def validate_ip_address(cls, v):
        # Simple IP address validation
        parts = v.split('.')
        if len(parts) != 4:
            raise ValueError('IP address must be in format X.X.X.X')
        for part in parts:
            if not part.isdigit() or not 0 <= int(part) <= 255:
                raise ValueError('Each part of IP must be 0-255')
        return v

class PrinterCreate(PrinterBase):
    pass

class Printer(PrinterBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Routes
@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/printers", response_model=List[Printer])
async def list_printers():
    return list(printers_db.values())

@app.post("/printers", response_model=Printer, status_code=status.HTTP_201_CREATED)
async def create_printer(printer: PrinterCreate):
    printer_id = str(len(printers_db) + 1)
    now = datetime.utcnow()
    db_printer = Printer(
        id=printer_id,
        created_at=now,
        updated_at=now,
        **printer.dict(exclude_unset=True)
    )
    printers_db[printer_id] = db_printer
    print_job_counter[printer_id] = 0
    return db_printer

@app.get("/printers/{printer_id}", response_model=Printer)
async def get_printer(printer_id: str):
    if printer_id not in printers_db:
        raise HTTPException(status_code=404, detail="Printer not found")
    return printers_db[printer_id]

@app.put("/printers/{printer_id}/volume", response_model=Printer)
async def update_print_volume(printer_id: str, volume_cm3: float):
    """Update the current print volume for a printer"""
    if printer_id not in printers_db:
        raise HTTPException(status_code=404, detail="Printer not found")
    
    printer = printers_db[printer_id]
    printer.current_print_volume += volume_cm3
    printer.updated_at = datetime.utcnow()
    
    # Increment print job counter for calibration service
    print_job_counter[printer_id] = print_job_counter.get(printer_id, 0) + 1
    
    return printer

@app.post("/printers/{printer_id}/calibrate", response_model=Printer)
async def calibrate_printer(printer_id: str):
    """Reset calibration status for a printer"""
    if printer_id not in printers_db:
        raise HTTPException(status_code=404, detail="Printer not found")
    
    printer = printers_db[printer_id]
    printer.last_calibration_date = datetime.utcnow()
    printer.updated_at = datetime.utcnow()
    print_job_counter[printer_id] = 0  # Reset print counter after calibration
    
    return printer

@app.get("/printers/{printer_id}/info")
async def get_printer_info(printer_id: str):
    """Get printer information including specs and volume tolerance"""
    if printer_id not in printers_db:
        raise HTTPException(status_code=404, detail="Printer not found")
    
    printer = printers_db[printer_id]
    return {
        "id": printer.id,
        "name": printer.name,
        "model": printer.model,
        "status": printer.status,
        "print_volume_tolerance": printer.print_volume_tolerance,
        "current_print_volume": printer.current_print_volume,
        "last_calibration_date": printer.last_calibration_date,
        "specs": printer.specs.dict() if hasattr(printer, 'specs') else {}
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
