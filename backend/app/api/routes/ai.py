# AI-powered API routes for medical text translation and suggestions
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, MedicalRecord
from app.api.deps import get_current_active_user
from app.services.ai_service import ai_service

router = APIRouter(prefix="/api/ai", tags=["AI Services"])


class TranslateRequest(BaseModel):
    """Request schema for text translation"""
    text: str


class SuggestionsRequest(BaseModel):
    """Request schema for lifestyle suggestions"""
    condition: str


class AIResponse(BaseModel):
    """Response schema for AI operations"""
    result: str | None
    cached: bool = False


@router.post("/translate", response_model=AIResponse)
async def translate_medical_text(
    request: TranslateRequest,
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """Translate medical text to layman's terms on-demand"""
    if not ai_service.api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not configured. Please set META_AI_API_KEY in environment variables."
        )
    
    translation = await ai_service.translate_medical_text(request.text)
    
    if translation is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to translate medical text. Please try again."
        )
    
    return AIResponse(result=translation, cached=False)


@router.post("/suggestions", response_model=AIResponse)
async def get_lifestyle_suggestions(
    request: SuggestionsRequest,
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """Get lifestyle suggestions for a medical condition on-demand"""
    if not ai_service.api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not configured. Please set META_AI_API_KEY in environment variables."
        )
    
    suggestions = await ai_service.generate_lifestyle_suggestions(request.condition)
    
    if suggestions is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate lifestyle suggestions. Please try again."
        )
    
    return AIResponse(result=suggestions, cached=False)


@router.post("/explain/{record_id}")
async def explain_medical_record(
    record_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    force_refresh: bool = False
):
    """Get AI explanation and suggestions for a specific medical record"""
    # Get the medical record
    record = db.query(MedicalRecord).filter(
        MedicalRecord.id == record_id,
        MedicalRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found"
        )
    
    # Check if we have cached results and force_refresh is False
    if not force_refresh and record.translated_text and record.lifestyle_suggestions:
        return {
            "translation": record.translated_text,
            "suggestions": record.lifestyle_suggestions,
            "cached": True
        }
    
    # Check if AI service is configured
    if not ai_service.api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not configured. Please set META_AI_API_KEY in environment variables."
        )
    
    # Get AI explanations
    result = await ai_service.explain_medical_record(record.original_text, record.record_type)
    
    # Cache the results
    if result["translation"]:
        record.translated_text = result["translation"]
    if result["suggestions"]:
        record.lifestyle_suggestions = result["suggestions"]
    
    db.commit()
    db.refresh(record)
    
    return {
        "translation": result["translation"],
        "suggestions": result["suggestions"],
        "cached": False
    }
