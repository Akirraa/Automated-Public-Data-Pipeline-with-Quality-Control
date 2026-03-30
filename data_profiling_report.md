# Data Profiling Report: OWID COVID-19 Dataset

This report provides a manual and automated exploration of the Our World in Data (OWID) COVID-19 dataset, identifying critical features, missing data patterns, and reporting tardiness.

---

## 1. Column Criticality Analysis

We categorize the 67 available features into two tiers based on their utility for core analytical decision-making.

### **Tier 1: Critical Columns (High Business Value)**
| Column | Description | Why it's Critical |
| :--- | :--- | :--- |
| `location` / `iso_code` | Geographic identifiers | Fundamental for grouping and mapping. |
| `date` | Temporal identifier | Essential for time-series and trend analysis. |
| `new_cases` / `new_deaths` | Daily counts | Primary metrics for tracking pandemic velocity. |
| `total_cases` / `total_deaths` | Cumulative counts | Used for overall impact assessment. |
| `population` | Static demographic | Necessary for per-capita normalization. |

### **Tier 2: Secondary Columns (Contextual)**
- **Healthcare Capacity**: `icu_patients`, `hosp_patients`, `hospital_beds_per_thousand`. (Highly sparse).
- **Policy/Response**: `stringency_index`, `reproduction_rate`.
- **Economics**: `gdp_per_capita`, `extreme_poverty`.
- **Vaccination**: `total_vaccinations`, `people_fully_vaccinated`.

---

## 2. Completeness Rates by Continent

Completeness varies significantly by registry quality and regional infrastructure.

### **Variable Completeness (%)**
| Continent | Cases/Deaths | Testing | Vaccinations | Hospital Data |
| :--- | :--- | :--- | :--- | :--- |
| **Africa** | 100.0% | 12.0% | 6.6% | 0.8% |
| **Europe** | 93.8% | 29.8% | 29.8% | 35.1% |
| **Asia** | 93.4% | 24.4% | 22.7% | 3.7% |
| **North America** | 99.9% | 14.4% | 13.0% | 4.1% |
| **South America** | 99.9% | 29.1% | 27.6% | 2.2% |

> [!WARNING]
> **Hospitalization Data Gap**: Outside of Europe, hospital and ICU data is extremely sparse (<5% completeness), making healthcare burden analysis difficult for developing regions.

---

## 3. Missing Data Patterns

1.  **Reporting Frequency Decay**: Many countries transitioned from daily to weekly or monthly reporting in 2023, leading to "staircase" patterns in raw daily columns.
2.  **Testing Cessation**: Testing metrics (`total_tests`, `positive_rate`) show a sharp decline in completeness post-2022 as official testing sites were dismantled.
3.  **Vaccination Batch Reporting**: Vaccinations are often reported in large intermittent batches rather than daily, requiring smoothed (`_smoothed`) columns for accurate trend analysis.

---

## 4. Reporting Tardiness (Delayed Data)

We identify "Tardiness" as the delta between the global latest update (**2024-08-14**) and the country's last record.

### **Top Tardiness Observations**
| Location | Last Reported | Days Behind | Status |
| :--- | :--- | :--- | :--- |
| **Western Sahara** | 2022-04-20 | 847 | Likely Defunct |
| **Macao** | 2023-04-13 | 489 | Inactive |
| **Taiwan** | 2023-09-24 | 325 | Inactive |
| **Russia** | 2024-08-04 | 10 | Delayed (Active) |
| **Panama** | 2024-08-04 | 10 | Delayed (Active) |

---

## 5. Summary Recommendations

- **Use Smoothed Values**: Always use `_smoothed` versions of cases and deaths to account for weekend reporting lags and late catch-ups.
- **Per-Million Priority**: Given the massive population variance (e.g., India vs. Iceland), `_per_million` metrics are mandatory for fair cross-country comparison.
- **Interpolation Required**: Due to reporting gaps (especially in Africa/Asia), linear interpolation should be applied to daily counts before calculating rolling averages.
