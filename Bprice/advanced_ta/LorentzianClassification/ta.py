import pandas as pd
import numpy as np

def lo_ema(data, period):
    if not isinstance(data, (list, tuple, pd.Series)):
        data = list(data)
    if len(data) < period:
        raise ValueError("Data length must be greater than or equal to the period.")
    
    ema = []
    multiplier = 2 / (period + 1)
    sma = sum(data[:period]) / period
    ema.append(sma)
    
    # Calculate EMA for the rest of the data
    for price in data[period:]:
        ema_value = (price - ema[-1]) * multiplier + ema[-1]
        ema.append(ema_value)
    
    # Fill initial period with NaN
    ema = [np.nan] * (period - 1) + ema
    
    # Return as DataFrame
    df = pd.DataFrame({'ema_'+str(period): ema})
    return df

def lo_sma(data, period):
    if not isinstance(data, (list, tuple, pd.Series)):
        data = list(data)
    if len(data) < period:
        raise ValueError("Data length must be greater than or equal to the period.")
    
    # Calculate SMA
    sma = [np.nan] * (period - 1)  # Fill with NaN for initial periods
    sma.extend([sum(data[i:i + period]) / period for i in range(len(data) - period + 1)])
    
    # Return as DataFrame
    df = pd.DataFrame({'sma'+str(period): sma})
    return df




def lo_rsi(data, period=14):
    if not isinstance(data, (list, tuple, pd.Series)):
        data = list(data)
    if len(data) < period + 1:
        raise ValueError("Data length must be greater than the specified period.")
    
    # Convert to Pandas Series for easier calculation
    data = pd.Series(data)
    
    # Calculate price changes
    delta = data.diff()
    
    # Separate gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Calculate average gain and loss using rolling mean
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    
    # Calculate the Relative Strength (RS)
    rs = avg_gain / avg_loss
    
    # Calculate the RSI
    rsi = 100 - (100 / (1 + rs))
    
    # Return as a DataFrame
    df = pd.DataFrame({'RSI': rsi})
    return df


def lo_cci(high, low, close, period=20):
    # Ensure inputs are valid
    if not all(isinstance(arr, (list, tuple, pd.Series)) for arr in [high, low, close]):
        raise ValueError("High, low, and close prices must be lists, tuples, or Pandas Series.")
    if len(high) != len(low) or len(low) != len(close):
        raise ValueError("High, low, and close prices must have the same length.")
    if len(high) < period:
        raise ValueError("Data length must be greater than or equal to the specified period.")
    
    # Convert to Pandas Series for easier calculation
    high = pd.Series(high)
    low = pd.Series(low)
    close = pd.Series(close)
    
    # Calculate the Typical Price
    typical_price = (high + low + close) / 3
    
    # Calculate the Simple Moving Average (SMA) of the Typical Price
    sma = typical_price.rolling(window=period).mean()
    
    # Calculate the Mean Deviation
    mean_deviation = typical_price.rolling(window=period).apply(
        lambda x: np.mean(np.abs(x - np.mean(x))), raw=True
    )
    
    # Calculate the CCI
    cci = (typical_price - sma) / (0.015 * mean_deviation)
    
    # Return as a DataFrame
    df = pd.DataFrame({'CCI': cci})
    return df




def lo_adx(high, low, close, window=14,get_di = False,fillna=False):
    # Calculate True Range (TR)
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Calculate +DM and -DM
    plus_dm = high.diff().clip(lower=0)
    minus_dm = low.diff().clip(upper=0).abs()

    # Smooth TR, +DM, and -DM using Wilder's method
    atr = tr.ewm(alpha=1/window, adjust=False).mean()
    plus_dm_smoothed = plus_dm.ewm(alpha=1/window, adjust=False).mean()
    minus_dm_smoothed = minus_dm.ewm(alpha=1/window, adjust=False).mean()

    # Calculate +DI and -DI
    plus_di = 100 * (plus_dm_smoothed / atr)
    minus_di = 100 * (minus_dm_smoothed / atr)

    # Calculate DX
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)

    # Calculate ADX
    adx = dx.ewm(alpha=1/window, adjust=False).mean()

    # Handle NaN values if needed
    if fillna:
        adx = adx.fillna(20)
        plus_di = plus_di.fillna(20)
        minus_di = minus_di.fillna(20)
    if get_di:
        
        return adx, plus_di, minus_di
    else:
        return adx




def lo_atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14, fillna: bool = False) -> pd.Series:

    # Calculate True Range (TR)
    close_shift = close.shift(1)
    tr1 = high - low
    tr2 = abs(high - close_shift)
    tr3 = abs(low - close_shift)
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # Calculate ATR using Wilder's smoothing method
    atr = true_range.ewm(alpha=1/window, adjust=False).mean()

    # Handle NaN values if needed
    if fillna:
        atr = atr.fillna(0)

    return pd.Series(atr, name="atr")
