# scripts/build_subject_phrases_from_paper.py
import json
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from config.paths import data_file

def main():
    path = data_file("subjects.json")
    if not path.exists():
        print("subjects.json missing; skipping subject phrase generation")
        return
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    subjects = raw.get("subjects", {})
    if not isinstance(subjects, dict):
        print("Error: subjects field is not a dictionary")
        return
    
    lines = ["# data/subject_phrases.py", "# Auto-generated from Paper API subject data", "", "SUBJECT_PHRASES = {"]
    
    for code, info in subjects.items():
        if not isinstance(info, dict):
            continue
        
        name = (info.get("d") or "").lower().strip()
        if not name:
            continue
        
        # Generate aliases
        aliases = set()
        aliases.add(name)
        aliases.add(name.replace(" and ", " & "))
        aliases.add(code.replace("_", " ").lower())
        aliases.add(code.lower())
        
        # Add common abbreviations
        words = name.split()
        if len(words) > 0:
            # First word abbreviation
            aliases.add(words[0][:4].lower())
            # Acronym if multiple words
            if len(words) > 1:
                acronym = "".join([w[0] for w in words if w]).lower()
                if len(acronym) >= 2:
                    aliases.add(acronym)
        
        # Filter out empty strings and format
        alias_list = sorted([a for a in aliases if a])
        if alias_list:
            lines.append(f'    "{code}": {json.dumps(alias_list)},')
    
    lines.append("}")
    
    output_path = data_file("subject_phrases.py")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"wrote {output_path} with {len(subjects)} subjects")

if __name__ == "__main__":
    main()

