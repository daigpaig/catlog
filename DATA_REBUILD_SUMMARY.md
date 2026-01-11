# Data Rebuild Summary

All missing data assets have been recreated with rebuild scripts and fallbacks. Here's what was built:

## ✅ Files Created

### Configuration
- **`backend/app/config/paths.py`** - Centralized path resolution for data files

### Data Files (Source)
- **`backend/app/data/subject_phrases.py`** - Subject aliases mapping (30+ subjects)
- **`backend/app/data/program_requirements_v0.json`** - Seed program requirements (3 programs)
- **`backend/app/data/instructors.csv`** - Sample instructor roster (10 instructors)
- **`backend/app/data/catalog_raw.csv`** - Sample catalog export (14 courses)

### Build Scripts
- **`backend/app/scripts/build_instructor_index.py`** - Builds instructor index from CSV
- **`backend/app/scripts/build_catalog_json.py`** - Builds catalog JSON from CSV
- **`backend/app/scripts/build_atoms_index.py`** - Builds Chroma vector index
- **`backend/app/scripts/build_short_labels.py`** - Builds short labels cache
- **`backend/app/scripts/README.md`** - Documentation for scripts

### Build Automation
- **`Makefile`** - One-command rebuild: `make data`

### Updates
- **`.gitignore`** - Added `data_gen/` to ignore generated files
- **`parse_structured_query.py`** - Enhanced import fallback for subject_phrases
- **`shortlist_classes.py`** - Added graceful fallbacks for missing catalog

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install chromadb openai python-dotenv
```

### 2. Build All Data Assets
```bash
make data
```

This will:
- Build `instructor_index.pkl` from `instructors.csv`
- Build `5000_w_desc.json` from `catalog_raw.csv` (or create mock)
- Build Chroma vector index (requires OpenAI API key)
- Build `short_labels.json`

### 3. Verify
Check that these files exist:
- `backend/app/data/instructor_index.pkl`
- `backend/app/data/5000_w_desc.json`
- `backend/app/data/short_labels.json`
- `backend/app/data_gen/chroma/` (directory)

## 📋 Manual Tasks (When You Have Real Data)

### High Priority
1. **Replace `data/instructors.csv`** with real instructor roster
   - Export from registrar or scrape from course catalog
   - Format: `first_name,last_name,canonical`
   - Then run: `python scripts/build_instructor_index.py`

2. **Replace `data/catalog_raw.csv`** with real catalog export
   - Export from paper.nu API or registrar
   - Format: `subject,number,title,desc,school,level,distros,instructors`
   - Then run: `python scripts/build_catalog_json.py`

3. **Set OpenAI API Key** (required for embeddings)
   ```bash
   export OPENAI_API_KEY=your-key-here
   # or add to .env file
   ```

### Medium Priority
4. **Update `data/program_requirements_v0.json`**
   - Replace seed data with real requirement logic
   - Parse from registrar PDFs or official requirements

5. **Expand `data/subject_phrases.py`**
   - Add more subject aliases as you discover them
   - Can be auto-generated from catalog if you have subject display names

### Low Priority
6. **Add MEETING/TOPIC fields** to catalog
   - Extend `build_atoms_index.py` to index meeting times and topics
   - Improves distance scoring for schedule-aware queries

## 🔍 Fallbacks & Error Handling

All code now gracefully handles missing files:

- **`extract_subjects()`**: Returns `([], [])` if `subject_phrases.py` missing
- **`extract_instructors()`**: Returns `([], [])` if `instructor_index.pkl` missing
- **`shortlist_classes()`**: Returns `[]` if `5000_w_desc.json` missing (with log warning)
- **`build_instructor_index.py`**: Creates stub index if CSV missing
- **`build_catalog_json.py`**: Creates mock catalog (50 courses) if CSV missing

## 🧪 Testing

Test the pipeline end-to-end:

```bash
# 1. Build data
make data

# 2. Start backend
cd backend
uvicorn app.main:app --reload

# 3. Test endpoint (in another terminal)
curl -X POST http://localhost:8000/plan/shortlist \
  -H "Content-Type: application/json" \
  -d '{
    "message": "intermediate CS after 11am, no Fridays, maybe distro 2",
    "profile": {
      "netid": "test",
      "majors": ["data-science-bs"],
      "minors": [],
      "classes_already_taken": [],
      "vocational_interests": [],
      "favorite_profs": [],
      "disliked_profs": [],
      "earliest_class_time": null,
      "locked_classes": []
    },
    "term_hint": "2025 Spring"
  }'
```

Expected: No crashes, parser returns constraints, shortlist may be empty until pipeline is fully implemented.

## 📁 Directory Structure

```
backend/app/
├── config/
│   └── paths.py                    # ✅ Created
├── data/                           # Source data (git-tracked)
│   ├── subject_phrases.py          # ✅ Created
│   ├── instructors.csv             # ✅ Created (sample)
│   ├── catalog_raw.csv             # ✅ Created (sample)
│   ├── program_requirements_v0.json # ✅ Created
│   ├── instructor_index.pkl         # ⚙️ Generated (run make data)
│   ├── 5000_w_desc.json            # ⚙️ Generated (run make data)
│   └── short_labels.json           # ⚙️ Generated (run make data)
├── data_gen/                       # Generated (git-ignored)
│   └── chroma/                     # ⚙️ Generated (run make data)
└── scripts/
    ├── build_instructor_index.py   # ✅ Created
    ├── build_catalog_json.py        # ✅ Created
    ├── build_atoms_index.py         # ✅ Created
    ├── build_short_labels.py       # ✅ Created
    └── README.md                    # ✅ Created
```

## 🎯 Next Steps

1. **Run `make data`** to generate all data files
2. **Test the parser** with sample queries
3. **Replace sample CSVs** with real data when available
4. **Implement `shortlist_classes()`** to integrate with existing scoring functions
5. **Test end-to-end** with real user queries

All infrastructure is in place! 🎉


