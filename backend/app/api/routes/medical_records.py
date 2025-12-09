# Medical records API routes
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    MedicalRecordCreate,
    MedicalRecordUpdate,
    MedicalRecordResponse,
    MedicalRecordList
)
from app.models import User, MedicalRecord
from app.api.deps import get_current_active_user

router = APIRouter(prefix="/api/records", tags=["Medical Records"])


@router.post("", response_model=MedicalRecordResponse, status_code=status.HTTP_201_CREATED)
def create_medical_record(
    record_data: MedicalRecordCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Create a new medical record"""
    db_record = MedicalRecord(
        user_id=current_user.id,
        title=record_data.title,
        original_text=record_data.original_text,
        record_type=record_data.record_type
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.get("", response_model=List[MedicalRecordList])
def list_medical_records(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = 0,
    limit: int = 100
):
    """List all medical records for the current user"""
    records = db.query(MedicalRecord).filter(
        MedicalRecord.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    # Transform to list view
    return [
        MedicalRecordList(
            id=record.id,
            title=record.title,
            record_type=record.record_type,
            created_at=record.created_at,
            has_translation=record.translated_text is not None,
            has_suggestions=record.lifestyle_suggestions is not None
        )
        for record in records
    ]


@router.get("/{record_id}", response_model=MedicalRecordResponse)
def get_medical_record(
    record_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Get a specific medical record"""
    record = db.query(MedicalRecord).filter(
        MedicalRecord.id == record_id,
        MedicalRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found"
        )
    
    return record


@router.put("/{record_id}", response_model=MedicalRecordResponse)
def update_medical_record(
    record_id: int,
    record_data: MedicalRecordUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Update a medical record"""
    record = db.query(MedicalRecord).filter(
        MedicalRecord.id == record_id,
        MedicalRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found"
        )
    
    # Update fields
    update_data = record_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    
    # Clear cached AI data if original text changed
    if "original_text" in update_data:
        record.translated_text = None
        record.lifestyle_suggestions = None
    
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medical_record(
    record_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Delete a medical record"""
    record = db.query(MedicalRecord).filter(
        MedicalRecord.id == record_id,
        MedicalRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found"
        )
    
    db.delete(record)
    db.commit()
    return None
