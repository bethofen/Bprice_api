import numpy as np
import pandas as pd
import math


#@title def get rsi14
def Get_Rsi(data, period=14):
    """Calculate RSI using pandas optimized operations."""
    import pandas as pd
    import numpy as np
    
    # Convert to pandas Series
    if not isinstance(data, pd.Series):
        data = pd.Series(data)
    
    # Calculate price changes
    delta = data.diff()
    
    # Separate gains and losses
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    
    # Use exponential weighted mean with alpha = 1/period (Wilder's method)
    alpha = 1.0 / period
    avg_gains = gains.ewm(alpha=alpha, adjust=False).mean()
    avg_losses = losses.ewm(alpha=alpha, adjust=False).mean()
    
    # Calculate RSI
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.fillna(0).round(2).tolist()

#@title def get percen
def Get_percen(open_prices, close_prices):
    """Calculate percentage change using vectorized operations."""
    import pandas as pd
    import numpy as np
    
    # Convert to numpy arrays for vectorized operations
    open_arr = np.array(open_prices)
    close_arr = np.array(close_prices)
    
    # Handle division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        result = np.where(open_arr == 0, 0, (close_arr - open_arr) / open_arr * 100)
    
    return result.round(2).tolist()

def Get_ema(data, period):
    """Fast EMA calculation using pandas."""
    import pandas as pd
    
    if isinstance(data, list):
        data = pd.Series(data)
    
    # Use pandas ewm (exponentially weighted moving average)
    ema = data.ewm(span=period, adjust=False).mean()
    
    # Add None padding for consistency
    result = [None] * (period - 1) + ema.iloc[period-1:].tolist()
    
    return result

def Get_macd(data, short_period=12, long_period=26, signal_period=9):
    if not isinstance(data, (list, tuple)):
        data = list(data)
    short_ema = Get_ema(data, short_period)
    long_ema = Get_ema(data, long_period)
    macd_line = [
        short - long if short is not None and long is not None else None
        for short, long in zip(short_ema, long_ema)
    ]
    macd_valid = [val for val in macd_line if val is not None]
    signal_line = Get_ema(macd_valid, signal_period)
    signal_line = [None] * (len(macd_line) - len(signal_line)) + signal_line

    # Calculate the MACD histogram (difference between MACD line and Signal line)
    macd_histogram = [
        macd - signal if macd is not None and signal is not None else None
        for macd, signal in zip(macd_line, signal_line)
    ]

    return macd_line, signal_line, macd_histogram


def Get_sma(data, period):
    """Fast SMA calculation using pandas rolling window."""
    import pandas as pd
    
    if isinstance(data, list):
        data = pd.Series(data)
    
    # Calculate rolling mean
    sma = data.rolling(window=period).mean()
    
    # Convert to list with proper formatting
    result = sma.round(2).tolist()
    
    return result


def Get_bollinger(data,period):
    bollin = [0 for i in range(period-1)]
    for i in range(len(data)-period+1):
        bollram = float(str(round((sum(data[i:period+i]) /period), 2)))
        bollram2 = data[i:period+i]
        bollram2 = [(i-bollram) **2 for i in bollram2]
        bollram3 = sum(bollram2) / (period-1)
        bollin.append(float(str(round(math.sqrt(bollram3), 2))))
    return bollin


# Sd standard Deviation
def Get_boll_upband(data,period,trend,Sd=None,Ma=None):
    if Sd:
        boll = Sd
    else:
        boll = Get_bollinger(data,period)
    if Ma:
        MA = Ma
    else:
        MA = Get_sma(data,period)
    bolltrend = []
    if trend == "UP":
        for i in range(len(data)):
            bolltrend.append(float(str(round(MA[i] + (boll[i] * 2), 2))))
    elif trend == "LOW":
        for i in range(len(data)):
            bolltrend.append(float(str(round(MA[i] - (boll[i] * 2), 2))))
    else:
        print("trend error")
    return bolltrend


def Get_VWap(close,high,low,volume):
#   close = btc_full_price['close'].values.tolist()
#   high = btc_full_price['high'].values.tolist()
#   low = btc_full_price['low'].values.tolist()
#   volume = btc_full_price['volume'].values.tolist()    
  SumTpv = 0.00
  SumVolune = 0.00
  Vwap = []
  for i in range(0,len(close)):
    SumTpv += ((close[i]+high[i]+low[i])/3)*volume[i]
    SumVolune += volume[i]
    Vwap.append(float(str(round((SumTpv/SumVolune), 2))))
  return Vwap

def Get_VWap2(btc_full_price):
  close = btc_full_price['close'].values.tolist()
  high = btc_full_price['high'].values.tolist()
  low = btc_full_price['low'].values.tolist()
  volume = btc_full_price['volume'].values.tolist()    
  SumTpv = 0.00
  SumVolune = 0.00
  Vwap = []
  for i in range(0,len(close)):
    SumTpv += ((close[i]+high[i]+low[i])/3)*volume[i]
    SumVolune += volume[i]
    Vwap.append(float(str(round((SumTpv/SumVolune), 2))))
  return Vwap



def Get_AdxandDi(High,Low,Close,GetDi = False,Float2 =False):
    def To14(idct):
        # Averageresult = [0 for i in range(13)]
        Averageresult = []
        Averageresult.append(sum(idct[0:14]))
        if Float2:
            for i in range(len(idct)-1):
                Averageresult.append(round(Averageresult[i]-(Averageresult[i]/14)+idct[i+13],2))
        else:
            for i in range(14,len(idct)):
                Averageresult.append(Averageresult[i-14]-(Averageresult[i-14]/14)+idct[i])
        return Averageresult
    def toAdx(Dx):
        Adx = [round(sum(Dx[0:14])/14,2)]
        for i in range(14,len(Dx)):
            Adx.append(round(((Adx[i-14]*13)+Dx[i])/14,2))
        return Adx


    def ToFloat2():
        #GET Tr
        Tr = [round(max(High[i] -Low[i],abs(High[i] -Close[i-1]),abs(Low[i]-Close[i-1])),2) for i in range(1,len(High))]
        # Get +-dm
        PlusDM =  [round(max(High[i]-High[i-1],0),2) if High[i]-High[i-1]>Low[i-1]-Low[i] else 0 for i in range(1,len(High))]
        MinusDM = [round(max(Low[i-1]-Low[i],0),2) if Low[i-1]-Low[i]>High[i]-High[i-1] else 0 for i in range(1,len(Low))]
        #Get +-dm tr average 14
        PlusDM14 = To14(PlusDM)
        MinusDM14 = To14(MinusDM)
        Tr14 =  To14(Tr)
        #Get +-di average 14
        bf = [0 for i in range(14)]
        PlusDi14  = [round(100*PlusDM14[i]/Tr14[i],2) for i in range(len(PlusDM14))]
        MinusDi14 = [round(100*MinusDM14[i]/Tr14[i],2) for i in range(len(PlusDM14))]
        #Get Dx and adx  adx is average14 Dx
        Dx = [round(100*(abs(PlusDi14[i]-MinusDi14[i])/(PlusDi14[i]+MinusDi14[i])),2) for i in range(len(PlusDi14))]
        Adx = toAdx(Dx)
        return Adx,PlusDi14,MinusDi14
    def NotFloat2():

        #GET Tr
        Tr = [max(High[i] -Low[i],abs(High[i] -Close[i-1]),abs(Low[i]-Close[i-1])) for i in range(1,len(High))]
        # Get +-dm
        PlusDM =  [max(High[i]-High[i-1],0) if High[i]-High[i-1]>Low[i-1]-Low[i] else 0 for i in range(1,len(High))]
        MinusDM = [max(Low[i-1]-Low[i],0) if Low[i-1]-Low[i]>High[i]-High[i-1] else 0 for i in range(1,len(Low))]
        #Get +-dm tr average 14
        PlusDM14  = To14(PlusDM)
        MinusDM14 = To14(MinusDM)
        Tr14      = To14(Tr)
        #Get +-di average 14
        PlusDi14  = [100*PlusDM14[i]/Tr14[i] for i in range(len(PlusDM14))]
        MinusDi14 = [100*MinusDM14[i]/Tr14[i] for i in range(len(PlusDM14))]
        #Get Dx and adx  adx is average14 Dx
        Dx = [100*(abs(PlusDi14[i]-MinusDi14[i])/(PlusDi14[i]+MinusDi14[i])) for i in range(len(PlusDi14))]
        Adx = toAdx(Dx)
        return Adx,PlusDi14,MinusDi14

    if Float2:
        Adx,PlusDi14,MinusDi14 = ToFloat2()
    else:
        Adx,PlusDi14,MinusDi14 = NotFloat2()
    empbf = [None for i in range(14)]
    empbfadx = [None for i in range(27)]
    if GetDi:
        return empbfadx + Adx,empbf + PlusDi14,empbf + MinusDi14
    else:
        return empbfadx + Adx
    
def Get_cci(close, high, low, period=20):
    tp = (np.array(high) + np.array(low)  + np.array(close) ) / 3
    sma = pd.Series(tp).rolling(window=period).mean()
    mad = pd.Series(tp).rolling(window=period).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)
    cci = (tp - sma) / (0.015 * mad)
    return cci.values

def Get_atr(data, period):
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


def Get_UT_Bot_Alerts(data, key_value=1, atr_period=10, use_heikin_ashi=False):
    import pandas as pd
    import numpy as np
    
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
    df = df.fillna(method='bfill').fillna(method='ffill')
    
    return df
# Example Usage:
# df = pd.read_csv('your_data.csv')
# df = UT_Bot_Alerts(df, a=1, c=10, h=False)
# print(df[['close', 'xATRTrailingStop', 'pos', 'buy', 'sell', 'barcolor']].tail())



def Get_Supertrend(df, atr_period=14, multiplier=3.0):
    """Calculate Supertrend indicator correctly."""
    import pandas as pd
    import numpy as np
    
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


def Get_avgHLOC(data, list_data):
    """Calculate average of specified columns for each row."""
    data = data.copy()
    data.columns = data.columns.str.lower()
    
    # Check if all required columns exist
    missing_cols = [col for col in list_data if col not in data.columns]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")
    
    # Method 2: Using pandas vectorized operations (เร็วมาก)
    return data[list_data].mean(axis=1).tolist()


def Get_heikin_ashi(df):
    df = df.copy()
    
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
