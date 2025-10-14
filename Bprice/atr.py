def cal_atr_optimized(data, period):
    """
    Calculate Average True Range (ATR) - Optimized Version
    
    ATR measures market volatility by calculating the average of true ranges
    over a specified period. True Range is the maximum of:
    1. High - Low
    2. |High - Previous Close|
    3. |Low - Previous Close|
    
    Parameters:
    -----------
    data : pandas.DataFrame
        OHLC data with columns: 'high', 'low', 'close'
    period : int
        Number of periods for ATR calculation
        
    Returns:
    --------
    pandas.Series : ATR values
    """
    import pandas as pd
    import numpy as np
    
    # Input validation
    required_cols = ['high', 'low', 'close']
    if not all(col in data.columns for col in required_cols):
        raise ValueError(f"Data must contain columns: {required_cols}")
    
    if period <= 0:
        raise ValueError("Period must be positive")
    
    if len(data) < period:
        raise ValueError(f"Data length ({len(data)}) must be >= period ({period})")
    
    # Calculate the three True Range components
    high_low = data['high'] - data['low']
    high_prev_close = np.abs(data['high'] - data['close'].shift(1))
    low_prev_close = np.abs(data['low'] - data['close'].shift(1))
    
    # Get True Range (maximum of the three components)
    # Using np.maximum.reduce is fastest for this operation
    true_range = np.maximum.reduce([high_low, high_prev_close, low_prev_close])
    
    # Calculate ATR using simple moving average
    atr = pd.Series(true_range, index=data.index).rolling(
        window=period, 
        min_periods=1
    ).mean()
    
    return atr


def cal_atr_wilder(data, period):
    """
    Calculate ATR using Wilder's Smoothing Method (more accurate)
    
    This is the original method used by J. Welles Wilder Jr.
    It uses exponential smoothing instead of simple moving average.
    
    Parameters:
    -----------
    data : pandas.DataFrame
        OHLC data with columns: 'high', 'low', 'close'
    period : int
        Number of periods for ATR calculation
        
    Returns:
    --------
    pandas.Series : ATR values using Wilder's method
    """
    import pandas as pd
    import numpy as np
    
    # Input validation
    required_cols = ['high', 'low', 'close']
    if not all(col in data.columns for col in required_cols):
        raise ValueError(f"Data must contain columns: {required_cols}")
    
    # Calculate True Range
    high_low = data['high'] - data['low']
    high_prev_close = np.abs(data['high'] - data['close'].shift(1))
    low_prev_close = np.abs(data['low'] - data['close'].shift(1))
    
    true_range = np.maximum.reduce([high_low, high_prev_close, low_prev_close])
    tr_series = pd.Series(true_range, index=data.index)
    
    # Wilder's smoothing: ATR = ((previous_ATR * (period-1)) + current_TR) / period
    # This is equivalent to EWM with alpha = 1/period
    atr = tr_series.ewm(alpha=1/period, adjust=False).mean()
    
    return atr


def cal_atr_vectorized(data, period):
    """
    Ultra-fast vectorized ATR calculation
    
    Uses pure numpy operations for maximum speed.
    Best for large datasets or real-time applications.
    
    Parameters:
    -----------
    data : pandas.DataFrame
        OHLC data with columns: 'high', 'low', 'close'
    period : int
        Number of periods for ATR calculation
        
    Returns:
    --------
    pandas.Series : ATR values
    """
    import pandas as pd
    import numpy as np
    
    # Convert to numpy arrays for speed
    high = data['high'].values
    low = data['low'].values
    close = data['close'].values
    
    # Calculate True Range components
    hl = high - low
    hc = np.abs(high[1:] - close[:-1])
    lc = np.abs(low[1:] - close[:-1])
    
    # True Range calculation
    tr = np.zeros(len(data))
    tr[0] = hl[0]  # First TR is just High-Low
    tr[1:] = np.maximum.reduce([hl[1:], hc, lc])
    
    # ATR calculation using numpy convolution (fastest rolling mean)
    atr = np.convolve(tr, np.ones(period)/period, mode='valid')
    
    # Pad with NaN for first (period-1) values
    atr_full = np.concatenate([np.full(period-1, np.nan), atr])
    
    return pd.Series(atr_full, index=data.index)


def Get_atr(data, period, method='simple'):
    """
    Comprehensive ATR function with multiple calculation methods
    
    Parameters:
    -----------
    data : pandas.DataFrame
        OHLC data with columns: 'high', 'low', 'close'
    period : int
        Number of periods for ATR calculation
    method : str, default='simple'
        Calculation method: 'simple', 'wilder', 'vectorized'
        
    Returns:
    --------
    pandas.Series : ATR values
    """
    if method == 'simple':
        return cal_atr_optimized(data, period)
    elif method == 'wilder':
        return cal_atr_wilder(data, period)
    elif method == 'vectorized':
        return cal_atr_vectorized(data, period)
    else:
        raise ValueError("Method must be 'simple', 'wilder', or 'vectorized'")
    


def atr_trailing_stop(df, entry_price, position_type, period=14, multiplier=3, old_stop=None):
    if entry_price is None:
        raise ValueError("entry_price must be provided and cannot be None.")
    if position_type not in ["BUY", "SELL"]:
        raise ValueError("position_type must be 'BUY' or 'SELL'.")
    
    # Calculate ATR
    atr = Get_atr(df, period)
    
    # Use the latest ATR value
    atr_value = atr.iloc[-1]
    
    if position_type == 'BUY':
        # Calculate new stop-loss for a long position
        new_stop = entry_price - atr_value * multiplier

        if old_stop is not None:
            new_stop = max(new_stop, old_stop)
    
    elif position_type == 'SELL':
        # Calculate new stop-loss for a short position
        new_stop = entry_price + atr_value * multiplier
        
        if old_stop is not None:
            new_stop = min(new_stop, old_stop)
    return int(new_stop)
