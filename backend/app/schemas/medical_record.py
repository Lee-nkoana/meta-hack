# Medical record Pydantic schemas
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MedicalRecordBase(BaseModel):
    """Base medical record schema"""
    title: str = Field(..., min_length=1, max_length=200)
    original_text: str = Field(..., min_length=1)
    record_type: Optional[str] = "doctor_note"


class MedicalRecordCreate(MedicalRecordBase):
    """Schema for creating a new medical record"""
    pass


class MedicalRecordUpdate(BaseModel):
    """Schema for updating a medical record"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    original_text: Optional[str] = Field(None, min_length=1)
    record_type: Optional[str] = None


class MedicalRecordResponse(MedicalRecordBase):
    """Schema for medical record response"""
    id: int
    user_id: int
    translated_text: Optional[str] = None
    lifestyle_suggestions: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MedicalRecordList(BaseModel):
    """Schema for medical record list view (summary)"""
    id: int
    title: str
    record_type: str
    created_at: datetime
    has_translation: bool = False
    has_suggestions: bool = False
    
    class Config:
        from_attributes = True
