# scripts/build_instructor_index.py
from pathlib import Path
import csv
import pickle
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from config.paths import data_file, DATA

def main():
    src = data_file("instructors.csv")
    out = data_file("instructor_index.pkl")
    
    full_names_lower = set()
    canonical_by_lower = {}
    first_to_full = {}
    last_to_full = {}

    if not src.exists():
        print("No instructors.csv; creating a tiny stub index.")
        payload = dict(
            full_names_lower=set(),
            canonical_by_lower={},
            first_to_full={},
            last_to_full={}
        )
        with open(out, "wb") as f:
            pickle.dump(payload, f)
        print(f"wrote stub {out}")
        return

    with open(src, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            fn = (row.get("first_name") or "").strip()
            ln = (row.get("last_name") or "").strip()
            canonical = (row.get("canonical") or f"{fn} {ln}").strip()
            lower_full = f"{fn} {ln}".strip().lower()
            if not lower_full: 
                continue
            full_names_lower.add(lower_full)
            canonical_by_lower[lower_full] = canonical
            first_to_full.setdefault(fn.lower(), set()).add(canonical)
            last_to_full.setdefault(ln.lower(), set()).add(canonical)

    payload = dict(
        full_names_lower=full_names_lower,
        canonical_by_lower=canonical_by_lower,
        first_to_full=first_to_full,
        last_to_full=last_to_full
    )
    with open(out, "wb") as f:
        pickle.dump(payload, f)
    print(f"built {out} with {len(full_names_lower)} instructors")

if __name__ == "__main__":
    main()


