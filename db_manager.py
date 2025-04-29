"""
Database Manager Module
Handles database operations for the Smart Desktop Activity Tracker
"""

import os
import logging
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from models import User, Screenshot, ActivityLog, AutomationTask, AutomationSuggestion, get_session, init_db
from utils import setup_logging

# Setup logging
logger = setup_logging()

class DBManager:
    """
    Database manager class for handling database operations
    """
    def __init__(self):
        """Initialize the database manager"""
        self.session = None
        try:
            # Initialize database tables
            init_db()
            
            # Get a session
            self.session = get_session()
            
            # Check if we have a default user, create if not
            self._ensure_default_user()
            
            logger.info("Database manager initialized")
        except SQLAlchemyError as e:
            logger.error(f"Database initialization error: {e}")
    
    def _ensure_default_user(self):
        """Ensure that a default user exists in the database"""
        if not self.session:
            logger.error("No database session available")
            return
        
        try:
            # Check if default user exists
            user = self.session.query(User).filter_by(username="default").first()
            if not user:
                # Create default user
                user = User(
                    username="default",
                    email="default@example.com",
                    settings={"keyboard_privacy_mode": True, "screenshot_interval": 1}
                )
                self.session.add(user)
                self.session.commit()
                logger.info("Created default user")
            
            # Return the user ID
            return user.id
        except SQLAlchemyError as e:
            logger.error(f"Error ensuring default user: {e}")
            self.session.rollback()
            return None
    
    def get_default_user_id(self):
        """Get the ID of the default user"""
        if not self.session:
            logger.error("No database session available")
            return None
        
        try:
            user = self.session.query(User).filter_by(username="default").first()
            return user.id if user else None
        except SQLAlchemyError as e:
            logger.error(f"Error getting default user: {e}")
            return None
    
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
        if not self.session:
            logger.error("No database session available")
            return None
        
        try:
            user_id = self.get_default_user_id()
            if not user_id:
                logger.error("No default user found")
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
            
            self.session.add(screenshot)
            self.session.commit()
            
            logger.debug(f"Saved screenshot: {screenshot.id}")
            return screenshot.id
        
        except SQLAlchemyError as e:
            logger.error(f"Error saving screenshot: {e}")
            self.session.rollback()
            return None
    
    def update_screenshot(self, screenshot_id, **kwargs):
        """
        Update a screenshot record with new data
        
        Args:
            screenshot_id (int): ID of the screenshot to update
            **kwargs: Fields to update
        
        Returns:
            bool: Success status
        """
        if not self.session:
            logger.error("No database session available")
            return False
        
        try:
            screenshot = self.session.query(Screenshot).filter_by(id=screenshot_id).first()
            if not screenshot:
                logger.error(f"Screenshot with ID {screenshot_id} not found")
                return False
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(screenshot, key):
                    setattr(screenshot, key, value)
            
            self.session.commit()
            logger.debug(f"Updated screenshot: {screenshot_id}")
            return True
        
        except SQLAlchemyError as e:
            logger.error(f"Error updating screenshot: {e}")
            self.session.rollback()
            return False
    
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
        if not self.session:
            logger.error("No database session available")
            return None
        
        try:
            user_id = self.get_default_user_id()
            if not user_id:
                logger.error("No default user found")
                return None
            
            activity_log = ActivityLog(
                user_id=user_id,
                activity_type=activity_type,
                description=description,
                screenshot_id=screenshot_id,
                data=data
            )
            
            self.session.add(activity_log)
            self.session.commit()
            
            logger.debug(f"Logged activity: {activity_log.id}")
            return activity_log.id
        
        except SQLAlchemyError as e:
            logger.error(f"Error logging activity: {e}")
            self.session.rollback()
            return None
    
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
        if not self.session:
            logger.error("No database session available")
            return None
        
        try:
            user_id = self.get_default_user_id()
            if not user_id:
                logger.error("No default user found")
                return None
            
            automation_task = AutomationTask(
                user_id=user_id,
                name=name,
                description=description,
                steps=steps,
                triggers=triggers
            )
            
            self.session.add(automation_task)
            self.session.commit()
            
            logger.debug(f"Saved automation task: {automation_task.id}")
            return automation_task.id
        
        except SQLAlchemyError as e:
            logger.error(f"Error saving automation task: {e}")
            self.session.rollback()
            return None
    
    def update_automation_execution(self, task_id):
        """
        Update an automation task's execution count and last executed time
        
        Args:
            task_id (int): ID of the automation task
        
        Returns:
            bool: Success status
        """
        if not self.session:
            logger.error("No database session available")
            return False
        
        try:
            task = self.session.query(AutomationTask).filter_by(id=task_id).first()
            if not task:
                logger.error(f"Automation task with ID {task_id} not found")
                return False
            
            task.execution_count += 1
            task.last_executed = datetime.now()
            
            self.session.commit()
            logger.debug(f"Updated automation execution: {task_id}")
            return True
        
        except SQLAlchemyError as e:
            logger.error(f"Error updating automation execution: {e}")
            self.session.rollback()
            return False
    
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
        if not self.session:
            logger.error("No database session available")
            return None
        
        try:
            user_id = self.get_default_user_id()
            if not user_id:
                logger.error("No default user found")
                return None
            
            suggestion = AutomationSuggestion(
                user_id=user_id,
                title=title,
                description=description,
                confidence=confidence,
                pattern_data=pattern_data
            )
            
            self.session.add(suggestion)
            self.session.commit()
            
            logger.debug(f"Saved automation suggestion: {suggestion.id}")
            return suggestion.id
        
        except SQLAlchemyError as e:
            logger.error(f"Error saving automation suggestion: {e}")
            self.session.rollback()
            return None
    
    def get_recent_activities(self, limit=50):
        """
        Get recent activity logs
        
        Args:
            limit (int, optional): Maximum number of records to return
        
        Returns:
            list: List of activity logs, or empty list on failure
        """
        if not self.session:
            logger.error("No database session available")
            return []
        
        try:
            user_id = self.get_default_user_id()
            if not user_id:
                logger.error("No default user found")
                return []
            
            activities = self.session.query(ActivityLog)\
                .filter_by(user_id=user_id)\
                .order_by(ActivityLog.timestamp.desc())\
                .limit(limit)\
                .all()
            
            return activities
        
        except SQLAlchemyError as e:
            logger.error(f"Error getting recent activities: {e}")
            return []
    
    def get_automation_tasks(self):
        """
        Get all automation tasks
        
        Returns:
            list: List of automation tasks, or empty list on failure
        """
        if not self.session:
            logger.error("No database session available")
            return []
        
        try:
            user_id = self.get_default_user_id()
            if not user_id:
                logger.error("No default user found")
                return []
            
            tasks = self.session.query(AutomationTask)\
                .filter_by(user_id=user_id)\
                .order_by(AutomationTask.created_at.desc())\
                .all()
            
            return tasks
        
        except SQLAlchemyError as e:
            logger.error(f"Error getting automation tasks: {e}")
            return []
    
    def get_automation_suggestions(self, include_dismissed=False):
        """
        Get automation suggestions
        
        Args:
            include_dismissed (bool, optional): Whether to include dismissed suggestions
        
        Returns:
            list: List of automation suggestions, or empty list on failure
        """
        if not self.session:
            logger.error("No database session available")
            return []
        
        try:
            user_id = self.get_default_user_id()
            if not user_id:
                logger.error("No default user found")
                return []
            
            query = self.session.query(AutomationSuggestion)\
                .filter_by(user_id=user_id)
            
            if not include_dismissed:
                query = query.filter_by(is_dismissed=False)
            
            suggestions = query.order_by(AutomationSuggestion.created_at.desc())\
                .all()
            
            return suggestions
        
        except SQLAlchemyError as e:
            logger.error(f"Error getting automation suggestions: {e}")
            return []
    
    def dismiss_suggestion(self, suggestion_id):
        """
        Mark a suggestion as dismissed
        
        Args:
            suggestion_id (int): ID of the suggestion
        
        Returns:
            bool: Success status
        """
        if not self.session:
            logger.error("No database session available")
            return False
        
        try:
            suggestion = self.session.query(AutomationSuggestion).filter_by(id=suggestion_id).first()
            if not suggestion:
                logger.error(f"Suggestion with ID {suggestion_id} not found")
                return False
            
            suggestion.is_dismissed = True
            
            self.session.commit()
            logger.debug(f"Dismissed suggestion: {suggestion_id}")
            return True
        
        except SQLAlchemyError as e:
            logger.error(f"Error dismissing suggestion: {e}")
            self.session.rollback()
            return False
    
    def implement_suggestion(self, suggestion_id):
        """
        Mark a suggestion as implemented
        
        Args:
            suggestion_id (int): ID of the suggestion
        
        Returns:
            bool: Success status
        """
        if not self.session:
            logger.error("No database session available")
            return False
        
        try:
            suggestion = self.session.query(AutomationSuggestion).filter_by(id=suggestion_id).first()
            if not suggestion:
                logger.error(f"Suggestion with ID {suggestion_id} not found")
                return False
            
            suggestion.is_implemented = True
            
            self.session.commit()
            logger.debug(f"Implemented suggestion: {suggestion_id}")
            return True
        
        except SQLAlchemyError as e:
            logger.error(f"Error implementing suggestion: {e}")
            self.session.rollback()
            return False
    
    def cleanup_old_data(self, days=7):
        """
        Clean up old screenshots and activity logs
        
        Args:
            days (int, optional): Number of days to keep data
        
        Returns:
            int: Number of deleted records
        """
        if not self.session:
            logger.error("No database session available")
            return 0
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Get screenshot IDs to delete
            screenshot_ids = [row[0] for row in self.session.query(Screenshot.id)
                            .filter(Screenshot.timestamp < cutoff_date)
                            .all()]
            
            # Delete related activity logs first
            deleted_logs = self.session.query(ActivityLog)\
                .filter(ActivityLog.screenshot_id.in_(screenshot_ids))\
                .delete(synchronize_session=False)
            
            # Delete screenshots
            deleted_screenshots = self.session.query(Screenshot)\
                .filter(Screenshot.timestamp < cutoff_date)\
                .delete(synchronize_session=False)
            
            # Delete old activity logs without screenshots
            deleted_logs += self.session.query(ActivityLog)\
                .filter(ActivityLog.timestamp < cutoff_date)\
                .delete(synchronize_session=False)
            
            self.session.commit()
            logger.info(f"Cleaned up {deleted_screenshots} screenshots and {deleted_logs} activity logs")
            return deleted_screenshots + deleted_logs
        
        except SQLAlchemyError as e:
            logger.error(f"Error cleaning up old data: {e}")
            self.session.rollback()
            return 0
    
    def close(self):
        """Close the database session"""
        if self.session:
            self.session.close()
            logger.info("Database session closed")

# Create a singleton instance
db_manager = DBManager()