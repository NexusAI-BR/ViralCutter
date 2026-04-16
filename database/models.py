from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    path = Column(String, nullable=False)
    url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String, default='idle') # idle, processing, completed, error
    workflow = Column(String)
    video_path = Column(String)
    
    # Configuration used for this project
    config = Column(JSON)
    
    segments = relationship("Segment", back_populates="project", cascade="all, delete-orphan")

class Segment(Base):
    __tablename__ = 'segments'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    title = Column(String)
    start_time = Column(Float)
    end_time = Column(Float)
    duration = Column(Float)
    score = Column(Integer)
    hook = Column(Text)
    reasoning = Column(Text)
    
    # Paths to generated files
    raw_cut_path = Column(String)
    final_cut_path = Column(String)
    subtitle_json_path = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="segments")

class AppConfig(Base):
    __tablename__ = 'app_config'
    
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(JSON)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
