from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn
import os

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

# Models
class PrinterStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"

class PrinterBase(BaseModel):
    name: str
    model: str
    ip_address: str
    location: str
    status: PrinterStatus = PrinterStatus.OFFLINE

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
        **printer.dict()
    )
    printers_db[printer_id] = db_printer
    return db_printer

@app.get("/printers/{printer_id}", response_model=Printer)
async def get_printer(printer_id: str):
    if printer_id not in printers_db:
        raise HTTPException(status_code=404, detail="Printer not found")
    return printers_db[printer_id]

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
