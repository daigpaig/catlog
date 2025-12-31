"""
Migration script to update database schema for auth fields.
This will recreate the database with the new schema.
WARNING: This will delete all existing data!
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from sqlmodel import SQLModel
from database import engine
from models.db_models import UserProfileDB, ScheduleDB, ScheduleCoursesDB

def migrate_database():
    """Drop all tables and recreate with new schema."""
    print("Dropping all tables...")
    SQLModel.metadata.drop_all(engine)
    
    print("Creating new tables with updated schema...")
    SQLModel.metadata.create_all(engine)
    
    print("✅ Database migration complete!")
    print("⚠️  All existing data has been deleted.")

if __name__ == "__main__":
    response = input("This will delete all data. Continue? (yes/no): ")
    if response.lower() == "yes":
        migrate_database()
    else:
        print("Migration cancelled.")

