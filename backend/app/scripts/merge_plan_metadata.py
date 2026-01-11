# scripts/merge_plan_metadata.py
from __future__ import annotations
import json
import sys
import os
from pathlib import Path

# Add parent directory to path to import config
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from config.paths import data_file

def chars_list(s: str) -> list[str]:
    """Extract distro/discipline codes from string."""
    if not s:
        return []
    return [ch for ch in s if ch in "1234567"]

def main():
    cat_path = data_file("5000_w_desc.json")
    plan_path = data_file("plan.json")
    
    if not cat_path.exists():
        print(f"Error: {cat_path} not found. Run normalize_paper_schedule.py first.")
        return
    
    if not plan_path.exists():
        print(f"Warning: {plan_path} not found. Skipping plan metadata merge.")
        return
    
    try:
        with open(cat_path, "r", encoding="utf-8") as f:
            cat_rows = json.load(f)
        with open(plan_path, "r", encoding="utf-8") as f:
            plan_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return
    except Exception as e:
        print(f"Error reading files: {e}")
        return
    
    # Build lookup by course_id
    cat = {row["course_id"]: row for row in cat_rows if "course_id" in row}
    
    # Process plan courses
    plan_courses = plan_data.get("courses", [])
    if not isinstance(plan_courses, list):
        plan_courses = []
    
    # Also check legacy courses if present
    legacy_courses = plan_data.get("legacy", [])
    if isinstance(legacy_courses, list):
        plan_courses.extend(legacy_courses)
    
    merged_count = 0
    for pc in plan_courses:
        if not isinstance(pc, dict):
            continue
            
        cid = pc.get("i")
        if not cid or cid not in cat:
            continue
        
        row = cat[cid]
        updated = False
        
        # Merge description
        if (not row.get("desc") or row.get("desc").strip() == "") and pc.get("d"):
            row["desc"] = pc["d"].strip()
            updated = True
        
        # Merge distros
        if pc.get("s"):
            plan_distros = set(chars_list(pc["s"]))
            existing_distros = set(row.get("distros", []))
            row["distros"] = sorted(existing_distros | plan_distros)
            updated = True
        
        # Merge disciplines
        if pc.get("f"):
            plan_disciplines = set(chars_list(pc["f"]))
            existing_disciplines = set(row.get("disciplines", []))
            row["disciplines"] = sorted(existing_disciplines | plan_disciplines)
            updated = True
        
        # Update school
        if pc.get("c"):
            row["school"] = pc["c"].strip()
            updated = True
        
        # Add prerequisites
        if pc.get("p"):
            row["prerequisites"] = pc["p"].strip()
            updated = True
        
        if updated:
            merged_count += 1
    
    # Fallback: if desc still empty, try first section description
    for row in cat.values():
        if not row.get("desc") or row.get("desc").strip() == "":
            for sec in row.get("sections", []):
                if isinstance(sec, dict):
                    # Check if section has description in p field
                    p = sec.get("p")
                    if p and isinstance(p, list) and len(p) > 0:
                        first_item = p[0]
                        if isinstance(first_item, list) and len(first_item) >= 2:
                            desc_text = str(first_item[1]).strip()
                            if desc_text:
                                row["desc"] = desc_text
                                break
    
    out = list(cat.values())
    with open(cat_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"merged plan.json into 5000_w_desc.json ({merged_count} courses updated)")

if __name__ == "__main__":
    main()

