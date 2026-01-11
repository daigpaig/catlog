from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, text
from sqlalchemy import Result
from ..database import engine
from ..models.db_models import ScheduleCoursesDB, ScheduleDB, UserProfileDB
from ..schemas.schedule import ScheduleCourseCreate
from ..auth.dependencies import get_current_user
import hashlib

router = APIRouter()

def generate_course_color(subject: str) -> str:
    """
    Generate a consistent color for a course based on its subject (paper.nu style).
    Uses a hash function to ensure the same subject always gets the same color.
    Returns a hex color code that looks good on dark backgrounds.
    
    Args:
        subject: Course subject code (e.g., "COMP_SCI", "MATH", "STAT")
    """
    if not subject:
        # Default color if no subject provided
        return "#3b82f6"  # Blue
    
    # Paper.nu-inspired color palette - vibrant colors that work on dark backgrounds
    colors = [
        "#3b82f6",  # Blue
        "#8b5cf6",  # Purple
        "#ec4899",  # Pink
        "#ef4444",  # Red
        "#f59e0b",  # Amber
        "#10b981",  # Emerald
        "#06b6d4",  # Cyan
        "#6366f1",  # Indigo
        "#f97316",  # Orange
        "#14b8a6",  # Teal
        "#a855f7",  # Violet
        "#e11d48",  # Rose
        "#0ea5e9",  # Sky
        "#84cc16",  # Lime
        "#f43f5e",  # Fuchsia
    ]
    
    # Normalize subject code (uppercase, strip whitespace)
    normalized_subject = subject.upper().strip()
    
    # Create a hash from the subject and use it to select a color
    hash_obj = hashlib.md5(normalized_subject.encode())
    hash_int = int(hash_obj.hexdigest(), 16)
    color_index = hash_int % len(colors)
    return colors[color_index]

@router.get("/schedule/{schedule_id}/courses")
def get_schedule_courses(
    schedule_id: int,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """Get all courses for a specific schedule - ensures it belongs to the authenticated user."""
    with Session(engine) as session:
        # Verify schedule belongs to user
        schedule = session.exec(select(ScheduleDB).where(ScheduleDB.id == schedule_id)).first()
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found.")
        if schedule.netid != current_user.netid:
            raise HTTPException(status_code=403, detail="Cannot access schedule for different user")
        
        # Ensure migration is done before querying
        _ensure_migration()
        
        # Get all courses for this schedule
        try:
            courses = session.exec(
                select(ScheduleCoursesDB).where(ScheduleCoursesDB.schedule_id == schedule_id)
            ).all()
            # Backfill colors for courses that don't have them (use subject-based color)
            courses_to_update = []
            for course in courses:
                if not course.color and course.course_subject:
                    # Generate color based on subject
                    course.color = generate_course_color(course.course_subject)
                    courses_to_update.append(course)
            
            # Batch update courses with new colors
            if courses_to_update:
                for course in courses_to_update:
                    try:
                        session.execute(
                            text("UPDATE schedulecoursesdb SET color = :color WHERE id = :id"),
                            {"color": course.color, "id": course.id}
                        )
                    except Exception as e:
                        print(f"Warning: Could not update color for course {course.id}: {e}")
                session.commit()
            
            # Convert to dict - manually construct to ensure all fields including id are included
            result = []
            for c in courses:
                # Ensure course has a valid ID before adding to result
                if not hasattr(c, 'id') or c.id is None:
                    print(f"Warning: Course missing ID: section_id={getattr(c, 'section_id', 'unknown')}")
                    continue  # Skip courses without valid IDs
                
                # Manually construct dict to ensure all fields are included
                course_dict = {
                    'id': c.id,
                    'schedule_id': c.schedule_id,
                    'section_id': c.section_id,
                    'course_subject': getattr(c, 'course_subject', None),
                    'course_number': getattr(c, 'course_number', None),
                    'course_title': getattr(c, 'course_title', None),
                    'section_number': getattr(c, 'section_number', None),
                    'meeting_days': getattr(c, 'meeting_days', None) or [],
                    'start_end': getattr(c, 'start_end', None) or [],
                    'instructors': getattr(c, 'instructors', None) or [],
                    'color': getattr(c, 'color', None),
                }
                
                result.append(course_dict)
            return result
        except Exception as e:
            # If query fails due to missing columns, try raw SQL fallback using execute()
            print(f"Warning: Could not query with SQLModel: {e}")
            result = session.execute(
                text("SELECT id, schedule_id, section_id FROM schedulecoursesdb WHERE schedule_id = :schedule_id"),
                {"schedule_id": schedule_id}
            )
            rows = result.all()
            # Return minimal data
            return [{"id": r[0], "schedule_id": schedule_id, "section_id": r[2]} for r in rows]

def _ensure_migration():
    """Helper function to ensure database schema is migrated. Uses separate transactions for each ALTER TABLE."""
    try:
        # Check if table exists first
        with engine.connect() as check_conn:
            try:
                # Try to check if new columns exist (including color)
                check_conn.execute(text("SELECT course_subject, color FROM schedulecoursesdb LIMIT 1"))
                return  # Columns exist, no migration needed
            except Exception:
                # Columns don't exist or table doesn't exist - try to migrate
                pass
        
        # Migrate - add missing columns using separate connections for each ALTER TABLE
        print("Auto-migrating schedulecoursesdb: adding new columns...")
        columns_to_add = [
            ("course_subject", "TEXT"),
            ("course_number", "TEXT"),
            ("course_title", "TEXT"),
            ("section_number", "TEXT"),
            ("meeting_days", "TEXT"),
            ("start_end", "TEXT"),
            ("instructors", "TEXT"),
            ("color", "TEXT"),
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                # Use a separate connection for each ALTER TABLE to ensure it's committed
                with engine.begin() as mig_conn:  # begin() auto-commits on exit
                    mig_conn.execute(text(f"ALTER TABLE schedulecoursesdb ADD COLUMN {col_name} {col_type}"))
                print(f"  ✓ Added column: {col_name}")
            except Exception as e:
                error_str = str(e).lower()
                if "duplicate column" in error_str or "already exists" in error_str:
                    print(f"  Note: Column {col_name} already exists")
                elif "no such table" in error_str:
                    # Table doesn't exist - SQLModel will create it with all columns on first insert
                    print(f"  Note: Table doesn't exist yet, will be created automatically")
                    break
                else:
                    print(f"  ✗ Warning: Could not add column {col_name}: {e}")
        print("✓ Migration attempt complete")
    except Exception as e:
        print(f"Warning: Migration check failed: {e}")

@router.post("/schedule/{schedule_id}/courses")
def add_course(
    schedule_id: int,
    course_data: ScheduleCourseCreate,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """Add a course section to a schedule - ensures schedule belongs to the authenticated user."""
    # Ensure migration is done BEFORE opening session
    _ensure_migration()
    
    with Session(engine) as session:
        # Verify schedule belongs to user
        schedule = session.exec(select(ScheduleDB).where(ScheduleDB.id == schedule_id)).first()
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found.")
        if schedule.netid != current_user.netid:
            raise HTTPException(status_code=403, detail="Cannot modify schedule for different user")
        
        # Check if section already exists using raw SQL (only uses columns that definitely exist)
        existing_id = None
        try:
            # Use execute() for raw SQL with parameters
            result: Result = session.execute(
                text("SELECT id FROM schedulecoursesdb WHERE section_id = :section_id AND schedule_id = :schedule_id"),
                {"section_id": course_data.section_id, "schedule_id": schedule_id}
            )
            row = result.first()
            if row:
                # Extract ID from row - SQLAlchemy Result returns Row objects
                existing_id = row[0]
        except Exception as e:
            print(f"Note: Could not check for existing section: {e}")
            existing_id = None
        
        # Use raw SQL INSERT/UPDATE to avoid SQLModel column issues
        import json
        meeting_days_json = json.dumps(course_data.meeting_days or [])
        start_end_json = json.dumps(course_data.start_end or [])
        instructors_json = json.dumps(course_data.instructors or [])
        
        # Generate color if not provided - use subject for consistent coloring (paper.nu style)
        # All courses in the same subject get the same color
        if course_data.color:
            color = course_data.color
        elif course_data.course_subject:
            color = generate_course_color(course_data.course_subject)
        else:
            # Fallback: use section_id if no subject available
            color = generate_course_color(course_data.section_id)
        
        if existing_id:
            # Update existing entry using raw SQL with execute()
            try:
                session.execute(
                    text("""
                        UPDATE schedulecoursesdb 
                        SET course_subject = :course_subject,
                            course_number = :course_number,
                            course_title = :course_title,
                            section_number = :section_number,
                            meeting_days = :meeting_days,
                            start_end = :start_end,
                            instructors = :instructors,
                            color = :color
                        WHERE id = :id
                    """),
                    {
                        "id": existing_id,
                        "course_subject": course_data.course_subject,
                        "course_number": course_data.course_number,
                        "course_title": course_data.course_title,
                        "section_number": course_data.section_number,
                        "meeting_days": meeting_days_json,
                        "start_end": start_end_json,
                        "instructors": instructors_json,
                        "color": color,
                    }
                )
                session.commit()
                return {"message": "Course updated.", "id": existing_id}
            except Exception as e:
                session.rollback()
                print(f"Error updating schedule course: {e}")
                import traceback
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=f"Failed to update course: {str(e)}")
        
        # Create new entry using raw SQL with execute()
        try:
            session.execute(
                text("""
                    INSERT INTO schedulecoursesdb 
                    (schedule_id, section_id, course_subject, course_number, course_title, section_number, meeting_days, start_end, instructors, color)
                    VALUES (:schedule_id, :section_id, :course_subject, :course_number, :course_title, :section_number, :meeting_days, :start_end, :instructors, :color)
                """),
                {
                    "schedule_id": schedule_id,
                    "section_id": course_data.section_id,
                    "course_subject": course_data.course_subject,
                    "course_number": course_data.course_number,
                    "course_title": course_data.course_title,
                    "section_number": course_data.section_number,
                    "meeting_days": meeting_days_json,
                    "start_end": start_end_json,
                    "instructors": instructors_json,
                    "color": color,
                }
            )
            session.commit()
            # Get the ID of the newly inserted row
            id_result = session.execute(text("SELECT last_insert_rowid()"))
            row = id_result.first()
            new_id = row[0] if row else None
            return {"message": "Course added.", "id": new_id}
        except Exception as e:
            session.rollback()
            print(f"Error creating schedule course: {e}")
            import traceback
            traceback.print_exc()
            # If error is about missing columns, that means migration didn't work
            if "no such column" in str(e).lower():
                raise HTTPException(
                    status_code=500,
                    detail=f"Database schema is outdated. Please delete backend/app/database.db and restart the server."
                )
            raise HTTPException(status_code=500, detail=f"Failed to add course: {str(e)}")


@router.delete("/schedule/{schedule_id}/courses/{schedule_course_id}")
def remove_course(
    schedule_id: int,
    schedule_course_id: int,
    current_user: UserProfileDB = Depends(get_current_user)
):
    """Remove a course from a schedule - ensures schedule belongs to the authenticated user."""
    with Session(engine) as session:
        # Verify schedule belongs to user
        schedule = session.exec(select(ScheduleDB).where(ScheduleDB.id == schedule_id)).first()
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found.")
        if schedule.netid != current_user.netid:
            raise HTTPException(status_code=403, detail="Cannot modify schedule for different user")
        
        sched_course = session.exec(
            select(ScheduleCoursesDB).where(
                ScheduleCoursesDB.id == schedule_course_id,
                ScheduleCoursesDB.schedule_id == schedule_id
            )
        ).first()
        if sched_course:
            session.delete(sched_course)
            session.commit()
            return {"message": "Course deleted."}
        return {"error": "Course not found."}