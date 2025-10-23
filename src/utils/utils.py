import pandas as pd
import numpy as np

def calculate_average(data: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    missing_cols = [col for col in columns if col not in data.columns]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")

    # Calculate the average, which results in a pandas Series
    average_series = data[columns].mean(axis=1)

    # Convert the Series to a DataFrame and name the column
    return pd.DataFrame({'average': average_series})


def calculate_percent_change(start_prices: pd.Series, end_prices: pd.Series) -> pd.DataFrame:
    change = (end_prices - start_prices) / start_prices * 100
    
    # Replace infinite values with 0 and fill NaNs
    result_series = change.replace([np.inf, -np.inf], 0).fillna(0).round(2)
    
    # Convert the Series to a DataFrame and name the column
    return pd.DataFrame({'percent_change': result_series})