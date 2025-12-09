# User profile and dashboard API routes
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserProfile, UserUpdate, UserResponse
from app.models import User, MedicalRecord
from app.api.deps import get_current_active_user
from app.utils.security import get_password_hash

router = APIRouter(prefix="/api/users", tags=["Users"])


class DashboardStats(BaseModel):
    """Dashboard statistics response"""
    total_records: int
    records_with_translation: int
    records_with_suggestions: int
    recent_records: list


@router.get("/me", response_model=UserProfile)
def get_user_profile(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Get current user profile with statistics"""
    record_count = db.query(MedicalRecord).filter(
        MedicalRecord.user_id == current_user.id
    ).count()
    
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        record_count=record_count
    )


@router.put("/me", response_model=UserResponse)
def update_user_profile(
    user_data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Update current user profile"""
    update_data = user_data.model_dump(exclude_unset=True)
    
    # Check if email is being updated and if it's already taken
    if "email" in update_data:
        existing_user = db.query(User).filter(
            User.email == update_data["email"],
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Handle password update separately
    if "password" in update_data:
        current_user.hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
    
    # Update other fields
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Get dashboard statistics for the current user"""
    # Get all records for the user
    all_records = db.query(MedicalRecord).filter(
        MedicalRecord.user_id == current_user.id
    ).all()
    
    total_records = len(all_records)
    records_with_translation = sum(1 for r in all_records if r.translated_text)
    records_with_suggestions = sum(1 for r in all_records if r.lifestyle_suggestions)
    
    # Get recent records (last 5)
    recent_records_query = db.query(MedicalRecord).filter(
        MedicalRecord.user_id == current_user.id
    ).order_by(MedicalRecord.created_at.desc()).limit(5).all()
    
    recent_records = [
        {
            "id": record.id,
            "title": record.title,
            "record_type": record.record_type,
            "created_at": record.created_at.isoformat(),
            "has_translation": record.translated_text is not None,
            "has_suggestions": record.lifestyle_suggestions is not None
        }
        for record in recent_records_query
    ]
    
    return DashboardStats(
        total_records=total_records,
        records_with_translation=records_with_translation,
        records_with_suggestions=records_with_suggestions,
        recent_records=recent_records
    )
