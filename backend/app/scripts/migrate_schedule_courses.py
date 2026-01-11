#!/usr/bin/env python3
"""
Migration script to add new columns to ScheduleCoursesDB table.
Run this if your database doesn't have the new columns yet.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import SQLModel, create_engine, text
from app.database import engine
from app.models.db_models import ScheduleCoursesDB

def migrate():
    """Add new columns to ScheduleCoursesDB if they don't exist."""
    print("Checking database schema...")
    
    with engine.connect() as conn:
        # Check if columns exist
        result = conn.execute(text("PRAGMA table_info(schedulecoursesdb)"))
        columns = {row[1] for row in result}
        
        print(f"Existing columns: {columns}")
        
        new_columns = {
            'course_subject': 'TEXT',
            'course_number': 'TEXT',
            'course_title': 'TEXT',
            'section_number': 'TEXT',
            'meeting_days': 'TEXT',  # JSON stored as TEXT in SQLite
            'start_end': 'TEXT',     # JSON stored as TEXT in SQLite
            'instructors': 'TEXT',   # JSON stored as TEXT in SQLite
        }
        
        added = []
        for col_name, col_type in new_columns.items():
            if col_name.lower() not in {c.lower() for c in columns}:
                try:
                    conn.execute(text(f"ALTER TABLE schedulecoursesdb ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                    added.append(col_name)
                    print(f"✓ Added column: {col_name}")
                except Exception as e:
                    print(f"✗ Failed to add column {col_name}: {e}")
        
        if added:
            print(f"\n✓ Successfully added {len(added)} columns: {', '.join(added)}")
        else:
            print("\n✓ All columns already exist. No migration needed.")
        
        print("\nMigration complete!")

if __name__ == "__main__":
    migrate()
