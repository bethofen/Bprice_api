import pandas as pd
import numpy as np
def calculate_atr_optimized(data:pd.DataFrame, period:int=14)->pd.DataFrame:
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
    """
    
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
    atr = pd.DataFrame(true_range, index=data.index).rolling(
        window=period, 
        min_periods=1
    ).mean()
    
    return atr


def calculate_atr_wilder(data:pd.DataFrame, period:int=14)->pd.DataFrame:
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
    """
    # Input validation
    required_cols = ['high', 'low', 'close']
    if not all(col in data.columns for col in required_cols):
        raise ValueError(f"Data must contain columns: {required_cols}")
    
    # Calculate True Range
    high_low = data['high'] - data['low']
    high_prev_close = np.abs(data['high'] - data['close'].shift(1))
    low_prev_close = np.abs(data['low'] - data['close'].shift(1))
    
    true_range = np.maximum.reduce([high_low, high_prev_close, low_prev_close])
    tr_data = pd.DataFrame(true_range, index=data.index)
    
    # Wilder's smoothing: ATR = ((previous_ATR * (period-1)) + current_TR) / period
    # This is equivalent to EWM with alpha = 1/period
    atr = tr_data.ewm(alpha=1/period, adjust=False).mean()
    
    return atr


def calculate_atr_vectorized(data:pd.DataFrame, period:int=14)->pd.DataFrame:
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
    """
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
    
    return pd.DataFrame(atr_full, index=data.index)


def calculate_atr(data:pd.DataFrame, period:int=14, method:str='simple')->pd.DataFrame:
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
    """
    if method == 'simple':
        return calculate_atr_optimized(data, period)
    elif method == 'wilder':
        return calculate_atr_wilder(data, period)
    elif method == 'vectorized':
        return calculate_atr_vectorized(data, period)
    else:
        raise ValueError("Method must be 'simple', 'wilder', or 'vectorized'")
    

 