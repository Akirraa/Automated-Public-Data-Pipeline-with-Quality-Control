# Data Profiling Report: Our World in Data COVID-19 Dataset

## 1. Schema Inspection
The dataset is primarily in CSV format and contains over 60 columns. For our reporting, the essential schema involves:
- `iso_code` (string): 3-letter country code.
- `location` (string): Geographical entity name.
- `date` (datetime): Observation date pattern YYYY-MM-DD.
- `new_cases` (float): Confirmed new cases (can contain anomalies).
- `new_deaths` (float): Confirmed new deaths.
- `total_vaccinations` (float): Total number of COVID-19 vaccination doses administered.

*Key columns isolated for processing:* `iso_code`, `location`, `date`, `new_cases`, `new_deaths`, `total_vaccinations`.

## 2. Completeness & Missing Value Analysis
- `iso_code` and `location`: Approaching 100% completeness.
- `date`: 100% completeness.
- Metrics (`new_cases`, `new_deaths`, `total_vaccinations`): Expected to have up to ~5% missing values depending on the specific country's reporting reliability, especially on weekends or during early periods of the pandemic.

## 3. Summary Statistics & Anomalies
- Some values for `new_cases` and `new_deaths` are historically updated and can be **negative** in the raw data due to corrections by health authorities.
- The pipeline will inherently clean out these negative anomalous values (clamping at `>= 0`).
