# scripts/normalize_paper_schedule.py
from __future__ import annotations
from pathlib import Path
import json
import re
import sys
import os
from typing import Any, Dict, List, Optional, Tuple

# Add parent directory to path to import config
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from config.paths import data_file

DAY = {"0": "Mon", "1": "Tue", "2": "Wed", "3": "Thu", "4": "Fri", "5": "Sat", "6": "Sun"}

def daycode_to_text(code: Optional[str]) -> str:
    """Convert meeting day code (e.g., "024") to text (e.g., "Mon/Wed/Fri")."""
    if not code:
        return ""
    return "/".join(DAY[d] for d in code if d in DAY)

def hhmm(t: Optional[Dict[str, int]]) -> Optional[str]:
    """Convert {h, m} dict to "HH:MM" string."""
    if not t:
        return None
    h = t.get("h")
    m = t.get("m")
    if h is None or m is None:
        return None
    return f"{int(h):02d}:{int(m):02d}"

def level_from_number(num: str) -> int:
    """Extract course level from catalog number (e.g., "340-3" -> 300)."""
    if not num:
        return 100
    m = re.match(r"(\d)", num)
    return int(m.group(1)) * 100 if m else 100

def distros_from_string(s: Optional[str]) -> List[str]:
    """Extract distro codes from string (e.g., "14" -> ["1", "4"])."""
    if not s:
        return []
    return [ch for ch in s if ch in "1234567"]

def merge_meetings(sec: Dict[str, Any]) -> List[str]:
    """Merge meeting days, start times, and end times into readable strings."""
    parts = []
    m_arr = sec.get("m") or []
    x_arr = sec.get("x") or []
    y_arr = sec.get("y") or []
    
    # Handle both single string and array formats
    if isinstance(m_arr, str):
        m_arr = [m_arr]
    if not isinstance(x_arr, list):
        x_arr = [x_arr] if x_arr else []
    if not isinstance(y_arr, list):
        y_arr = [y_arr] if y_arr else []
    
    max_len = max(len(m_arr), len(x_arr), len(y_arr))
    for i in range(max_len):
        days = daycode_to_text(m_arr[i] if i < len(m_arr) else None)
        start = hhmm(x_arr[i] if i < len(x_arr) else None)
        end = hhmm(y_arr[i] if i < len(y_arr) else None)
        if days and start and end:
            parts.append(f"{days} {start}–{end}")
    return parts

def first_section_desc(sec: Dict[str, Any]) -> Optional[str]:
    """Extract first section description from SectionDescription array."""
    # SectionDescription[] is like: [ ["Overview","text..."], ["Materials","..."] ]
    p = sec.get("p") or []
    if p and isinstance(p, list) and len(p) > 0:
        first_item = p[0]
        if isinstance(first_item, list) and len(first_item) >= 2:
            return str(first_item[1]).strip()
    return None

def main():
    src = data_file("5000.json")
    if not src.exists():
        print(f"Error: {src} not found. Please ensure Paper schedule data is available.")
        return
    
    try:
        # Handle large JSON files (may be minified single line)
        with open(src, "r", encoding="utf-8") as f:
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
    
    out = []
    for course in rows:
        if not isinstance(course, dict):
            continue
            
        subject = (course.get("u") or "").strip()
        number = (course.get("n") or "").strip()
        title = (course.get("t") or "").strip()
        school = (course.get("c") or "WCAS").strip()
        course_id = f"{subject} {number}".strip()
        
        if not course_id:
            continue
        
        instructors = set()
        meeting_texts = []
        sections_norm = []
        
        sections = course.get("s") or []
        if not isinstance(sections, list):
            sections = []
        
        for sec in sections:
            if not isinstance(sec, dict):
                continue
                
            # Extract instructors
            instructors_list = sec.get("r") or []
            if not isinstance(instructors_list, list):
                instructors_list = []
            
            for r in instructors_list:
                if isinstance(r, dict):
                    name = (r.get("n") or "").strip()
                    if name:
                        instructors.add(name)
            
            # Merge meetings
            meetings = merge_meetings(sec)
            meeting_texts.extend(meetings)
            
            # Build normalized section
            section_data = {
                "section_id": sec.get("i"),
                "section_number": sec.get("s"),
                "topic": (sec.get("k") or "").strip(),
                "meetings": meetings,
                "distros": distros_from_string(sec.get("o")),
                "disciplines": distros_from_string(sec.get("f")),
                "start_date": sec.get("d"),
                "end_date": sec.get("e"),
                "component": sec.get("c"),
                "instructors": [r.get("n") for r in instructors_list if isinstance(r, dict) and r.get("n")],
                "room": (sec.get("l") or [None])[0] if isinstance(sec.get("l"), list) and sec.get("l") else None,
            }
            sections_norm.append(section_data)
        
        # Use first section description if available
        desc = ""
        for sec in sections:
            if isinstance(sec, dict):
                sec_desc = first_section_desc(sec)
                if sec_desc:
                    desc = sec_desc
                    break
        
        out.append({
            "course_id": course_id,
            "subject": subject,
            "number": number,
            "title": title,
            "desc": desc,  # to be filled from plan or section descriptions
            "school": school,
            "level": level_from_number(number),
            "distros": [],  # to be merged from plan or sections
            "disciplines": [],  # optional
            "instructors": sorted(instructors),
            "meeting_text": "; ".join([m for m in meeting_texts if m]),
            "sections": sections_norm,
        })
    
    output_path = data_file("5000_w_desc.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"wrote {output_path} with {len(out)} courses")

if __name__ == "__main__":
    main()

