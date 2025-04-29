#!/usr/bin/env python3
"""
Test script for database integration
Tests the database models and operations
"""

import os
import sys
import time
from datetime import datetime

from models import init_db, User, Screenshot, ActivityLog, AutomationTask, AutomationSuggestion
from db_manager import db_manager
from utils import setup_logging

# Setup logging
logger = setup_logging()

def test_database_operations():
    """Test basic database operations"""
    print("Testing database operations...")
    
    # Get default user
    user_id = db_manager.get_default_user_id()
    if not user_id:
        print("Error: No default user found")
        return False
    
    print(f"Default user ID: {user_id}")
    
    # Test screenshot creation
    print("\nTesting screenshot creation...")
    screenshot_id = db_manager.save_screenshot(
        file_path="test_screenshot.png",
        window_title="Test Window",
        application_name="Test App",
        extracted_text="This is test text from a screenshot",
        resolution="1920x1080"
    )
    
    if not screenshot_id:
        print("Error: Failed to create screenshot")
        return False
    
    print(f"Created screenshot with ID: {screenshot_id}")
    
    # Test activity logging
    print("\nTesting activity logging...")
    activity_id = db_manager.log_activity(
        activity_type="test_activity",
        description="Test activity description",
        screenshot_id=screenshot_id,
        data={"test_key": "test_value", "timestamp": time.time()}
    )
    
    if not activity_id:
        print("Error: Failed to log activity")
        return False
    
    print(f"Created activity log with ID: {activity_id}")
    
    # Test automation task creation
    print("\nTesting automation task creation...")
    task_id = db_manager.save_automation_task(
        name="Test Automation",
        steps=[
            {"type": "click", "x": 100, "y": 200},
            {"type": "key", "key": "enter"},
            {"type": "wait", "duration": 1.0}
        ],
        description="Test automation task",
        triggers=[
            {"type": "time", "value": "09:00"}
        ]
    )
    
    if not task_id:
        print("Error: Failed to create automation task")
        return False
    
    print(f"Created automation task with ID: {task_id}")
    
    # Test updating automation execution
    print("\nTesting automation execution update...")
    updated = db_manager.update_automation_execution(task_id)
    if not updated:
        print("Error: Failed to update automation execution")
        return False
    
    print(f"Updated automation execution count for task ID: {task_id}")
    
    # Test suggestion creation
    print("\nTesting suggestion creation...")
    suggestion_id = db_manager.save_automation_suggestion(
        title="Test Suggestion",
        description="You should automate this test activity",
        confidence=0.85,
        pattern_data={"occurrences": 5, "pattern_type": "click_sequence"}
    )
    
    if not suggestion_id:
        print("Error: Failed to create suggestion")
        return False
    
    print(f"Created suggestion with ID: {suggestion_id}")
    
    # Test retrieving recent activities
    print("\nTesting activity retrieval...")
    activities = db_manager.get_recent_activities(limit=10)
    print(f"Retrieved {len(activities)} recent activities")
    
    # Test retrieving automation tasks
    print("\nTesting automation task retrieval...")
    tasks = db_manager.get_automation_tasks()
    print(f"Retrieved {len(tasks)} automation tasks")
    
    # Test retrieving suggestions
    print("\nTesting suggestion retrieval...")
    suggestions = db_manager.get_automation_suggestions()
    print(f"Retrieved {len(suggestions)} automation suggestions")
    
    print("\nAll database tests completed successfully!")
    return True

if __name__ == "__main__":
    print("Database Test Script")
    print("===================\n")
    
    if 'DATABASE_URL' not in os.environ:
        print("Error: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    print(f"Database URL: {os.environ['DATABASE_URL']}")
    
    # Initialize the database
    print("\nInitializing database...")
    init_db()
    
    # Run tests
    if test_database_operations():
        print("\nAll tests passed!")
        sys.exit(0)
    else:
        print("\nTests failed!")
        sys.exit(1)