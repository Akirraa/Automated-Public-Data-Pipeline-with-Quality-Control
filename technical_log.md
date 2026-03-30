# Technical Log & Decision Record

## Step 0 & 1: Planning and Architecture Setup
- **Action**: Designed the pipeline utilizing CRISP-DM methodology.
- **Difficulty**: Bridging continuous execution into a standard script setup without complex orchestrators.
- **Technical Choice & Justification**: Used Python's `schedule` library running in a `while True` loop inside `main.py` instead of Apache Airflow to keep dependencies lightweight and fully python-script constrained, as requested.
- **Technical Choice & Justification**: Implemented a global `config.yaml` for thresholds, URLs, and paths to prevent magic strings and hardcoding inside the data manipulation functions.
- **Technical Choice & Justification**: Included this `technical_log.md` file explicitly to track progression and decision milestones simultaneously with the codebase per user request.

## Step 2 & 3: Ingestion and Cleaning
- **Action**: Created `ingest.py` and `clean.py` scripts.
- **Difficulty**: Handling missing values properly without breaking the dataset.
- **Technical Choice & Justification**: For metrics like `new_cases` and `new_deaths`, missing values are imputed as `0`, and negatives are clamped to `0` rather than dropped, preserving the timeline continuity for the specific country. Completely unidentifiable rows (missing `iso_code` or unparseable `date`) are dropped entirely.
- **Technical Choice & Justification**: Deduplication uses the composite key `['iso_code', 'date']` ensuring exactly one record per country per day.

## Step 4: Data Validation (Great Expectations)
- **Action**: Created `validate.py` embedding 10 strict data quality enforcement rules.
- **Difficulty**: Programmatically dynamic documentation generation inside a stateless pipeline.
- **Technical Choice & Justification**: Used an `ephemeral` DataContext combined with purely Pythonic configurations rather than the `great_expectations init` CLI boilerplate in order to preserve pipeline container portability and ensure absolute idempotency. DataDocs natively pushed to `expectations/`.

## Step 5: Modeling and Aggregation
- **Action**: Developed `aggregate.py` and `report.py` to calculate final metrics and strictly format the schema.
- **Difficulty**: Handling missing external metrics required for computed KPI's (e.g. `cases_per_million`, division by zero risks).
- **Technical Choice & Justification**: Added `population` implicitly to `clean.py` core extractions to eliminate extra joins. Sourced the top 20 rankings based on robust 7-day windows using `pd.Timedelta`, taking cumulative maximums for population and vaccination counts, and sums for daily metrics. 
- **Technical Choice & Justification**: `report.py` statically named `final_report.csv` ensures deterministic paths for Power BI dashboard automated linking, eliminating dynamic file path breaks in the BI platform when runs trigger daily.

## Step 6: Orchestration and Deployment
- **Action**: Wrote `main.py` weaving all modules together cleanly using functional imports.
- **Difficulty**: Managing global logging contexts sequentially across module boundaries so that all steps write to the same daily rotating file without duplication.
- **Technical Choice & Justification**: Reset default root loggers inside `setup_global_logging()` when `run_pipeline` triggers, ensuring both Stream and File handlers sink harmoniously to the dynamically generated daily log path `logs/pipeline_log_YYYYMMDD.txt`. 
- **Technical Choice & Justification**: Hard stops implemented smoothly. If Great Expectations evaluates `False`, `main.py` aborts the daily ingestion flow entirely preventing cascading BI metrics corruption or pipeline crash errors.

## Step 7: Web Application Scaling (React + FastAPI)
- **Action**: Replaced manual BI integrations with a programmatic fullstack Javascript frontend driven by a Python FastAPI backend.
- **Difficulty**: Coupling statically generated pipeline CSVs to dynamic RESTful HTTP delivery asynchronously.
- **Technical Choice & Justification**: `FastAPI` chosen over Django/Flask strictly for async I/O properties and minimal payload serving. Configured broad CORS middleware for friction-free bridging to the Vite React dev-server.
- **Technical Choice & Justification**: Discarded `Tailwind` for explicit Vanilla CSS implementing `Glassmorphism` rendering arrays using pure React Recharts mapping. This isolates UI complexity without locking the codebase into heavy utility-library compile times.

## Step 8: Universal Auto-ETL Overhaul
- **Action**: Completely decoupled the pipeline from the COVID-19 dataset assumptions, allowing generic arbitrary CSV processing explicitly requested by the user.
- **Difficulty**: Rendering statically typed React components (KPI bindings) against unknown variables securely without triggering `KeyError`/`undefined` loops.
- **Technical Choice & Justification**: Swapped `aggregate.py` to auto-detect categorical bounds (strings) and compute sums across auto-detected numerics simultaneously. `App.jsx` was rewritten utilizing functional array filtering (`typeof data[0][col] === 'number'`) to intercept whatever schema survives the ETL pipeline seamlessly ensuring visual parity regardless of underlying CSV context. Implemented a `multipart/form-data` endpoint triggering backend data scraping upon Dropzone executions natively bypassing the crontab scheduler cleanly.

## Step 9: Containerization & Documentation Wrap-Up
- **Action**: Created multi-stage `Dockerfile` and refined `README.md` to be purely technical and instructional.
- **Difficulty**: Containerizing dual independent architectures (Vite/Node + FastAPI/Python) cleanly via the explicitly requested singular `Dockerfile` rather than using `docker-compose.yml`.
- **Technical Choice & Justification**: Bootstrapped a Multi-stage build process. Built the React frontend in `node:18-alpine` asynchronously, copied just the `dist` folder directly into `python:3.10-slim`, and deployed a native `serve` node proxy. Bound the startup execution to concurrently host Uvicorn and Nginx/serve entirely on port 8000/5173 natively simulating localhost parity exactly as originally architected.
