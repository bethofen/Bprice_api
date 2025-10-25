import pandas as pd
def calculate_heikin_ashi(df:pd.DataFrame)->pd.DataFrame:
    # Ensure required columns are present
    if not {'open', 'high', 'low', 'close'}.issubset(df.columns):
        raise ValueError("Input DataFrame must contain 'open', 'high', 'low', 'close' columns.")
    # Initialize result DataFrame
    result = df.copy()
    # Calculate Heikin-Ashi Close
    result['ha_close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    
    # Calculate Heikin-Ashi Open
    result['ha_open'] = 0.0  # Initialize
    result.iloc[0, result.columns.get_loc('ha_open')] = df.iloc[0]['open']  # First row
    
    # Calculate subsequent ha_open values
    for i in range(1, len(result)):
        result.iloc[i, result.columns.get_loc('ha_open')] = (
            result.iloc[i-1]['ha_open'] + result.iloc[i-1]['ha_close']
        ) / 2
    
    # Calculate Heikin-Ashi High and Low
    result['ha_high'] = result[['high', 'ha_open', 'ha_close']].max(axis=1)
    result['ha_low'] = result[['low', 'ha_open', 'ha_close']].min(axis=1)
    
    # Determine trend
    result['trend'] = result.apply(
        lambda row: 'Bullish' if row['ha_close'] > row['ha_open'] else 'Bearish',
        axis=1
    )
    
    # Return the Heikin-Ashi OHLC data
    columns_to_return = ['ha_open', 'ha_high', 'ha_low', 'ha_close', 'trend']
    if 'datetime' in df.columns:
        columns_to_return.append('datetime')
    
    return result[columns_to_return].rename(columns={
        'ha_open': 'open',
        'ha_high': 'high',
        'ha_low': 'low',
        'ha_close': 'close'
    })
