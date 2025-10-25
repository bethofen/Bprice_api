import pandas as pd
import numpy as np
    
def calculate_ut_bot_alerts(data:pd.DataFrame, key_value:int=1, atr_period:int=10, use_heikin_ashi:bool=False)->pd.DataFrame:
    # Input validation
    required_columns = ['open', 'high', 'low', 'close']
    if not all(col in data.columns for col in required_columns):
        raise ValueError(f"Data must contain columns: {required_columns}")
    
    if len(data) < atr_period:
        raise ValueError(f"Data length must be >= ATR period ({atr_period})")
    
    # Create working copy
    df = data.copy()
    
    # Calculate ATR (True Range)
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift(1))
    low_close = np.abs(df['low'] - df['close'].shift(1))
    
    true_range = np.maximum.reduce([high_low, high_close, low_close])
    atr = pd.Series(true_range).rolling(window=atr_period, min_periods=1).mean()
    
    # Calculate nLoss (ATR * Key Value)
    nLoss = key_value * atr
    
    # Determine source price
    if use_heikin_ashi:
        # Heikin Ashi Close = (O + H + L + C) / 4
        src = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    else:
        src = df['close']
    
    # Initialize trailing stop array
    trailing_stop = np.zeros(len(df))
    trailing_stop[0] = src.iloc[0]  # Initialize first value
    
    # Calculate UT Bot trailing stop
    for i in range(1, len(df)):
        prev_stop = trailing_stop[i-1]
        prev_src = src.iloc[i-1]
        curr_src = src.iloc[i]
        curr_loss = nLoss.iloc[i]
        
        # UT Bot Algorithm Logic
        if curr_src > prev_stop and prev_src > prev_stop:
            # Both current and previous above stop = Uptrend continues
            # Raise the stop loss (but don't lower it)
            trailing_stop[i] = max(prev_stop, curr_src - curr_loss)
            
        elif curr_src < prev_stop and prev_src < prev_stop:
            # Both current and previous below stop = Downtrend continues  
            # Lower the stop loss (but don't raise it)
            trailing_stop[i] = min(prev_stop, curr_src + curr_loss)
            
        else:
            # Trend reversal detected
            if curr_src > prev_stop:
                # Price broke above stop = New uptrend
                trailing_stop[i] = curr_src - curr_loss
            else:
                # Price broke below stop = New downtrend
                trailing_stop[i] = curr_src + curr_loss
    
    # Add trailing stop to dataframe
    df['UT_TrailingStop'] = trailing_stop
    
    # Determine trend direction
    df['UT_Direction'] = src > df['UT_TrailingStop']
    
    # Generate buy/sell signals (trend change detection)
    df['UT_Buy'] = (df['UT_Direction'] == True) & (df['UT_Direction'].shift(1) == False)
    df['UT_Sell'] = (df['UT_Direction'] == False) & (df['UT_Direction'].shift(1) == True)
    
    # Create position column for easier backtesting
    df['UT_Position'] = 0
    current_position = 0
    
    for i in range(len(df)):
        if df['UT_Buy'].iloc[i]:
            current_position = 1
        elif df['UT_Sell'].iloc[i]:
            current_position = -1
        df.iloc[i, df.columns.get_loc('UT_Position')] = current_position
    
    # Add some additional useful columns
    df['UT_Distance'] = np.abs(src - df['UT_TrailingStop'])  # Distance from trailing stop
    df['UT_Distance_Pct'] = (df['UT_Distance'] / src) * 100  # Distance as percentage
    
    # Clean up - remove any NaN values
    df = df.bfill().ffill()
    
    return df
# Example Usage:
# df = pd.read_csv('your_data.csv')
# df = UT_Bot_Alerts(df, a=1, c=10, h=False)
# print(df[['close', 'xATRTrailingStop', 'pos', 'buy', 'sell', 'barcolor']].tail())



def calculate_supertrend(df:pd.DataFrame, atr_period:int=14, multiplier:float=3.0)->pd.DataFrame:
    """Calculate Supertrend indicator correctly."""
    df = df.copy()
    # Get price data
    high = df['high']
    low = df['low'] 
    close = df['close']
    
    # Calculate True Range properly
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = np.abs(high - prev_close)
    tr3 = np.abs(low - prev_close)
    
    true_range = np.maximum.reduce([tr1, tr2, tr3])
    
    # Calculate ATR using rolling mean (standard method)
    atr = pd.Series(true_range).rolling(window=atr_period, min_periods=1).mean()
    
    # Calculate HL2 (median price)
    hl2 = (high + low) / 2
    
    # Calculate basic upper and lower bands
    upper_band = hl2 + (multiplier * atr)
    lower_band = hl2 - (multiplier * atr)
    
    # Initialize final bands
    final_upper_band = upper_band.copy()
    final_lower_band = lower_band.copy()
    
    # Initialize supertrend
    supertrend = pd.Series([True] * len(df), index=df.index)
    
    # Calculate Supertrend
    for i in range(1, len(df)):
        # Current and previous indices
        curr_idx = df.index[i]
        prev_idx = df.index[i-1]
        
        # Calculate final bands with rules
        # Upper band: use lower of current and previous if trend is down
        if (upper_band.iloc[i] < final_upper_band.iloc[i-1]) or (close.iloc[i-1] > final_upper_band.iloc[i-1]):
            final_upper_band.iloc[i] = upper_band.iloc[i]
        else:
            final_upper_band.iloc[i] = final_upper_band.iloc[i-1]
            
        # Lower band: use higher of current and previous if trend is up  
        if (lower_band.iloc[i] > final_lower_band.iloc[i-1]) or (close.iloc[i-1] < final_lower_band.iloc[i-1]):
            final_lower_band.iloc[i] = lower_band.iloc[i]
        else:
            final_lower_band.iloc[i] = final_lower_band.iloc[i-1]
        
        # Determine trend direction
        if close.iloc[i] <= final_lower_band.iloc[i]:
            supertrend.iloc[i] = False  # Downtrend
        elif close.iloc[i] >= final_upper_band.iloc[i]:
            supertrend.iloc[i] = True   # Uptrend
        else:
            supertrend.iloc[i] = supertrend.iloc[i-1]  # Continue previous trend
    
    # Create Supertrend line
    supertrend_line = pd.Series(index=df.index, dtype=float)
    for i in range(len(df)):
        if supertrend.iloc[i]:
            supertrend_line.iloc[i] = final_lower_band.iloc[i]
        else:
            supertrend_line.iloc[i] = final_upper_band.iloc[i]
    
    # Add results to dataframe
    df['ATR'] = atr
    df['Supertrend'] = supertrend_line
    df['Supertrend_Direction'] = supertrend  # True = Uptrend, False = Downtrend
    df['ST_Upper_Band'] = final_upper_band
    df['ST_Lower_Band'] = final_lower_band
    
    return df
