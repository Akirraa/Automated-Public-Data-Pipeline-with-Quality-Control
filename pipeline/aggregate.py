import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def aggregate_metrics(cleaned_path: str, output_dir: str) -> dict:
    """
    Dynamically creates two distinct aggregations: Time-Series Progression and Entity Aggregations.
    """
    try:
        logging.info("Dynamically grouping features for time-series and entities...")
        df = pd.read_csv(cleaned_path)
        
        # Parse for temporal tracking
        date_col = None
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower() or 'year' in col.lower() or 'month' in col.lower():
                date_col = col
                # Try to enforce datetime safely
                try:
                    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                except:
                    pass
                break
                
        categoricals = [c for c in df.select_dtypes(include=['object', 'category']).columns if c != date_col]
        numerics = df.select_dtypes(include=['number']).columns
        
        os.makedirs(output_dir, exist_ok=True)
        out_paths = {}

        if len(numerics) > 0:
            # 1. Aggregate by Entity
            if len(categoricals) > 0:
                group_col = categoricals[0]
                logging.info(f"Auto-selected {group_col} as primary Entity.")
                agg_entity = df.groupby(group_col)[numerics].sum().reset_index()
                agg_entity = agg_entity.sort_values(by=numerics[0], ascending=False).head(50)
                agg_entity.rename(columns={group_col: 'entity_name'}, inplace=True)
            else:
                agg_entity = df.head(50)
                
            for col in numerics:
                if col in agg_entity:
                    agg_entity[col] = agg_entity[col].round(2)
            
            p1 = os.path.join(output_dir, "aggregated_by_entity.csv")
            agg_entity.to_csv(p1, index=False)
            out_paths['entity'] = p1
            
            # 2. Aggregate by Time Progression
            if date_col:
                logging.info(f"Auto-selected {date_col} as primary Time-Series index.")
                # Drop null dates securely
                time_df = df.dropna(subset=[date_col]).copy()
                
                # Format to extract simple readable strings for React Time-Series XAxis plotting
                time_df['period_str'] = time_df[date_col].dt.strftime('%Y-%m-%d')
                
                agg_time = time_df.groupby('period_str')[numerics].sum().reset_index()
                agg_time = agg_time.sort_values(by='period_str', ascending=True)
                agg_time.rename(columns={'period_str': 'time_period'}, inplace=True)
                
                for col in numerics:
                    if col in agg_time:
                        agg_time[col] = agg_time[col].round(2)
                        
                p2 = os.path.join(output_dir, "aggregated_by_time.csv")
                agg_time.to_csv(p2, index=False)
                out_paths['time'] = p2
            else:
                logging.warning("No temporal column detected for time-series.")

        return out_paths
    except Exception as e:
        logging.error(f"Error during dynamic aggregation: {e}")
        raise
