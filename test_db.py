#!/usr/bin/env python3
"""
Test Database Connection
A simple script to test if the database connection is working properly
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User

def test_database_connection():
    """Test if the database connection is working properly"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get database URL from environment variable
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set.")
        print("Please set DATABASE_URL or run fix_db.bat to create a SQLite database.")
        return False
    
    try:
        # Create database engine
        print(f"Connecting to database: {database_url}")
        engine = create_engine(database_url)
        
        # Create tables if they don't exist
        Base.metadata.create_all(engine)
        print("Database tables created successfully")
        
        # Create a session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Test query
        user_count = session.query(User).count()
        print(f"Number of users in database: {user_count}")
        
        # Create a test user if none exists
        if user_count == 0:
            test_user = User(
                username="test_user",
                email="test@example.com",
                settings={"theme": "dark", "notifications": True}
            )
            
            session.add(test_user)
            session.commit()
            
            print(f"Created test user with ID: {test_user.id}")
        
        # Close session
        session.close()
        
        return True
    
    except Exception as e:
        print(f"ERROR: Failed to connect to database: {e}")
        return False

if __name__ == "__main__":
    print("=== Database Connection Test ===")
    
    if test_database_connection():
        print("\nSUCCESS: Database connection is working properly!")
    else:
        print("\nFAILED: Database connection test failed.")
        print("Please run fix_db.bat to fix any database issues.")
    
    print("\nPress Enter to exit...")
    input()