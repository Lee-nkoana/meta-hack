# Knowledge Base Pydantic schemas
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class KnowledgeCreate(BaseModel):
    """Schema for creating a knowledge entry"""
    title: str
    content: str
    source: Optional[str] = None


class KnowledgeResponse(BaseModel):
    """Schema for knowledge entry response"""
    id: int
    title: str
    content: str
    source: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
