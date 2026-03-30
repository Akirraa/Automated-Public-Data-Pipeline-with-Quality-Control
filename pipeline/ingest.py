import os
import requests
import yaml
from datetime import datetime
import logging

# Set up basic logging for the module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(config_path: str = "config.yaml") -> dict:
    """
    Loads configuration settings from a YAML file.
    
    Args:
        config_path (str): The path to the configuration file relative to CWD.
        
    Returns:
        dict: Parsed configuration dictionary.
    """
    try:
        with open(config_path, "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        logging.error(f"Failed to load config file {config_path}: {e}")
        raise

def download_data(url: str, output_dir: str) -> str:
    """
    Downloads COVID-19 dataset from the given URL and saves it to the raw directory 
    with a timestamped filename.
    
    Args:
        url (str): The direct HTTP URL to download the CSV.
        output_dir (str): The path to the raw data directory.
        
    Returns:
        str: The file path where the raw dataset was stored.
    """
    try:
        logging.info(f"Starting download from {url}")
        # Note: Using stream to handle potentially large files gracefully, though standard get works.
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Ensure the directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate timestamp filename
        today_str = datetime.utcnow().strftime('%Y-%m-%d')
        filename = f"owid_{today_str}.csv"
        file_path = os.path.join(output_dir, filename)
        
        # Write content to file
        with open(file_path, 'wb') as file:
            file.write(response.content)
            
        logging.info(f"Successfully downloaded raw data to {file_path}")
        return file_path
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error during data ingestion: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error during data ingestion: {e}")
        raise

if __name__ == "__main__":
    # Test execution block
    try:
        config = load_config("../config.yaml")
        URL = config['pipeline']['dataset_url']
        RAW_DIR = os.path.join("..", config['paths']['raw_dir'])
        download_data(URL, RAW_DIR)
    except Exception as e:
        logging.error(f"Test execution failed: {e}")
