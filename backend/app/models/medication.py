# Medication database model
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Medication(Base):
    """Medication model for storing medication data and training information"""
    __tablename__ = "medications"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    url = Column(String, nullable=True)  # Source URL (e.g., from drugs.com)
    uses = Column(Text, nullable=True)  # Medical uses/indications
    side_effects = Column(Text, nullable=True)  # Known adverse reactions
    discontinued = Column(Boolean, default=False, nullable=False)
    discontinuation_reason = Column(Text, nullable=True)  # Why medication was discontinued
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Medication(name='{self.name}', discontinued={self.discontinued})>"
