"""
Database Models for Smart Desktop Activity Tracker
Defines SQLAlchemy models for storing user activity data
"""

import os
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# Get database URL from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


class User(Base):
    """User model for storing user information"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    last_active = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    settings = Column(JSON, nullable=True)
    
    # Relationships
    screenshots = relationship("Screenshot", back_populates="user", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
    automation_tasks = relationship("AutomationTask", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Screenshot(Base):
    """Screenshot model for storing captured screenshots"""
    __tablename__ = 'screenshots'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    file_path = Column(String(255), nullable=False)
    thumbnail_path = Column(String(255), nullable=True)
    resolution = Column(String(20), nullable=True)  # Format: "WIDTHxHEIGHT"
    window_title = Column(String(255), nullable=True)
    application_name = Column(String(100), nullable=True)
    extracted_text = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="screenshots")
    activity_logs = relationship("ActivityLog", back_populates="screenshot")
    
    def __repr__(self):
        return f"<Screenshot(id={self.id}, timestamp='{self.timestamp}')>"


class ActivityLog(Base):
    """Activity log model for storing user actions"""
    __tablename__ = 'activity_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    activity_type = Column(String(50), nullable=False)  # keyboard, mouse_click, window_change, automation
    description = Column(Text, nullable=True)
    screenshot_id = Column(Integer, ForeignKey('screenshots.id'), nullable=True)
    data = Column(JSON, nullable=True)  # Store additional activity-specific data
    
    # Relationships
    user = relationship("User", back_populates="activity_logs")
    screenshot = relationship("Screenshot", back_populates="activity_logs")
    
    def __repr__(self):
        return f"<ActivityLog(id={self.id}, type='{self.activity_type}', timestamp='{self.timestamp}')>"


class AutomationTask(Base):
    """Automation task model for storing recorded automations"""
    __tablename__ = 'automation_tasks'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    last_executed = Column(DateTime, nullable=True)
    execution_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    steps = Column(JSON, nullable=False)  # List of steps to execute
    triggers = Column(JSON, nullable=True)  # Conditions that trigger the automation
    
    # Relationships
    user = relationship("User", back_populates="automation_tasks")
    
    def __repr__(self):
        return f"<AutomationTask(id={self.id}, name='{self.name}')>"


class AutomationSuggestion(Base):
    """Automation suggestion model for storing suggested automations"""
    __tablename__ = 'automation_suggestions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    confidence = Column(Float, default=0.0)  # Confidence score (0-1)
    pattern_data = Column(JSON, nullable=True)  # Data about the detected pattern
    is_dismissed = Column(Boolean, default=False)
    is_implemented = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<AutomationSuggestion(id={self.id}, title='{self.title}')>"


class Setting(Base):
    """Settings model for storing application settings"""
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    key = Column(String(50), nullable=False)
    value = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Setting(id={self.id}, key='{self.key}')>"


# Create engine and session factory
if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
else:
    engine = None
    Session = None
    session = None


def init_db():
    """Initialize the database by creating all tables"""
    if engine:
        Base.metadata.create_all(engine)
        print("Database tables created successfully")
    else:
        print("Database URL not found. Tables not created.")


# Helper function to get a new session
def get_session():
    """Get a new database session"""
    if Session:
        return Session()
    return None