# Data Rebuild Scripts

This directory contains scripts to rebuild missing data assets for the Northwestern Course AI project.

## Quick Start

### Using Paper API Data (Preferred)

If you have Paper API JSON files (`5000.json` and `plan.json`):

```bash
make data-from-paper
```

Or auto-detect (uses Paper if available, else CSV):

```bash
make data
```

### Using CSV Files (Fallback)

If you only have CSV files:

```bash
make data-from-csv
```

## Scripts

### Paper API Ingestion (Primary)

#### `normalize_paper_schedule.py`
Converts Paper API schedule JSON (`5000.json`) to normalized catalog format.
- **Input**: `data/5000.json` (Paper `ScheduleCourse[]` format)
- **Output**: `data/5000_w_desc.json` (normalized catalog)
- **Features**: 
  - Extracts course metadata (subject, number, title, school)
  - Parses meeting times and days
  - Extracts instructors from sections
  - Handles null/empty fields gracefully

#### `merge_plan_metadata.py`
Merges plan metadata (`plan.json`) into normalized catalog.
- **Input**: `data/plan.json` (Paper `PlanCourse[]` format)
- **Output**: Updates `data/5000_w_desc.json` with descriptions, distros, disciplines
- **Features**:
  - Merges course descriptions
  - Combines distro codes
  - Updates school information
  - Adds prerequisites

#### `build_instructor_index_from_schedule.py`
Builds instructor index directly from schedule data.
- **Input**: `data/5000.json`
- **Output**: `data/instructor_index.pkl`
- **Features**: Extracts all instructor names from schedule sections

#### `build_subject_phrases_from_paper.py` (Optional)
Generates subject aliases from Paper subject data.
- **Input**: `data/subjects.json` (if available from Paper API)
- **Output**: Updates `data/subject_phrases.py`
- **Status**: Optional - only runs if `subjects.json` exists

### CSV Fallback Scripts

#### `build_instructor_index.py`
Builds `data/instructor_index.pkl` from `data/instructors.csv`.
- **Input**: `data/instructors.csv` (columns: `first_name,last_name,canonical`)
- **Output**: `data/instructor_index.pkl`
- **Fallback**: Creates stub index if CSV is missing

#### `build_catalog_json.py`
Builds `data/5000_w_desc.json` from `data/catalog_raw.csv`.
- **Input**: `data/catalog_raw.csv`
- **Output**: `data/5000_w_desc.json`
- **Fallback**: Creates mock catalog (50 courses) if CSV is missing

### Common Scripts

#### `build_atoms_index.py`
Builds Chroma vector index for semantic search.
- **Input**: `data/5000_w_desc.json`
- **Output**: `data_gen/chroma/` (Chroma database)
- **Requirements**: `chromadb` package, OpenAI API key
- **Features**: Indexes TITLE, DESC_SENT, INSTRUCTOR, MEETING, TOPIC atoms

#### `build_short_labels.py`
Builds short title/description cache for efficient hydration.
- **Input**: `data/5000_w_desc.json`
- **Output**: `data/short_labels.json`
- **Fallback**: Returns error if catalog missing

## Dependencies

```bash
pip install chromadb openai python-dotenv
```

## Data File Formats

### Paper API Format

**`5000.json`** - Schedule data (array of `ScheduleCourse`):
```json
[
  {
    "i": "internal_id",
    "c": "WCAS",
    "t": "Course Title",
    "u": "COMP_SCI",
    "n": "111-0",
    "s": [/* ScheduleSection[] */]
  }
]
```

**`plan.json`** - Plan data:
```json
{
  "courses": [/* PlanCourse[] */],
  "legacy": [/* PlanCourse[] */]  // optional
}
```

**`PlanCourse`** fields:
- `i`: course_id (e.g., `"COMP_SCI 111-0"`)
- `n`: name/title
- `d`: description
- `s`: DistrosString (e.g., `"14"` → `["1","4"]`)
- `f`: DisciplinesString
- `c`: school
- `p`: prerequisites

### Normalized Output Format

**`5000_w_desc.json`** - Normalized catalog (array of course objects):
```json
[
  {
    "course_id": "COMP_SCI 111-0",
    "subject": "COMP_SCI",
    "number": "111-0",
    "title": "Introduction to Computer Science",
    "desc": "Course description...",
    "school": "WCAS",
    "level": 100,
    "distros": ["2"],
    "disciplines": [],
    "instructors": ["Jane Doe", "John Smith"],
    "meeting_text": "Mon/Wed/Fri 10:00–11:20",
    "sections": [/* normalized section data */]
  }
]
```

## Manual Tasks

1. **Provide Paper API data**: Ensure `data/5000.json` and `data/plan.json` are available
2. **Set OpenAI API key**: Required for `build_atoms_index.py` embeddings
   ```bash
   export OPENAI_API_KEY=your-key-here
   ```
3. **Update `data/program_requirements_v0.json`**: Replace with real requirement logic when available
4. **Optional**: Provide `data/subjects.json` from Paper API to auto-generate subject aliases

## File Structure

```
backend/app/
├── config/
│   └── paths.py                    # Path resolution utilities
├── data/                           # Source data (checked into git)
│   ├── subject_phrases.py          # Subject aliases
│   ├── 5000.json                   # Paper API schedule data
│   ├── plan.json                   # Paper API plan data
│   ├── subjects.json               # Paper API subject data (optional)
│   ├── instructors.csv             # CSV fallback (optional)
│   ├── catalog_raw.csv             # CSV fallback (optional)
│   ├── program_requirements_v0.json
│   ├── instructor_index.pkl         # ⚙️ Generated
│   ├── 5000_w_desc.json            # ⚙️ Generated
│   └── short_labels.json           # ⚙️ Generated
├── data_gen/                       # Generated (git-ignored)
│   └── chroma/                     # ⚙️ Generated
└── scripts/
    ├── normalize_paper_schedule.py  # ✅ Paper API ingestion
    ├── merge_plan_metadata.py       # ✅ Plan metadata merge
    ├── build_instructor_index_from_schedule.py  # ✅ Instructor index from Paper
    ├── build_subject_phrases_from_paper.py      # ✅ Subject aliases from Paper
    ├── build_instructor_index.py    # CSV fallback
    ├── build_catalog_json.py        # CSV fallback
    ├── build_atoms_index.py         # Vector index builder
    ├── build_short_labels.py        # Short labels cache
    └── README.md                    # This file
```

## Testing

Test the pipeline end-to-end:

```bash
# 1. Build data from Paper API
make data-from-paper

# 2. Verify output
python -c "
import json
from backend.app.config.paths import data_file
rows = json.loads(data_file('5000_w_desc.json').read_text())
print(f'Loaded {len(rows)} courses')
if rows:
    print(f'Sample: {rows[0][\"course_id\"]} - {rows[0][\"title\"]}')
"
```

## Troubleshooting

- **"5000.json not found"**: Ensure Paper API schedule data is in `backend/app/data/5000.json`
- **"plan.json not found"**: Warning only - plan metadata merge will be skipped
- **"chromadb not installed"**: Run `pip install chromadb`
- **"OpenAI API key not set"**: Set `OPENAI_API_KEY` environment variable
- **Large JSON files**: Scripts handle minified single-line JSON automatically
