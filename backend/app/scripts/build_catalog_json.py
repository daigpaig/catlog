# scripts/build_catalog_json.py
from pathlib import Path
import csv
import json
import random
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from config.paths import data_file

def main():
    out = data_file("5000_w_desc.json")
    src_csv = data_file("catalog_raw.csv")

    data = []
    if src_csv.exists():
        with open(src_csv, newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                subj = row.get("subject", "").strip()
                num = row.get("number", "").strip()
                cid = f"{subj} {num}".strip()
                if not cid:
                    continue
                data.append({
                    "course_id": cid,
                    "subject": subj,
                    "number": num,
                    "title": row.get("title", "").strip(),
                    "desc": row.get("desc", "").strip(),
                    "school": row.get("school", "").strip(),
                    "level": int(row.get("level") or "100"),
                    "distros": [d for d in (row.get("distros", "").split("|")) if d],
                    "instructors": [i.strip() for i in row.get("instructors", "").split("|") if i.strip()],
                })
    else:
        # small mock
        subjects = ["COMP_SCI", "STAT", "MATH", "ECON", "PSYCH", "HISTORY", "PHIL", "POLI_SCI"]
        numbers = ["110", "211", "303-1", "303-2", "301", "250", "350", "400"]
        titles = {
            "COMP_SCI": ["Introduction to Programming", "Data Structures", "Algorithms", "Machine Learning"],
            "STAT": ["Introduction to Statistics", "Statistical Methods", "Probability Theory"],
            "MATH": ["Calculus I", "Calculus II", "Linear Algebra", "Differential Equations"],
            "ECON": ["Principles of Economics", "Microeconomics", "Macroeconomics"],
        }
        descs = [
            "Introduction to fundamental concepts and methods.",
            "Intermediate-level course covering core principles.",
            "Advanced topics and applications in the field.",
            "Comprehensive study of theoretical foundations.",
        ]
        
        for i in range(1, 51):
            subj = random.choice(subjects)
            num = random.choice(numbers)
            cid = f"{subj} {num}"
            title_base = random.choice(titles.get(subj, ["Course"]))
            data.append({
                "course_id": cid,
                "subject": subj,
                "number": num,
                "title": f"{title_base} ({num})",
                "desc": random.choice(descs),
                "school": "WCAS",
                "level": 200 if "211" in num or "250" in num else (300 if "303" in num or "350" in num else 100),
                "distros": ["2"] if subj in ["MATH", "COMP_SCI", "STAT"] else ["3"],
                "instructors": ["Jane Doe", "John Smith"],
            })

    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"wrote {out} with {len(data)} rows")

if __name__ == "__main__":
    main()


