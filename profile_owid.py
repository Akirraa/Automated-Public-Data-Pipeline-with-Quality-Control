import pandas as pd
import numpy as np
import json
import os

def profile_data(file_path):
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    
    # 1. Global Max Date (The "Latest Sync" point)
    global_max_date = df['date'].max()
    
    # 2. Tardiness Analysis (Taux de retard par pays)
    country_dates = df.groupby('location')['date'].max().reset_index()
    country_dates['days_behind'] = (global_max_date - country_dates['date']).dt.days
    tardiness = country_dates[country_dates['days_behind'] > 7].sort_values('days_behind', ascending=False)
    
    # 3. Completeness by Continent
    continents = df['continent'].unique()
    completeness = {}
    
    # Critical vs Secondary categorization (Manual list)
    critical_cols = [
        'iso_code', 'continent', 'location', 'date', 
        'total_cases', 'new_cases', 'total_deaths', 'new_deaths',
        'icu_patients', 'hosp_patients'
    ]
    
    for continent in continents:
        if pd.isna(continent): continue
        cont_df = df[df['continent'] == continent]
        stats = {}
        for col in df.columns:
            null_count = cont_df[col].isna().sum()
            completeness_rate = (1 - (null_count / len(cont_df))) * 100
            stats[col] = round(completeness_rate, 2)
        completeness[continent] = stats

    # 4. Critical vs Secondary Summary
    all_completeness = (1 - (df.isna().sum() / len(df))) * 100
    
    results = {
        "global_max": str(global_max_date),
        "tardiness_top_10": tardiness.head(10).astype(str).to_dict(orient="records"),
        "continent_completeness": completeness,
        "critical_cols": critical_cols,
        "global_completeness": all_completeness.to_dict()
    }
    
    with open("data/profiling_results.json", "w") as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    profile_data("data/raw/custom_upload.csv")
