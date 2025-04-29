#!/usr/bin/env python3
"""
Database Manager Module
Handles database operations for the Smart Desktop Activity Tracker
"""

import os
import json
import time
from datetime import datetime, timedelta
import sqlalchemy.exc
from sqlalchemy.orm import sessionmaker

from models import init_db, User, Screenshot, ActivityLog, AutomationTask, AutomationSuggestion
from utils import setup_logging

# Setup logging
logger = setup_logging()

class DBManager:
    """
    Database manager class for handling database operations
    """
    def __init__(self):
        """Initialize the database manager"""
        try:
            # Initialize database
            self.engine = init_db()
            self.Session = sessionmaker(bind=self.engine)
            
            # Create a default user if one doesn't exist
            self._ensure_default_user()
            
            logger.info("Database manager initialized")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def _ensure_default_user(self):
        """Ensure that a default user exists in the database"""
        session = self.Session()
        try:
            # Check if default user exists
            default_user = session.query(User).filter_by(username='default').first()
            
            if not default_user:
                # Create default user
                default_user = User(
                    username='default',
                    email='default@example.com',
                    settings={
                        'keyboard_privacy_mode': True,
                        'screenshot_interval': 1
                    }
                )
                session.add(default_user)
                session.commit()
                logger.info("Created default user")
        except Exception as e:
            session.rollback()
            logger.error(f"Error ensuring default user: {e}")
        finally:
            session.close()
    
    def get_default_user_id(self):
        """Get the ID of the default user"""
        session = self.Session()
        try:
            default_user = session.query(User).filter_by(username='default').first()
            return default_user.id if default_user else None
        except Exception as e:
            logger.error(f"Error getting default user ID: {e}")
            return None
        finally:
            session.close()
    
    def save_screenshot(self, file_path, window_title=None, application_name=None, extracted_text=None, thumbnail_path=None, resolution=None):
        """
        Save a screenshot record to the database
        
        Args:
            file_path (str): Path to the screenshot file
            window_title (str, optional): Title of the active window
            application_name (str, optional): Name of the active application
            extracted_text (str, optional): Text extracted from the screenshot
            thumbnail_path (str, optional): Path to a thumbnail of the screenshot
            resolution (str, optional): Resolution of the screenshot
        
        Returns:
            int: ID of the created screenshot record, or None on failure
        """
        session = self.Session()
        try:
            user_id = self.get_default_user_id()
            if not user_id:
                logger.error("No default user found for saving screenshot")
                return None
            
            screenshot = Screenshot(
                user_id=user_id,
                file_path=file_path,
                window_title=window_title,
                application_name=application_name,
                extracted_text=extracted_text,
                thumbnail_path=thumbnail_path,
                resolution=resolution
            )
            
            session.add(screenshot)
            session.commit()
            
            return screenshot.id
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving screenshot: {e}")
            return None
        finally:
            session.close()
    
    def update_screenshot(self, screenshot_id, **kwargs):
        """
        Update a screenshot record with new data
        
        Args:
            screenshot_id (int): ID of the screenshot to update
            **kwargs: Fields to update
        
        Returns:
            bool: Success status
        """
        session = self.Session()
        try:
            screenshot = session.query(Screenshot).get(screenshot_id)
            if not screenshot:
                logger.error(f"Screenshot with ID {screenshot_id} not found")
                return False
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(screenshot, key):
                    setattr(screenshot, key, value)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating screenshot: {e}")
            return False
        finally:
            session.close()
    
    def log_activity(self, activity_type, description=None, screenshot_id=None, data=None):
        """
        Log a user activity
        
        Args:
            activity_type (str): Type of activity (keyboard, mouse_click, window_change, automation)
            description (str, optional): Description of the activity
            screenshot_id (int, optional): ID of a related screenshot
            data (dict, optional): Additional activity data
        
        Returns:
            int: ID of the created activity log, or None on failure
        """
        session = self.Session()
        try:
            user_id = self.get_default_user_id()
            if not user_id:
                logger.error("No default user found for logging activity")
                return None
            
            activity_log = ActivityLog(
                user_id=user_id,
                activity_type=activity_type,
                description=description,
                screenshot_id=screenshot_id,
                data=data
            )
            
            session.add(activity_log)
            session.commit()
            
            return activity_log.id
        except Exception as e:
            session.rollback()
            logger.error(f"Error logging activity: {e}")
            return None
        finally:
            session.close()
    
    def save_automation_task(self, name, steps, description=None, triggers=None):
        """
        Save an automation task
        
        Args:
            name (str): Name of the automation task
            steps (list): List of steps to perform
            description (str, optional): Description of the automation
            triggers (list, optional): List of triggers for the automation
        
        Returns:
            int: ID of the created automation task, or None on failure
        """
        session = self.Session()
        try:
            user_id = self.get_default_user_id()
            if not user_id:
                logger.error("No default user found for saving automation task")
                return None
            
            automation_task = AutomationTask(
                user_id=user_id,
                name=name,
                description=description,
                steps=steps,
                triggers=triggers,
                is_active=True
            )
            
            session.add(automation_task)
            session.commit()
            
            return automation_task.id
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving automation task: {e}")
            return None
        finally:
            session.close()
    
    def update_automation_execution(self, task_id):
        """
        Update an automation task's execution count and last executed time
        
        Args:
            task_id (int): ID of the automation task
        
        Returns:
            bool: Success status
        """
        session = self.Session()
        try:
            task = session.query(AutomationTask).get(task_id)
            if not task:
                logger.error(f"Automation task with ID {task_id} not found")
                return False
            
            task.last_executed = datetime.now()
            task.execution_count += 1
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating automation execution: {e}")
            return False
        finally:
            session.close()
    
    def save_automation_suggestion(self, title, description=None, confidence=0.0, pattern_data=None):
        """
        Save an automation suggestion
        
        Args:
            title (str): Title of the suggestion
            description (str, optional): Description of the suggestion
            confidence (float, optional): Confidence score (0-1)
            pattern_data (dict, optional): Data about the detected pattern
        
        Returns:
            int: ID of the created suggestion, or None on failure
        """
        session = self.Session()
        try:
            user_id = self.get_default_user_id()
            if not user_id:
                logger.error("No default user found for saving automation suggestion")
                return None
            
            suggestion = AutomationSuggestion(
                user_id=user_id,
                title=title,
                description=description,
                confidence=confidence,
                pattern_data=pattern_data
            )
            
            session.add(suggestion)
            session.commit()
            
            return suggestion.id
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving automation suggestion: {e}")
            return None
        finally:
            session.close()
    
    def get_recent_activities(self, limit=50):
        """
        Get recent activity logs
        
        Args:
            limit (int, optional): Maximum number of records to return
        
        Returns:
            list: List of activity logs, or empty list on failure
        """
        session = self.Session()
        try:
            activities = session.query(ActivityLog).order_by(ActivityLog.timestamp.desc()).limit(limit).all()
            
            # Convert to dictionaries
            result = []
            for activity in activities:
                activity_dict = {
                    'id': activity.id,
                    'timestamp': activity.timestamp,
                    'activity_type': activity.activity_type,
                    'description': activity.description,
                    'screenshot_id': activity.screenshot_id,
                    'data': activity.data
                }
                result.append(activity_dict)
            
            return result
        except Exception as e:
            logger.error(f"Error getting recent activities: {e}")
            return []
        finally:
            session.close()
    
    def get_automation_tasks(self):
        """
        Get all automation tasks
        
        Returns:
            list: List of automation tasks, or empty list on failure
        """
        session = self.Session()
        try:
            tasks = session.query(AutomationTask).filter_by(is_active=True).all()
            
            # Convert to dictionaries
            result = []
            for task in tasks:
                task_dict = {
                    'id': task.id,
                    'name': task.name,
                    'description': task.description,
                    'created_at': task.created_at,
                    'last_executed': task.last_executed,
                    'execution_count': task.execution_count,
                    'steps': task.steps,
                    'triggers': task.triggers
                }
                result.append(task_dict)
            
            return result
        except Exception as e:
            logger.error(f"Error getting automation tasks: {e}")
            return []
        finally:
            session.close()
    
    def get_automation_suggestions(self, include_dismissed=False):
        """
        Get automation suggestions
        
        Args:
            include_dismissed (bool, optional): Whether to include dismissed suggestions
        
        Returns:
            list: List of automation suggestions, or empty list on failure
        """
        session = self.Session()
        try:
            query = session.query(AutomationSuggestion)
            if not include_dismissed:
                query = query.filter_by(is_dismissed=False)
            
            suggestions = query.order_by(AutomationSuggestion.confidence.desc()).all()
            
            # Convert to dictionaries
            result = []
            for suggestion in suggestions:
                suggestion_dict = {
                    'id': suggestion.id,
                    'title': suggestion.title,
                    'description': suggestion.description,
                    'created_at': suggestion.created_at,
                    'confidence': suggestion.confidence,
                    'is_dismissed': suggestion.is_dismissed,
                    'is_implemented': suggestion.is_implemented,
                    'pattern_data': suggestion.pattern_data
                }
                result.append(suggestion_dict)
            
            return result
        except Exception as e:
            logger.error(f"Error getting automation suggestions: {e}")
            return []
        finally:
            session.close()
    
    def dismiss_suggestion(self, suggestion_id):
        """
        Mark a suggestion as dismissed
        
        Args:
            suggestion_id (int): ID of the suggestion
        
        Returns:
            bool: Success status
        """
        session = self.Session()
        try:
            suggestion = session.query(AutomationSuggestion).get(suggestion_id)
            if not suggestion:
                logger.error(f"Automation suggestion with ID {suggestion_id} not found")
                return False
            
            suggestion.is_dismissed = True
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error dismissing suggestion: {e}")
            return False
        finally:
            session.close()
    
    def implement_suggestion(self, suggestion_id):
        """
        Mark a suggestion as implemented
        
        Args:
            suggestion_id (int): ID of the suggestion
        
        Returns:
            bool: Success status
        """
        session = self.Session()
        try:
            suggestion = session.query(AutomationSuggestion).get(suggestion_id)
            if not suggestion:
                logger.error(f"Automation suggestion with ID {suggestion_id} not found")
                return False
            
            suggestion.is_implemented = True
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error implementing suggestion: {e}")
            return False
        finally:
            session.close()
    
    def cleanup_old_data(self, days=7):
        """
        Clean up old screenshots and activity logs
        
        Args:
            days (int, optional): Number of days to keep data
        
        Returns:
            int: Number of deleted records
        """
        session = self.Session()
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Get screenshots to delete
            old_screenshots = session.query(Screenshot).filter(Screenshot.timestamp < cutoff_date).all()
            
            # Collect screenshot IDs for activity log cleanup
            screenshot_ids = [s.id for s in old_screenshots]
            
            # Delete activity logs associated with the screenshots
            activities_deleted = 0
            if screenshot_ids:
                activities_deleted = session.query(ActivityLog).filter(ActivityLog.screenshot_id.in_(screenshot_ids)).delete(synchronize_session=False)
            
            # Delete old activity logs regardless of screenshot association
            activities_deleted += session.query(ActivityLog).filter(ActivityLog.timestamp < cutoff_date).delete(synchronize_session=False)
            
            # Delete old screenshots
            screenshots_deleted = 0
            for screenshot in old_screenshots:
                # Try to delete the actual file
                try:
                    if os.path.exists(screenshot.file_path):
                        os.remove(screenshot.file_path)
                    
                    if screenshot.thumbnail_path and os.path.exists(screenshot.thumbnail_path):
                        os.remove(screenshot.thumbnail_path)
                except Exception as e:
                    logger.warning(f"Error deleting screenshot file: {e}")
                
                # Mark for deletion from database
                session.delete(screenshot)
                screenshots_deleted += 1
            
            session.commit()
            
            total_deleted = activities_deleted + screenshots_deleted
            logger.info(f"Cleaned up {activities_deleted} activity logs and {screenshots_deleted} screenshots")
            
            return total_deleted
        except Exception as e:
            session.rollback()
            logger.error(f"Error cleaning up old data: {e}")
            return 0
        finally:
            session.close()
    
    def close(self):
        """Close the database session"""
        try:
            self.engine.dispose()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")

# Singleton instance
db_manager = DBManager()