import pandas as pd

def create_df(extracted_data):
    """Converts extracted JSON data to Pandas DataFrame."""
    if "error" in extracted_data:
        return pd.DataFrame()
    
    df = pd.DataFrame(extracted_data)
    return df
