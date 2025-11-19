"""
Designer API - Study CRUD Operations
Handles study creation, retrieval, update, delete
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

router = APIRouter(prefix="/api/v1", tags=["Designer"])

# Pydantic models
class FormSchema(BaseModel):
    form_name: str
    frequency_days: int
    active_phases: List[str] = ["all"]
    fields: List[dict]

class StudyCreate(BaseModel):
    name: str
    description: str
    duration_days: int
    status: Optional[str] = "draft"
    forms: List[dict] = []

class StudyResponse(BaseModel):
    id: int
    name: str
    description: str
    duration_days: int
    status: str
    forms: List[dict]
    created_by: int
    created_at: datetime
    form_count: int = 0
    participant_count: int = 0

# In-memory storage (temporary - will use database later)
studies_db = {}
study_counter = 1

@router.post("/studies", response_model=StudyResponse)
async def create_study(study: StudyCreate):
    """Create a new study"""
    global study_counter
    
    study_id = study_counter
    study_counter += 1
    
    study_data = {
        "id": study_id,
        "name": study.name,
        "description": study.description,
        "duration_days": study.duration_days,
        "status": study.status,
        "forms": study.forms,
        "created_by": 1,  # TODO: Get from JWT token
        "created_at": datetime.now(),
        "form_count": len(study.forms),
        "participant_count": 0
    }
    
    studies_db[study_id] = study_data
    
    print(f"✅ Created study: {study_data}")
    
    return StudyResponse(**study_data)

@router.get("/studies", response_model=dict)
async def list_studies():
    """Get all studies"""
    studies_list = list(studies_db.values())
    return {"studies": studies_list}

@router.get("/studies/{study_id}", response_model=StudyResponse)
async def get_study(study_id: int):
    """Get study by ID"""
    if study_id not in studies_db:
        raise HTTPException(status_code=404, detail="Study not found")
    
    return StudyResponse(**studies_db[study_id])

@router.put("/studies/{study_id}", response_model=StudyResponse)
async def update_study(study_id: int, study: StudyCreate):
    """Update study"""
    if study_id not in studies_db:
        raise HTTPException(status_code=404, detail="Study not found")
    
    study_data = studies_db[study_id]
    study_data.update({
        "name": study.name,
        "description": study.description,
        "duration_days": study.duration_days,
        "status": study.status,
        "forms": study.forms,
        "form_count": len(study.forms)
    })
    
    return StudyResponse(**study_data)

@router.delete("/studies/{study_id}")
async def delete_study(study_id: int):
    """Delete study"""
    if study_id not in studies_db:
        raise HTTPException(status_code=404, detail="Study not found")
    
    del studies_db[study_id]
    return {"message": "Study deleted successfully"}