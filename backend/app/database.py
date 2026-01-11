from sqlmodel import SQLModel, create_engine, text
from sqlalchemy import inspect

sqlite_file_name = "database.db"
engine = create_engine(f"sqlite:///{sqlite_file_name}", echo = True)

def init_db():
    """Initialize database with all models."""
    from .models.db_models import UserProfileDB, ScheduleDB, ScheduleCoursesDB
    SQLModel.metadata.create_all(engine)
    
    # Auto-migrate UserProfileDB if needed
    _migrate_user_profile_db()

def _migrate_user_profile_db():
    """Add missing columns to UserProfileDB if they don't exist."""
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('userprofiledb')]
        
        columns_to_add = [
            ('unavailable_times', 'TEXT'),
            ('prefer_avoid_times', 'TEXT'),
        ]
        
        for col_name, col_type in columns_to_add:
            if col_name not in columns:
                try:
                    with engine.begin() as conn:
                        conn.execute(text(f"ALTER TABLE userprofiledb ADD COLUMN {col_name} {col_type}"))
                    print(f"✓ Added column userprofiledb.{col_name}")
                except Exception as e:
                    error_str = str(e).lower()
                    if "duplicate column" in error_str or "already exists" in error_str:
                        print(f"  Note: Column {col_name} already exists")
                    else:
                        print(f"  ✗ Warning: Could not add column {col_name}: {e}")
    except Exception as e:
        # Table might not exist yet, which is fine - it will be created by create_all
        if "no such table" not in str(e).lower():
            print(f"Warning: Migration check failed: {e}")