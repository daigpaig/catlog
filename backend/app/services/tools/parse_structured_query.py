from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Literal
import json
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Try to load .env from multiple possible locations
# First try the backend/app directory (where .env might be)
app_dir = Path(__file__).parent.parent  # backend/app
backend_dir = Path(__file__).parent.parent.parent  # backend
env_paths = [
    app_dir / ".env",  # backend/app/.env
    backend_dir / ".env",  # backend/.env
    Path.cwd() / ".env",   # Current working directory
    Path.cwd() / "backend" / ".env",  # backend/.env from project root
    Path.cwd() / "backend" / "app" / ".env",  # backend/app/.env from project root
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        break
else:
    # If no .env found, try default load_dotenv() behavior
    load_dotenv()

DayCode = Literal["M", "T", "W", "R", "F", "S", "U"]  # Monday=M, Tuesday=T, Wednesday=W, Thursday=R, Friday=F, Saturday=S, Sunday=U

@dataclass
class PrioritySpec:
    """Specification for ranking weights and hard/soft constraints."""
    # Ranking weights, not filters (e.g., {"requirement_fit": 1.0, "workload": 0.8})
    weights: Dict[str, float] = field(default_factory=dict)
    # Optional: mark constraints as must-satisfy (field names)
    hard: List[str] = field(default_factory=list)
    # Optional: mark constraints as soft preferences (field names)
    soft: List[str] = field(default_factory=list)

@dataclass
class StructuredQuery:
    # --- term / offering ---
    term: Optional[str] = None
    offered_in_terms: List[str] = field(default_factory=list)  # PlanCourse.terms (historical signal)

    # --- catalog identity ---
    subjects: List[str] = field(default_factory=list)          # "STAT", "CS", "COMP_SCI", ...
    catalog_numbers: List[str] = field(default_factory=list)   # "303", "211", etc.
    course_ids: List[str] = field(default_factory=list)        # Full IDs if known
    schools: List[str] = field(default_factory=list)           # "WCAS", "MEAS", etc.

    # --- gen-ed / distribution tags ---
    distros: List[str] = field(default_factory=list)           # Distribution requirement chars "1"-"7"
    disciplines: List[str] = field(default_factory=list)       # Discipline tags if applicable

    # --- units / repeatability ---
    units_range: List[Tuple[float, float]] = field(default_factory=list)  # e.g., [(3.0, 4.0)]
    repeatable: Optional[bool] = None
    exclude_placeholder: bool = True

    # --- schedule constraints (section-level) ---
    days_include: List[DayCode] = field(default_factory=list)  # ["M", "W"] for Monday/Wednesday
    days_exclude: List[DayCode] = field(default_factory=list)  # ["F"] for no Friday
    time_include: List[Tuple[str, str]] = field(default_factory=list)   # [("14:00", "17:00")] for 2pm-5pm
    time_exclude: List[Tuple[str, str]] = field(default_factory=list)   # [("08:00", "12:00")] for no mornings
    components: List[str] = field(default_factory=list)                 # ["LEC", "SEM", "LAB", etc.]
    components_exclude: List[str] = field(default_factory=list)

    # --- instructors ---
    instructors_include: List[str] = field(default_factory=list)
    instructors_exclude: List[str] = field(default_factory=list)

    # --- text search (core heuristic) ---
    include_keywords: List[str] = field(default_factory=list)  # Keywords to search for (LLM can expand these)
    exclude_keywords: List[str] = field(default_factory=list)  # Keywords to avoid
    # searched over:
    # - PlanCourse.name, description, prerequisites
    # - ScheduleSection.topic, descriptions[]
    # - Instructor.bio (if present)

    # --- ranking ---
    priority: PrioritySpec = field(default_factory=PrioritySpec)

    notes: str = ""
    original_message: str = ""

def _get_openai_client() -> OpenAI:
    """Get OpenAI client instance."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Try loading again in case it wasn't loaded before
        app_dir = Path(__file__).parent.parent  # backend/app
        backend_dir = Path(__file__).parent.parent.parent  # backend
        env_paths = [
            app_dir / ".env",  # backend/app/.env
            backend_dir / ".env",  # backend/.env
            Path.cwd() / ".env",
            Path.cwd() / "backend" / ".env",
            Path.cwd() / "backend" / "app" / ".env",
        ]
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path, override=True)
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    break
        
        if not api_key:
            raise ValueError(
                f"OPENAI_API_KEY not found in environment variables.\n"
                f"Checked .env files in: {[str(p) for p in env_paths]}\n"
                f"Current working directory: {Path.cwd()}\n"
                f"Make sure your .env file exists and contains OPENAI_API_KEY=your-key-here"
            )
    return OpenAI(api_key=api_key)

def parse_structured_query(message: str, term_hint: Optional[str] = None) -> StructuredQuery:
    """
    Parse a natural language query into a StructuredQuery using LLM.
    
    Args:
        message: The user's natural language query
        term_hint: Optional term hint (e.g., "2025FA")
    
    Returns:
        StructuredQuery object with extracted fields
    """
    client = _get_openai_client()
    
    system_prompt = """You are a query parser for a course recommendation system at Northwestern University.

Parse the user's query and extract structured information. Return a FLAT JSON object with all fields at the top level (NO nested grouping keys like "CATALOG IDENTITY" or "SCHEDULE CONSTRAINTS").

The JSON object should have these fields directly at the root level:

- term: Specific term code (e.g., "2025FA") if mentioned.
- offered_in_terms: List of historical terms if user mentions specific quarters.
- subjects: List of subject codes (e.g., ["COMP_SCI", "STAT", "MATH", "LING", "ITALIAN"]). Use canonical codes like "COMP_SCI" for CS/Computer Science.
- catalog_numbers: List of course numbers (e.g., ["303", "211"]) if specific courses mentioned.
- course_ids: List of full course IDs if known (e.g., ["STAT303-1"]).
- schools: List of school codes (e.g., ["WCAS", "MEAS", "MUSIC", "SPCH", "SESP", "KGSM", "LAW", "TGS", "UC", "DOHA", "JOUR"]).
- distros: List of distribution requirement numbers (1-7) as strings, e.g., ["1", "2"].
- disciplines: List of discipline tags if applicable.
- units_range: List of [min_credits, max_credits] tuples (e.g., [[3.0, 4.0]] for 3-4 credit classes).
- repeatable: Boolean if repeatable courses are required/allowed.
- exclude_placeholder: Boolean (default true) to exclude placeholder courses.
- days_include: List of day codes where M=Monday, T=Tuesday, W=Wednesday, R=Thursday, F=Friday, S=Saturday, U=Sunday (e.g., ["M", "W"] for Monday/Wednesday).
- days_exclude: List of day codes to exclude (e.g., ["F"] for "no Friday").
- time_include: List of [start_time, end_time] tuples in 24-hour format "HH:MM" (e.g., [["14:00", "17:00"]] for 2pm-5pm, [["14:00", "21:30"]] for "after 2pm").
- time_exclude: List of [start_time, end_time] tuples to exclude (e.g., [["08:00", "12:00"]] for "no mornings").
- components: List of component types to include (e.g., ["LEC", "SEM", "LAB"]).
- components_exclude: List of component types to avoid.
- instructors_include: List of instructor names (full names if possible).
- instructors_exclude: List of instructor names to avoid.
- include_keywords: List of keywords to search for in course names, descriptions, topics, prerequisites. 
  **CRITICAL: Expand keywords intelligently!** If user asks for:
  - "consulting courses" → add ["consulting", "management", "business", "communication", "strategy", "case study"]
  - "data analytics internships" → add ["data", "analytics", "statistics", "programming", "internship", "career"]
  - "machine learning and linguistics" → add ["machine learning", "ml", "linguistics", "nlp", "natural language", "computational linguistics"]
  - "urban planning" → add ["urban", "planning", "city", "urban studies", "policy", "urbanism"]
  - "NLP" → add ["nlp", "natural language", "computational linguistics", "language processing", "text analysis"]
  Include synonyms, related concepts, and domain-specific terms that would appear in course descriptions.
- exclude_keywords: List of keywords that should NOT appear in results (e.g., ["busywork", "attendance", "exams"] for "no busywork-heavy classes").
- priority: Object with:
  - weights: Object mapping priority names to weights 0-1 (e.g., {"requirement_fit": 1.0, "workload": 0.8}). Use this for ranking, not filtering.
  - hard: List of field names that are hard constraints (must satisfy), e.g., ["days_exclude", "time_include"].
  - soft: List of field names that are soft preferences, e.g., ["include_keywords", "workload"].
- notes: Any additional context about the query that doesn't fit into structured fields.

CRITICAL FORMATTING RULES:
- Return a FLAT JSON object with all fields at the root level. DO NOT nest fields under category keys like "CATALOG IDENTITY" or "SCHEDULE CONSTRAINTS".
- Example of CORRECT format:
  {
    "subjects": ["STAT"],
    "days_exclude": ["F"],
    "time_include": [["14:00", "21:30"]],
    "include_keywords": ["statistics", "data analysis"]
  }
- Example of INCORRECT format (DO NOT DO THIS):
  {
    "CATALOG IDENTITY": { "subjects": ["STAT"] },
    "SCHEDULE CONSTRAINTS": { "days_exclude": ["F"] }
  }
- Only include fields that have values (don't include empty lists, empty objects, or None values).
- For days, use letter codes: M, T, W, R, F, S, U (not numbers).
- For time ranges, use 24-hour format "HH:MM".
- Extract subjects from mentions: "CS"/"Computer Science" → "COMP_SCI", "STAT"/"Statistics" → "STAT", etc.
- For course codes like "STAT 303" or "CS 211", extract subject to subjects and number to catalog_numbers.
- For "no mornings", add ["08:00", "12:00"] to time_exclude.
- For "after 2pm", add ["14:00", "21:30"] to time_include.
- For "no Friday", add "F" to days_exclude.
- **KEYWORD EXPANSION IS CRITICAL**: Always expand include_keywords with related terms, synonyms, and domain concepts that would help match relevant courses.
- Be thoughtful about what users really mean - "courses for consulting" means they want keywords that would appear in consulting-related course descriptions.

Return ONLY valid JSON with a flat structure (all fields at root level), no other text."""

    user_prompt = f"""Parse this query: "{message}"

{f"Term hint: {term_hint}" if term_hint else ""}

Return a JSON object with the extracted fields."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1  # Low temperature for more consistent parsing
        )
        
        result_json = json.loads(response.choices[0].message.content)
        
        # Build StructuredQuery from JSON
        query = StructuredQuery(term=term_hint, original_message=message)
        
        # === TERM / OFFERING ===
        if "term" in result_json:
            query.term = result_json["term"]
        if "offered_in_terms" in result_json:
            query.offered_in_terms = result_json["offered_in_terms"]

        # === CATALOG IDENTITY ===
        if "subjects" in result_json:
            query.subjects = result_json["subjects"]
        if "catalog_numbers" in result_json:
            query.catalog_numbers = [str(cn) for cn in result_json["catalog_numbers"]]
        if "course_ids" in result_json:
            query.course_ids = result_json["course_ids"]
        if "schools" in result_json:
            query.schools = result_json["schools"]

        # === GEN-ED / DISTRIBUTION ===
        if "distros" in result_json:
            query.distros = [str(d) for d in result_json["distros"]]
        if "disciplines" in result_json:
            query.disciplines = [str(d) for d in result_json["disciplines"]]

        # === UNITS / REPEATABILITY ===
        if "units_range" in result_json:
            query.units_range = [tuple(ur) if isinstance(ur, list) else ur for ur in result_json["units_range"]]
        if "repeatable" in result_json:
            query.repeatable = result_json["repeatable"]
        if "exclude_placeholder" in result_json:
            query.exclude_placeholder = result_json["exclude_placeholder"]

        # === SCHEDULE CONSTRAINTS ===
        if "days_include" in result_json:
            query.days_include = [str(d) for d in result_json["days_include"]]
        if "days_exclude" in result_json:
            query.days_exclude = [str(d) for d in result_json["days_exclude"]]
        if "time_include" in result_json:
            query.time_include = [tuple(t) if isinstance(t, list) else t for t in result_json["time_include"]]
        if "time_exclude" in result_json:
            query.time_exclude = [tuple(t) if isinstance(t, list) else t for t in result_json["time_exclude"]]
        if "components" in result_json:
            query.components = result_json["components"]
        if "components_exclude" in result_json:
            query.components_exclude = result_json["components_exclude"]

        # === INSTRUCTORS ===
        if "instructors_include" in result_json:
            query.instructors_include = result_json["instructors_include"]
        if "instructors_exclude" in result_json:
            query.instructors_exclude = result_json["instructors_exclude"]

        # === TEXT SEARCH (KEYWORDS) ===
        if "include_keywords" in result_json:
            query.include_keywords = result_json["include_keywords"]
        if "exclude_keywords" in result_json:
            query.exclude_keywords = result_json["exclude_keywords"]

        # === PRIORITIES ===
        if "priority" in result_json:
            priority_data = result_json["priority"]
            if isinstance(priority_data, dict):
                if "weights" in priority_data:
                    query.priority.weights = priority_data["weights"]
                if "hard" in priority_data:
                    query.priority.hard = priority_data["hard"]
                if "soft" in priority_data:
                    query.priority.soft = priority_data["soft"]

        # === NOTES ===
        if "notes" in result_json:
            query.notes = result_json["notes"]
        
        return query
        
    except json.JSONDecodeError as e:
        # Fallback: return empty query with original message
        print(f"Failed to parse LLM response as JSON: {e}")
        return StructuredQuery(term=term_hint, original_message=message)
    except Exception as e:
        # Fallback: return empty query with original message
        print(f"Error calling LLM: {e}")
        return StructuredQuery(term=term_hint, original_message=message)
