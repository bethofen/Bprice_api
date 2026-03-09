import pandas as pd
import numpy as np


# def calculate_ut_bot_alerts(
#     data: pd.DataFrame,
#     key_value: int = 1,
#     atr_period: int = 10,
#     use_heikin_ashi: bool = False,
# ) -> pd.DataFrame:
#     # Input validation
#     required_columns = ["open", "high", "low", "close"]
#     if not all(col in data.columns for col in required_columns):
#         raise ValueError(f"Data must contain columns: {required_columns}")

#     if len(data) < atr_period:
#         raise ValueError(f"Data length must be >= ATR period ({atr_period})")

#     # Create working copy
#     df = data.copy()

#     # Calculate ATR (True Range)
#     high_low = df["high"] - df["low"]
#     high_close = np.abs(df["high"] - df["close"].shift(1))
#     low_close = np.abs(df["low"] - df["close"].shift(1))

#     true_range = np.maximum.reduce([high_low, high_close, low_close])
#     atr = pd.Series(true_range).rolling(window=atr_period, min_periods=1).mean()

#     # Calculate nLoss (ATR * Key Value)
#     nLoss = key_value * atr

#     # Determine source price
#     if use_heikin_ashi:
#         # Heikin Ashi Close = (O + H + L + C) / 4
#         src = (df["open"] + df["high"] + df["low"] + df["close"]) / 4
#     else:
#         src = df["close"]

#     # Initialize trailing stop array
#     trailing_stop = np.zeros(len(df))
#     trailing_stop[0] = src.iloc[0]  # Initialize first value

#     # Calculate UT Bot trailing stop
#     for i in range(1, len(df)):
#         prev_stop = trailing_stop[i - 1]
#         prev_src = src.iloc[i - 1]
#         curr_src = src.iloc[i]
#         curr_loss = nLoss.iloc[i]

#         # UT Bot Algorithm Logic
#         if curr_src > prev_stop and prev_src > prev_stop:
#             # Both current and previous above stop = Uptrend continues
#             # Raise the stop loss (but don't lower it)
#             trailing_stop[i] = max(prev_stop, curr_src - curr_loss)

#         elif curr_src < prev_stop and prev_src < prev_stop:
#             # Both current and previous below stop = Downtrend continues
#             # Lower the stop loss (but don't raise it)
#             trailing_stop[i] = min(prev_stop, curr_src + curr_loss)

#         else:
#             # Trend reversal detected
#             if curr_src > prev_stop:
#                 # Price broke above stop = New uptrend
#                 trailing_stop[i] = curr_src - curr_loss
#             else:
#                 # Price broke below stop = New downtrend
#                 trailing_stop[i] = curr_src + curr_loss

#     # Add trailing stop to dataframe
#     df["UT_TrailingStop"] = trailing_stop

#     # Determine trend direction
#     df["UT_Direction"] = src > df["UT_TrailingStop"]

#     # Generate buy/sell signals (trend change detection)
#     df["UT_Buy"] = (df["UT_Direction"] == True) & (df["UT_Direction"].shift(1) == False)
#     df["UT_Sell"] = (df["UT_Direction"] == False) & (
#         df["UT_Direction"].shift(1) == True
#     )

#     # Create position column for easier backtesting
#     df["UT_Position"] = 0
#     current_position = 0

#     for i in range(len(df)):
#         if df["UT_Buy"].iloc[i]:
#             current_position = 1
#         elif df["UT_Sell"].iloc[i]:
#             current_position = -1
#         df.iloc[i, df.columns.get_loc("UT_Position")] = current_position

#     # Add some additional useful columns
#     df["UT_Distance"] = np.abs(
#         src - df["UT_TrailingStop"]
#     )  # Distance from trailing stop
#     df["UT_Distance_Pct"] = (df["UT_Distance"] / src) * 100  # Distance as percentage

#     # Clean up - remove any NaN values
#     df = df.bfill().ffill()

#     return df


def calculate_ut_bot_alerts(
    data: pd.DataFrame,
    key_value: float = 1.0,  # ควรเป็น float
    atr_period: int = 10,
    use_heikin_ashi: bool = False,
) -> pd.DataFrame:
    required_columns = ["open", "high", "low", "close"]
    if not all(col in data.columns for col in required_columns):
        raise ValueError(f"Data must contain columns: {required_columns}")

    if len(data) < atr_period:
        raise ValueError(f"Data length must be >= ATR period ({atr_period})")

    df = data.copy()

    # --- 1. จัดการ Heikin Ashi ตั้งแต่ต้นทาง ---
    if use_heikin_ashi:
        ha_close = (df["open"] + df["high"] + df["low"] + df["close"]) / 4

        # สร้าง HA Open
        ha_open = np.zeros(len(df))
        ha_open[0] = (df["open"].iloc[0] + df["close"].iloc[0]) / 2

        # Numpy loop สำหรับ HA จะไวกว่า
        o_arr, c_arr = df["open"].values, df["close"].values
        for i in range(1, len(df)):
            ha_open[i] = (ha_open[i - 1] + ha_close.iloc[i - 1]) / 2

        ha_open_series = pd.Series(ha_open, index=df.index)

        # HA High / HA Low
        ha_high = pd.concat([df["high"], ha_open_series, ha_close], axis=1).max(axis=1)
        ha_low = pd.concat([df["low"], ha_open_series, ha_close], axis=1).min(axis=1)

        # เขียนทับค่าเพื่อไปคำนวณ ATR ต่อ
        df["open"], df["high"], df["low"], df["close"] = (
            ha_open_series,
            ha_high,
            ha_low,
            ha_close,
        )
        src = df["close"]
    else:
        src = df["close"]

    # --- 2. คำนวณ ATR แบบ TradingView (RMA) ---
    high_low = df["high"] - df["low"]
    high_close = np.abs(df["high"] - df["close"].shift(1))
    low_close = np.abs(df["low"] - df["close"].shift(1))

    # ป้องกัน NaN แท่งแรก เพื่อไม่ให้สูตรเพี้ยน
    high_close.iloc[0] = 0
    low_close.iloc[0] = 0

    true_range = np.maximum.reduce([high_low, high_close, low_close])

    # *** จุดสำคัญ *** ใช้ EWM (Exponential) จำลองสูตร RMA ของ TradingView
    atr = pd.Series(true_range).ewm(alpha=1 / atr_period, adjust=False).mean()

    nLoss = key_value * atr

    # --- 3. เพิ่มความเร็วด้วย Numpy Arrays ---
    src_arr = src.values
    loss_arr = nLoss.values
    trailing_stop = np.zeros(len(df))
    trailing_stop[0] = src_arr[0]

    # UT Bot Algorithm Logic
    for i in range(1, len(df)):
        prev_stop = trailing_stop[i - 1]
        prev_src = src_arr[i - 1]
        curr_src = src_arr[i]
        curr_loss = loss_arr[i]

        if curr_src > prev_stop and prev_src > prev_stop:
            trailing_stop[i] = max(prev_stop, curr_src - curr_loss)
        elif curr_src < prev_stop and prev_src < prev_stop:
            trailing_stop[i] = min(prev_stop, curr_src + curr_loss)
        else:
            if curr_src > prev_stop:
                trailing_stop[i] = curr_src - curr_loss
            else:
                trailing_stop[i] = curr_src + curr_loss

    df["UT_TrailingStop"] = trailing_stop
    df["UT_Direction"] = src > df["UT_TrailingStop"]

    # สร้างสัญญาณ
    df["UT_Buy"] = (df["UT_Direction"] == True) & (df["UT_Direction"].shift(1) == False)
    df["UT_Sell"] = (df["UT_Direction"] == False) & (
        df["UT_Direction"].shift(1) == True
    )

    # --- 4. จัดการ Position Column ด้วย Numpy (เร็วกว่า iloc) ---
    positions = np.zeros(len(df))
    current_pos = 0
    buy_arr = df["UT_Buy"].values
    sell_arr = df["UT_Sell"].values

    for i in range(len(df)):
        if buy_arr[i]:
            current_pos = 1
        elif sell_arr[i]:
            current_pos = -1
        positions[i] = current_pos

    df["UT_Position"] = positions
    df["UT_Distance"] = np.abs(src - df["UT_TrailingStop"])
    df["UT_Distance_Pct"] = (df["UT_Distance"] / src) * 100

    return df.bfill().ffill()


# Example Usage:
# df = pd.read_csv('your_data.csv')
# df = UT_Bot_Alerts(df, a=1, c=10, h=False)
# print(df[['close', 'xATRTrailingStop', 'pos', 'buy', 'sell', 'barcolor']].tail())


def calculate_supertrend(
    df: pd.DataFrame, atr_period: int = 10, multiplier: float = 3.0
) -> pd.DataFrame:
    """Calculate Supertrend indicator correctly using RMA for ATR."""
    df = df.copy()

    # Get price data
    high = df["high"]
    low = df["low"]
    close = df["close"]

    # --- 1. Calculate True Range ---
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    # ใช้ max ระหว่าง 3 ค่า
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # --- 2. Calculate ATR using RMA (Wilder's Smoothing) ---
    # จุดที่แก้: ใช้ ewm (Exponential Weighted Functions) เพื่อจำลอง RMA แทน rolling mean
    # alpha = 1 / period คือสูตรของ Wilder
    atr = true_range.ewm(
        alpha=1 / atr_period, min_periods=atr_period, adjust=False
    ).mean()

    # --- 3. Calculate Basic Bands ---
    hl2 = (high + low) / 2
    upper_band = hl2 + (multiplier * atr)
    lower_band = hl2 - (multiplier * atr)

    # Initialize final bands with 0.0 or generic values to avoid NaN propagation issues
    final_upper_band = upper_band.copy()
    final_lower_band = lower_band.copy()

    # Initialize supertrend direction
    # True = Uptrend, False = Downtrend
    supertrend = [True] * len(df)

    # --- 4. The Loop (Recursive Logic) ---
    # แปลงเป็น numpy array เพื่อความเร็วในการ loop (เร็วกว่า .iloc มาก)
    close_np = close.values
    upper_band_np = upper_band.values
    lower_band_np = lower_band.values
    final_upper_np = final_upper_band.values
    final_lower_np = final_lower_band.values

    for i in range(1, len(df)):
        # ถ้า ATR ยังเป็น NaN (ช่วงแรกของกราฟ) ให้ข้ามไป
        if np.isnan(upper_band_np[i]):
            continue

        # ถ้าก่อนหน้านี้เป็น NaN (เพิ่งเริ่มมีค่า) ให้ตั้งค่าเริ่มต้นเท่ากับ Basic Band
        if np.isnan(final_upper_np[i - 1]):
            final_upper_np[i] = upper_band_np[i]
            final_lower_np[i] = lower_band_np[i]
            continue

        # Logic: Final Upper Band
        # ถ้า Basic Upper Band ปัจจุบัน ต่ำกว่า Final Upper Band ก่อนหน้า -> ใช้ Basic (บีบลง)
        # หรือ ถ้า ราคาปิดก่อนหน้า ทะลุ Final Upper Band ก่อนหน้าไปแล้ว (เทรนด์เปลี่ยน) -> รีเซ็ตเป็น Basic
        if (upper_band_np[i] < final_upper_np[i - 1]) or (
            close_np[i - 1] > final_upper_np[i - 1]
        ):
            final_upper_np[i] = upper_band_np[i]
        else:
            final_upper_np[i] = final_upper_np[i - 1]

        # Logic: Final Lower Band
        # ถ้า Basic Lower Band ปัจจุบัน สูงกว่า Final Lower Band ก่อนหน้า -> ใช้ Basic (ดันขึ้น)
        # หรือ ถ้า ราคาปิดก่อนหน้า หลุด Final Lower Band ก่อนหน้า (เทรนด์เปลี่ยน) -> รีเซ็ตเป็น Basic
        if (lower_band_np[i] > final_lower_np[i - 1]) or (
            close_np[i - 1] < final_lower_np[i - 1]
        ):
            final_lower_np[i] = lower_band_np[i]
        else:
            final_lower_np[i] = final_lower_np[i - 1]

        # Logic: Determine Trend Direction
        # เช็คราคาปัจจุบันกับ Band เพื่อหาทิศทาง
        if supertrend[i - 1] == True:  # ถ้าเดิมเป็นขาขึ้น
            if close_np[i] <= final_lower_np[i]:
                supertrend[i] = False  # เปลี่ยนเป็นขาลง
            else:
                supertrend[i] = True  # ยังคงขาขึ้น
        else:  # ถ้าเดิมเป็นขาลง
            if close_np[i] >= final_upper_np[i]:
                supertrend[i] = True  # เปลี่ยนเป็นขาขึ้น
            else:
                supertrend[i] = False  # ยังคงขาลง

    # --- 5. Create Supertrend Line ---
    # สร้างเส้นเดียวเพื่อพลอตกราฟ
    supertrend_line = np.where(supertrend, final_lower_np, final_upper_np)

    # Add to DataFrame
    df["ATR"] = atr
    df["Supertrend"] = supertrend_line
    df["Supertrend_Direction"] = supertrend  # True=Green, False=Red

    # Optional: เก็บ Final Bands ไว้ดู Debug
    # df['ST_Upper_Band'] = final_upper_np
    # df['ST_Lower_Band'] = final_lower_np

    return df


# def kernel_regression_optimized(series, kernel='rational_quadratic',
#                                 lookback=20, alpha=1.0, length_scale=1.0,
#                                 level=0, show_color=True):

#     series = np.asarray(series, dtype=np.float64)
#     result = np.full_like(series, fill_value=np.nan, dtype=np.float64)
#     n = len(series)

#     # Pre-calculate kernel function
#     if kernel == 'rational_quadratic':
#         def kernel_fn(d2):
#             return (1 + d2 / (2 * alpha * length_scale ** 2)) ** (-alpha)
#     elif kernel == 'gaussian':
#         def kernel_fn(d2):
#             return np.exp(-d2 / (2 * length_scale ** 2))
#     else:
#         raise ValueError("Unknown kernel")

#     # Vectorized computation
#     for i in range(lookback + level, n):
#         start = i - lookback - level
#         end = i - level

#         y_window = series[start:end]

#         # Skip if NaN
#         if np.any(np.isnan(y_window)):
#             continue

#         # Vectorized distance calculation
#         x_diff = np.arange(lookback) - lookback  # relative positions
#         d2 = x_diff ** 2

#         weights = kernel_fn(d2)
#         weights /= weights.sum()

#         result[i] = np.dot(weights, y_window)

#     if show_color:
#         colors = ['green' if result[i] > result[i-1] else 'red'
#                   if not (np.isnan(result[i]) or np.isnan(result[i-1]))
#                   else None
#                   for i in range(len(result))]
#         return result, colors

#     return result
