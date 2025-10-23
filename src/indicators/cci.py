import pandas as pd
import numpy as np

def calculate_cci(data: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    required_cols = ['high', 'low', 'close']
    if not all(col in data.columns for col in required_cols):
        raise ValueError(f"Input DataFrame must contain columns: {required_cols}")

    # 2. Calculate Typical Price (TP) directly from DataFrame columns.
    # This keeps it as a pandas Series with the correct index.
    tp = (data['high'] + data['low'] + data['close']) / 3

    # 3. Calculate the Simple Moving Average of the Typical Price.
    sma = tp.rolling(window=period, min_periods=1).mean()

    # 4. Calculate the Mean Absolute Deviation (MAD).
    mad = tp.rolling(window=period, min_periods=1).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)

    # 5. Calculate the CCI.
    # We replace potential division-by-zero results with 0.
    cci_series = (tp - sma) / (0.015 * mad)
    cci_series = cci_series.replace([np.inf, -np.inf], 0).fillna(0)

    # 6. Return as a DataFrame with a descriptive column name.
    return pd.DataFrame({f'CCI_{period}': cci_series})