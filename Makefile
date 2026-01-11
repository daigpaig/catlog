.PHONY: data data-from-paper data-from-csv all clean

# Build all data assets from Paper API JSON files (preferred)
data-from-paper:
	@echo "Building data assets from Paper API..."
	cd backend/app && python scripts/normalize_paper_schedule.py
	cd backend/app && python scripts/merge_plan_metadata.py
	cd backend/app && python scripts/build_instructor_index_from_schedule.py
	cd backend/app && python scripts/build_atoms_index.py
	cd backend/app && python scripts/build_short_labels.py
	@echo "Data build from Paper API complete!"

# Build all data assets from CSV files (fallback)
data-from-csv:
	@echo "Building data assets from CSV files..."
	cd backend/app && python scripts/build_instructor_index.py
	cd backend/app && python scripts/build_catalog_json.py
	cd backend/app && python scripts/build_atoms_index.py
	cd backend/app && python scripts/build_short_labels.py
	@echo "Data build from CSV complete!"

# Auto-detect: use Paper API if available, else fallback to CSV
data:
	@echo "Detecting data source..."
	@if [ -f backend/app/data/5000.json ]; then \
		echo "Found Paper API data, using Paper ingestion..."; \
		$(MAKE) data-from-paper; \
	else \
		echo "Paper API data not found, using CSV fallback..."; \
		$(MAKE) data-from-csv; \
	fi

# Clean generated data (keeps source files)
clean:
	@echo "Cleaning generated data..."
	rm -rf backend/app/data_gen/
	rm -f backend/app/data/*.pkl
	rm -f backend/app/data/5000_w_desc.json
	rm -f backend/app/data/short_labels.json
	@echo "Clean complete!"

# Rebuild everything from scratch
all: clean data


