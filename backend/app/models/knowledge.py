# Knowledge Base database model
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class KnowledgeBase(Base):
    """Model for storing medical knowledge for RAG"""
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    source = Column(String)  # URL or source description
    created_at = Column(DateTime(timezone=True), server_default=func.now())
