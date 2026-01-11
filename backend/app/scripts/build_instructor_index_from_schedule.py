# scripts/build_instructor_index_from_schedule.py
import json
import pickle
import re
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from config.paths import data_file

def normalize_name(n: str) -> str:
    """Normalize name: trim and collapse whitespace."""
    if not n:
        return ""
    return re.sub(r"\s+", " ", n.strip())

def add_instructor(
    name: str,
    full_names_lower: set,
    canonical_by_lower: dict,
    first_to_full: dict,
    last_to_full: dict
):
    """Add instructor to all index structures."""
    name = normalize_name(name)
    if not name:
        return
    
    low = name.lower()
    full_names_lower.add(low)
    canonical_by_lower[low] = name
    
    parts = name.split(" ")
    if len(parts) >= 2:
        first = parts[0].lower()
        last = parts[-1].lower()
        first_to_full.setdefault(first, set()).add(name)
        last_to_full.setdefault(last, set()).add(name)

def main():
    schedule_path = data_file("5000.json")
    if not schedule_path.exists():
        print(f"Error: {schedule_path} not found. Cannot build instructor index.")
        return
    
    try:
        with open(schedule_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            rows = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    if not isinstance(rows, list):
        print(f"Error: Expected list of courses, got {type(rows)}")
        return
    
    full_names_lower = set()
    canonical_by_lower = {}
    first_to_full = {}
    last_to_full = {}
    
    for course in rows:
        if not isinstance(course, dict):
            continue
        
        sections = course.get("s") or []
        if not isinstance(sections, list):
            sections = []
        
        for sec in sections:
            if not isinstance(sec, dict):
                continue
            
            instructors_list = sec.get("r") or []
            if not isinstance(instructors_list, list):
                instructors_list = []
            
            for r in instructors_list:
                if isinstance(r, dict):
                    name = r.get("n")
                    if name:
                        add_instructor(
                            name,
                            full_names_lower,
                            canonical_by_lower,
                            first_to_full,
                            last_to_full
                        )
    
    payload = dict(
        full_names_lower=full_names_lower,
        canonical_by_lower=canonical_by_lower,
        first_to_full={k: list(v) for k, v in first_to_full.items()},
        last_to_full={k: list(v) for k, v in last_to_full.items()}
    )
    
    output_path = data_file("instructor_index.pkl")
    with open(output_path, "wb") as f:
        pickle.dump(payload, f)
    print(f"built {output_path} with {len(full_names_lower)} instructors")

if __name__ == "__main__":
    main()

