from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class CaseStatus(str, enum.Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    PENDING = "pending"

class Case(Base):
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(Enum(CaseStatus), default=CaseStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())