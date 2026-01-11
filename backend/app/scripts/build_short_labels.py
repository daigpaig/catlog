# scripts/build_short_labels.py
from pathlib import Path
import json
import re
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from config.paths import data_file

def shorten(text: str, n=140) -> str:
    """Truncate text to n characters, preserving word boundaries."""
    if not text:
        return ""
    t = re.sub(r"\s+", " ", (text or "").strip())
    if len(t) <= n:
        return t
    # Try to cut at word boundary
    truncated = t[:n].rstrip()
    last_space = truncated.rfind(" ")
    if last_space > n * 0.8:  # Only use word boundary if we're not losing too much
        return truncated[:last_space] + "..."
    return truncated + "..."

def main():
    catalog_path = data_file("5000_w_desc.json")
    if not catalog_path.exists():
        print(f"Error: {catalog_path} not found. Run build_catalog_json.py first.")
        return
    
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    out = []
    for c in catalog:
        out.append({
            "course_id": c["course_id"],
            "short_title": shorten(c.get("title", ""), 80),
            "short_desc": shorten(c.get("desc", ""), 180),
        })
    
    out_path = data_file("short_labels.json")
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out_path} with {len(out)} entries")

if __name__ == "__main__":
    main()


