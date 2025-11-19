"""
Designer API - Production-Grade Study Lifecycle Management
Implements proper CRUD with status-based editing permissions
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Database imports
from database import (
    get_db,
    create_study,
    get_study,
    get_all_studies,
    Study
)

# Create router with /api/v1/designer prefix
router = APIRouter(prefix="/api/v1/designer", tags=["designer"])

# ==================== PYDANTIC MODELS ====================

class StudyCreateRequest(BaseModel):
    """Request model for creating a new study"""
    name: str
    description: Optional[str] = ""

class StudyUpdateRequest(BaseModel):
    """Request model for updating a study"""
    name: Optional[str] = None
    description: Optional[str] = None

class StudyResponse(BaseModel):
    """Response model for study data"""
    id: int
    name: str
    description: str
    status: str
    created_at: datetime
    form_count: int
    
    class Config:
        from_attributes = True

# ==================== ENDPOINTS ====================

@router.post("/studies", response_model=dict)
async def create_study_endpoint(study: StudyCreateRequest, db = Depends(get_db)):
    """
    Create a new study in 'draft' status.
    Draft studies can be edited freely.
    """
    new_study = create_study(
        db, 
        name=study.name, 
        description=study.description or ""
    )
    
    # Set status to draft (should be default, but ensure it)
    new_study.status = 'draft'
    db.commit()
    db.refresh(new_study)
    
    return {
        "success": True,
        "message": "Study created in draft mode",
        "study": {
            "id": new_study.id,
            "name": new_study.name,
            "description": new_study.description,
            "status": new_study.status,
            "created_at": new_study.created_at.isoformat(),
            "form_count": len(new_study.forms)
        }
    }

@router.get("/studies", response_model=dict)
async def list_studies(
    status: Optional[str] = None,
    db = Depends(get_db)
):
    """
    Get all studies, optionally filtered by status.
    
    Query params:
        status: 'draft', 'active', or 'archived' (optional)
    """
    studies = get_all_studies(db)
    
    # Filter by status if provided
    if status:
        studies = [s for s in studies if s.status == status]
    
    return {
        "success": True,
        "count": len(studies),
        "studies": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "status": s.status,
                "created_at": s.created_at.isoformat(),
                "form_count": len(s.forms)
            }
            for s in studies
        ]
    }

@router.get("/studies/{study_id}", response_model=dict)
async def get_study_details(study_id: int, db = Depends(get_db)):
    """Get detailed information about a specific study"""
    study = get_study(db, study_id)
    
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")
    
    return {
        "success": True,
        "study": {
            "id": study.id,
            "name": study.name,
            "description": study.description,
            "status": study.status,
            "created_at": study.created_at.isoformat(),
            "forms": [
                {
                    "id": f.id,
                    "form_id": f.form_id,
                    "title": f.title,
                    "frequency": f.frequency,
                    "created_at": f.created_at.isoformat()
                }
                for f in study.forms
            ],
            "form_count": len(study.forms),
            "can_edit": study.status == 'draft',
            "can_activate": study.status == 'draft' and len(study.forms) > 0,
            "can_archive": study.status in ['draft', 'active']
        }
    }

@router.put("/studies/{study_id}", response_model=dict)
async def update_study(
    study_id: int, 
    updates: StudyUpdateRequest, 
    db = Depends(get_db)
):
    """
    Update a study's details.
    Only allowed if study is in 'draft' status.
    """
    study = get_study(db, study_id)
    
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")
    
    # Check if study can be edited
    if study.status != 'draft':
        raise HTTPException(
            status_code=403, 
            detail=f"Cannot edit study in '{study.status}' status. Only 'draft' studies can be edited."
        )
    
    # Apply updates
    if updates.name is not None:
        study.name = updates.name
    if updates.description is not None:
        study.description = updates.description
    
    db.commit()
    db.refresh(study)
    
    return {
        "success": True,
        "message": "Study updated successfully",
        "study": {
            "id": study.id,
            "name": study.name,
            "description": study.description,
            "status": study.status,
            "created_at": study.created_at.isoformat(),
            "form_count": len(study.forms)
        }
    }

@router.post("/studies/{study_id}/activate", response_model=dict)
async def activate_study(study_id: int, db = Depends(get_db)):
    """
    Activate a study, locking it for editing.
    Use this when first subject enrolls.
    """
    study = get_study(db, study_id)
    
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")
    
    if study.status != 'draft':
        raise HTTPException(
            status_code=400,
            detail=f"Cannot activate study in '{study.status}' status"
        )
    
    if len(study.forms) == 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot activate study with no forms"
        )
    
    # Activate the study
    study.status = 'active'
    db.commit()
    db.refresh(study)
    
    return {
        "success": True,
        "message": "Study activated and locked for editing",
        "study": {
            "id": study.id,
            "name": study.name,
            "status": study.status,
            "form_count": len(study.forms)
        }
    }

@router.delete("/studies/{study_id}", response_model=dict)
async def archive_study(study_id: int, db = Depends(get_db)):
    """
    Soft delete (archive) a study.
    Archived studies are hidden but data is preserved.
    """
    study = get_study(db, study_id)
    
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")
    
    if study.status == 'archived':
        raise HTTPException(
            status_code=400,
            detail="Study is already archived"
        )
    
    # Soft delete - just change status
    study.status = 'archived'
    db.commit()
    db.refresh(study)
    
    return {
        "success": True,
        "message": "Study archived successfully",
        "study": {
            "id": study.id,
            "name": study.name,
            "status": study.status
        }
    }

@router.post("/studies/{study_id}/restore", response_model=dict)
async def restore_study(study_id: int, db = Depends(get_db)):
    """
    Restore an archived study back to draft status.
    """
    study = get_study(db, study_id)
    
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")
    
    if study.status != 'archived':
        raise HTTPException(
            status_code=400,
            detail="Only archived studies can be restored"
        )
    
    # Restore to draft
    study.status = 'draft'
    db.commit()
    db.refresh(study)
    
    return {
        "success": True,
        "message": "Study restored to draft status",
        "study": {
            "id": study.id,
            "name": study.name,
            "status": study.status
        }
    }

# ==================== HELPER ENDPOINT ====================

@router.get("/studies/{study_id}/permissions", response_model=dict)
async def get_study_permissions(study_id: int, db = Depends(get_db)):
    """
    Get what actions are allowed for this study based on status.
    Useful for frontend to show/hide buttons.
    """
    study = get_study(db, study_id)
    
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")
    
    permissions = {
        "can_view": True,  # Always can view
        "can_edit": study.status == 'draft',
        "can_activate": study.status == 'draft' and len(study.forms) > 0,
        "can_archive": study.status in ['draft', 'active'],
        "can_restore": study.status == 'archived',
        "can_add_forms": study.status == 'draft',
        "can_enroll_subjects": study.status == 'active'
    }
    
    return {
        "success": True,
        "study_id": study_id,
        "status": study.status,
        "permissions": permissions,
        "reason": {
            "draft": "Study is in draft mode - full editing allowed",
            "active": "Study is active - locked to protect data integrity",
            "archived": "Study is archived - read-only"
        }.get(study.status, "Unknown status")
    }
