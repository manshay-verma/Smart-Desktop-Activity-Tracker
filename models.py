#!/usr/bin/env python3
"""
Database Models
Defines database models for the Smart Desktop Activity Tracker
"""

import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.schema import MetaData
from sqlalchemy.dialects.postgresql import JSONB

# Create a base class for declarative class definitions
Base = declarative_base()

# Define models
class User(Base):
    """User model"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    last_active = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    settings = Column(JSONB, default={})
    
    # Relationships
    screenshots = relationship("Screenshot", back_populates="user", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
    automation_tasks = relationship("AutomationTask", back_populates="user", cascade="all, delete-orphan")
    automation_suggestions = relationship("AutomationSuggestion", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

class Screenshot(Base):
    """Screenshot model"""
    __tablename__ = 'screenshots'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    file_path = Column(String(255), nullable=False)
    thumbnail_path = Column(String(255))
    resolution = Column(String(50))
    window_title = Column(String(255))
    application_name = Column(String(100))
    extracted_text = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="screenshots")
    activity_logs = relationship("ActivityLog", back_populates="screenshot")
    
    def __repr__(self):
        return f"<Screenshot(id={self.id}, timestamp='{self.timestamp}')>"

class ActivityLog(Base):
    """Activity Log model"""
    __tablename__ = 'activity_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    activity_type = Column(String(50), nullable=False)
    description = Column(Text)
    screenshot_id = Column(Integer, ForeignKey('screenshots.id'))
    data = Column(JSONB)
    
    # Relationships
    user = relationship("User", back_populates="activity_logs")
    screenshot = relationship("Screenshot", back_populates="activity_logs")
    
    def __repr__(self):
        return f"<ActivityLog(id={self.id}, type='{self.activity_type}')>"

class AutomationTask(Base):
    """Automation Task model"""
    __tablename__ = 'automation_tasks'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    last_executed = Column(DateTime)
    execution_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    steps = Column(JSONB, nullable=False)
    triggers = Column(JSONB)
    
    # Relationships
    user = relationship("User", back_populates="automation_tasks")
    
    def __repr__(self):
        return f"<AutomationTask(id={self.id}, name='{self.name}')>"

class AutomationSuggestion(Base):
    """Automation Suggestion model"""
    __tablename__ = 'automation_suggestions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    confidence = Column(Float, default=0.0)
    is_dismissed = Column(Boolean, default=False)
    is_implemented = Column(Boolean, default=False)
    pattern_data = Column(JSONB)
    
    # Relationships
    user = relationship("User", back_populates="automation_suggestions")
    
    def __repr__(self):
        return f"<AutomationSuggestion(id={self.id}, title='{self.title}')>"

# Database setup function
def init_db():
    """Initialize the database connection and create tables if they don't exist"""
    # Get database URL from environment variable
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    # Create database engine
    engine = create_engine(database_url)
    
    # Create tables
    Base.metadata.create_all(engine)
    print("Database tables created successfully")
    
    return engine

# For testing purposes
if __name__ == "__main__":
    engine = init_db()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Create a test user
    test_user = User(
        username="test_user",
        email="test@example.com",
        settings={"theme": "dark", "notifications": True}
    )
    
    session.add(test_user)
    session.commit()
    
    print(f"Created test user with ID: {test_user.id}")
    
    session.close()