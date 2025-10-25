import pandas as pd

def calculate_sma(price_series: pd.Series, period: int = 14) -> pd.Series:
    return price_series.rolling(window=period).mean()

def calculate_ema(price_series: pd.Series, period: int = 14) -> pd.Series:
    return price_series.ewm(span=period, adjust=False).mean()

def calculate_dema(data_series: pd.Series, period: int=14) -> pd.Series:
    """
    คำนวณ DEMA จาก Series และคืนค่าเป็น DataFrame ใหม่
    """
    # คำนวณ EMA 2 ชั้น
    ema1 = data_series.ewm(span=period, adjust=False).mean()
    ema2 = ema1.ewm(span=period, adjust=False).mean()
    
    # คำนวณ DEMA
    dema = (2 * ema1) - ema2
    return dema


def calculate_tema(data_series: pd.Series, period: int=14) -> pd.Series:
    """
    คำนวณ TEMA จาก Series และคืนค่าเป็น DataFrame ใหม่
    """
    # คำนวณ EMA 3 ชั้น
    ema1 = data_series.ewm(span=period, adjust=False).mean()
    ema2 = ema1.ewm(span=period, adjust=False).mean()
    ema3 = ema2.ewm(span=period, adjust=False).mean()

    # คำนวณ TEMA
    tema = (3 * ema1) - (3 * ema2) + ema3
    return tema 

def calculate_macd(
    price_series: pd.Series,
    short_period: int = 12,
    long_period: int = 26,
    signal_period: int = 9
) -> pd.DataFrame:
    # 1. Calculate the Short and Long term EMAs
    short_ema = calculate_ema(price_series, period=short_period)
    long_ema = calculate_ema(price_series, period=long_period)

    # 2. Calculate the MACD Line
    macd_line = short_ema - long_ema

    # 3. Calculate the Signal Line (EMA of the MACD Line)
    signal_line = calculate_ema(macd_line, period=signal_period)

    # 4. Calculate the MACD Histogram
    macd_histogram = macd_line - signal_line

    # 5. Combine all Series into a single DataFrame
    macd_df = pd.DataFrame({
        f'MACD_{short_period}_{long_period}': macd_line,
        f'Signal_{signal_period}': signal_line,
        f'Histogram_{signal_period}': macd_histogram
    })

    return macd_df.round(4) # Round for cleaner output