# Medical record database model
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class MedicalRecord(Base):
    """Medical record model for storing patient medical data"""
    __tablename__ = "medical_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    original_text = Column(Text, nullable=False)
    image_data = Column(Text, nullable=True)  # Base64 encoded image data
    ocr_confidence = Column(Integer, nullable=True)  # OCR confidence score (0-100)
    ocr_extracted_text = Column(Text, nullable=True)  # Original OCR output before user edits
    translated_text = Column(Text, nullable=True)  # Cached AI translation
    lifestyle_suggestions = Column(Text, nullable=True)  # Cached AI suggestions
    record_type = Column(String, default="doctor_note")  # doctor_note, lab_result, prescription, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to user
    user = relationship("User", back_populates="medical_records")
