# Training image database model
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class TrainingImage(Base):
    """Training image model for storing OCR training data"""
    __tablename__ = "training_images"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for admin uploads
    image_data = Column(Text, nullable=False)  # Base64 encoded image
    extracted_text = Column(Text, nullable=True)  # OCR extracted text
    corrected_text = Column(Text, nullable=True)  # Human-corrected version (for training feedback)
    ocr_confidence = Column(Float, nullable=True)  # Confidence score from OCR (0.0 - 1.0)
    image_type = Column(String, default="printed")  # Types: handwritten, printed, mixed
    is_training_data = Column(Boolean, default=False)  # Flag for curated training examples
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<TrainingImage(id={self.id}, type='{self.image_type}', confidence={self.ocr_confidence})>"
