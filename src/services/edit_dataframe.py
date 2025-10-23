import pandas as pd
import pandas as pd

def clean_ohlcv(data: pd.DataFrame) -> pd.DataFrame:
    # First, make all column names lowercase
    df = data.rename(columns=str.lower)
    
    # Define the columns we want to keep
    ohlcv_cols = ['open', 'high', 'low', 'close', 'volume']
    
    # Check if all required columns exist in the renamed DataFrame
    missing_cols = [col for col in ohlcv_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"DataFrame is missing required columns: {missing_cols}")
        
    # Select and return only the columns we want
    return df[ohlcv_cols]



def round_dataframe(data: pd.DataFrame, decimals: int) -> pd.DataFrame:
    # The built-in round() method is highly optimized and ignores non-numeric columns.
    return data.round(decimals)