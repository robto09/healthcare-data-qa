"""
Script to download the Medical Cost Personal dataset from a public source
and save it to the data directory.
"""

import os
import pandas as pd
from pathlib import Path

def download_dataset():
    """Download the Medical Cost Personal dataset."""
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # URL for the dataset
    url = "https://raw.githubusercontent.com/stedy/Machine-Learning-with-R-datasets/master/insurance.csv"
    
    try:
        # Download and save the dataset
        df = pd.read_csv(url)
        output_path = data_dir / "insurance.csv"
        df.to_csv(output_path, index=False)
        print(f"Dataset downloaded successfully to {output_path}")
        print(f"Shape: {df.shape}")
        print("\nSample data:")
        print(df.head())
        
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        raise

if __name__ == "__main__":
    download_dataset()