import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def aggregate_metrics(cleaned_path: str, output_dir: str) -> dict:
    """
    Refined Universal Aggregation:
    - Extracts 'Latest Snapshot' per country for Entity summaries (Fair ranking)
    - Retains full temporal progression for time-series charts.
    - Prioritizes 'Per Million' or Normalized metrics for ranking where available.
    """
    try:
        logging.info("Dynamically grouping features for time-series and entities...")
        df = pd.read_csv(cleaned_path)
        
        # 1. Parse Temporal Column (already formatted but ensured)
        date_col = None
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                date_col = col
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                break
        
        # 2. Identify Geographic/Entity Column
        loc_col = 'location' if 'location' in df.columns else ('country' if 'country' in df.columns else None)
        
        # 3. Separate Categoricals and Numerics
        categoricals = [c for c in df.select_dtypes(include=['object', 'category']).columns if c != date_col]
        numerics = df.select_dtypes(include=['number']).columns.tolist()
        
        os.makedirs(output_dir, exist_ok=True)
        out_paths = {}

        if len(numerics) > 0 and loc_col:
            # --- 4. Entity Aggregation (LATEST SNAPSHOT) ---
            logging.info(f"Using {loc_col} as primary Entity for latest snapshotting.")
            
            # For each location, keep the last row with a non-null numeric value
            # This handles the case where latest date might not have all reporting yet.
            if date_col:
                # Sort by date for proper tail extraction
                df_sorted = df.sort_values([loc_col, date_col])
                # We prioritize normalized metrics for the aggregation if they exist.
                normalized_numerics = [c for c in numerics if 'per_million' in c.lower() or 'per_100' in c.lower() or 'rate' in col.lower()]
                
                # Snapshot: Latest record per country
                agg_entity = df_sorted.groupby(loc_col).tail(1).copy()
                
                # Prioritize numeric order: normalized columns first for ranking
                sorted_numerics = normalized_numerics + [col for col in numerics if col not in normalized_numerics]
                
                agg_entity.rename(columns={loc_col: 'entity_name'}, inplace=True)
                
                # Keep top 100 countries to ensure responsive UI
                agg_entity = agg_entity.sort_values(by=sorted_numerics[0], ascending=False).head(100)
            else:
                # Fallback to simple mean if temporal dimension is missing
                agg_entity = df.groupby(loc_col)[numerics].mean().reset_index()
                agg_entity.rename(columns={loc_col: 'entity_name'}, inplace=True)

            p1 = os.path.join(output_dir, "aggregated_by_entity.csv")
            agg_entity.to_csv(p1, index=False)
            out_paths['entity'] = p1
            
            # --- 5. Time Progression Aggregation (FULL TREND) ---
            if date_col:
                logging.info(f"Compiling temporal trend with {date_col} index.")
                time_df = df.dropna(subset=[date_col]).copy()
                time_df['period_str'] = time_df[date_col].dt.strftime('%Y-%m-%d')
                
                # Intelligent aggregation map
                agg_map = {}
                for col in numerics:
                    # Categorize: Rates/Intensity (Mean) vs Totals (Sum)
                    is_rate = any(x in col.lower() for x in ['_per_', 'rate', 'positive', 'index', 'reproduction'])
                    agg_map[col] = 'mean' if is_rate else 'sum'
                
                # Perform the mapped aggregation
                agg_time = time_df.groupby('period_str').agg(agg_map).reset_index()
                agg_time = agg_time.sort_values(by='period_str', ascending=True)
                agg_time.rename(columns={'period_str': 'time_period'}, inplace=True)
                
                p2 = os.path.join(output_dir, "aggregated_by_time.csv")
                agg_time.to_csv(p2, index=False)
                out_paths['time'] = p2
        else:
            logging.warning("Insufficient numeric or geographic columns to perform intelligent aggregation.")

        return out_paths
    except Exception as e:
        logging.error(f"Error during intelligent aggregation: {e}")
        raise
