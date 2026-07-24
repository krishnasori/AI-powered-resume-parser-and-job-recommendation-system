from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class ResumeParse(Base):
    __tablename__ = "resume_parses"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    extracted_skills = Column(Text) # Will store JSON string of skills
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Tomorrow we will link this to the User table!