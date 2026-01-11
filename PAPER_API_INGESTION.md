# Paper API Ingestion - Complete

All scripts have been created to ingest Paper API JSON files and convert them to the normalized format your pipeline expects.

## ✅ Created Scripts

### Primary Paper API Scripts

1. **`scripts/normalize_paper_schedule.py`**
   - Converts `5000.json` (Paper `ScheduleCourse[]`) → `5000_w_desc.json`
   - Handles meeting times, days, instructors, sections
   - Null-safe throughout

2. **`scripts/merge_plan_metadata.py`**
   - Merges `plan.json` metadata into normalized catalog
   - Adds descriptions, distros, disciplines, prerequisites
   - Handles both `courses` and `legacy` arrays

3. **`scripts/build_instructor_index_from_schedule.py`**
   - Builds `instructor_index.pkl` directly from schedule data
   - No CSV needed - extracts from `5000.json` sections

4. **`scripts/build_subject_phrases_from_paper.py`** (Optional)
   - Auto-generates `subject_phrases.py` from Paper subject data
   - Only runs if `subjects.json` exists

### Updated Scripts

5. **`scripts/build_atoms_index.py`**
   - Updated to handle `meeting_text` and section `topic` fields
   - Works with normalized Paper API format

6. **`Makefile`**
   - Added `data-from-paper` target
   - Auto-detects Paper API data vs CSV fallback
   - `make data` now intelligently chooses source

## 🚀 Quick Start

### Step 1: Ensure Paper API Data Files

Place your Paper API JSON files in `backend/app/data/`:
- `5000.json` - Schedule data (required)
- `plan.json` - Plan metadata (optional but recommended)
- `subjects.json` - Subject data (optional)

### Step 2: Build Data

```bash
# Auto-detect (preferred)
make data

# Or explicitly use Paper API
make data-from-paper

# Or use CSV fallback
make data-from-csv
```

### Step 3: Verify

```bash
cd backend/app
python -c "
import json
from config.paths import data_file
rows = json.loads(data_file('5000_w_desc.json').read_text())
print(f'✅ Loaded {len(rows)} courses')
if rows:
    c = rows[0]
    print(f'Sample: {c[\"course_id\"]} - {c[\"title\"]}')
    print(f'  Instructors: {c.get(\"instructors\", [])}')
    print(f'  Distros: {c.get(\"distros\", [])}')
"
```

## 📋 Data Flow

```
Paper API JSON Files
    ↓
normalize_paper_schedule.py
    ↓
5000_w_desc.json (partial)
    ↓
merge_plan_metadata.py
    ↓
5000_w_desc.json (complete)
    ↓
build_instructor_index_from_schedule.py → instructor_index.pkl
build_atoms_index.py → data_gen/chroma/
build_short_labels.py → short_labels.json
```

## 🔍 Field Mappings

### Paper API → Normalized Format

| Paper Field | Normalized Field | Notes |
|------------|------------------|-------|
| `u` (subject) | `subject` | e.g., "COMP_SCI" |
| `n` (number) | `number` | e.g., "111-0" |
| `t` (title) | `title` | Course title |
| `c` (school) | `school` | e.g., "WCAS" |
| `s[]` (sections) | `sections[]` | Normalized section data |
| `s[].r[].n` | `instructors[]` | Extracted instructor names |
| `s[].m` + `s[].x` + `s[].y` | `meeting_text` | Merged meeting times |
| `plan.d` | `desc` | Course description |
| `plan.s` | `distros[]` | Distribution codes |
| `plan.f` | `disciplines[]` | Discipline codes |

### Meeting Time Parsing

- **Day codes**: `"024"` → `"Mon/Wed/Fri"`
- **Times**: `{h: 10, m: 0}` → `"10:00"`
- **Combined**: `"Mon/Wed/Fri 10:00–11:20"`

## 🛠️ Error Handling

All scripts include robust error handling:

- **Missing files**: Graceful warnings, continues with available data
- **Null fields**: All field accesses use `.get()` with defaults
- **Type checking**: Validates JSON structure before processing
- **Large files**: Handles minified single-line JSON automatically

## 📝 Integration Notes

### Existing Pipeline Compatibility

- ✅ `shortlist_classes.py` - Already reads `5000_w_desc.json`
- ✅ `extract_instructors()` - Already finds `instructor_index.pkl`
- ✅ `extract_subjects()` - Already uses `subject_phrases.py`
- ✅ `build_atoms_index.py` - Updated for Paper format fields

### New Fields Available

The normalized format now includes:
- `meeting_text`: Human-readable meeting schedule
- `sections[]`: Detailed section information
- `disciplines[]`: Discipline codes (if available)
- `prerequisites`: Prerequisite string (if available)

## 🧪 Testing

Test the full pipeline:

```bash
# 1. Build all data
make data-from-paper

# 2. Start backend
cd backend
uvicorn app.main:app --reload

# 3. Test endpoint
curl -X POST http://localhost:8000/plan/shortlist \
  -H "Content-Type: application/json" \
  -d '{
    "message": "intermediate CS after 11am, no Fridays",
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
    }
  }'
```

## 📚 Documentation

- **`scripts/README.md`** - Detailed script documentation
- **`DATA_REBUILD_SUMMARY.md`** - Original rebuild guide
- **This file** - Paper API ingestion guide

## 🎯 Next Steps

1. ✅ Run `make data-from-paper` to build all data assets
2. ✅ Verify output files exist and have correct structure
3. ✅ Test the parser with real queries
4. ✅ Implement `shortlist_classes()` to use the new data
5. ✅ Test end-to-end with real user queries

All infrastructure is ready! 🎉

