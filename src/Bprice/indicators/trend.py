import pandas as pd
import numpy as np
import warnings

# Suppress pandas fragmentation warnings for large dataframe quantitative operations
warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)


def compute_heikin_ashi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes Heikin-Ashi synthetic candlestick data based on standard OHLC inputs.
    Strictly follows the recursive Munehisa Homma formulation where HA_Open relies on previous HA states.
    """
    ha_df = df.copy()

    # Standardize nomenclature for algorithmic consistency
    col_map = {col: col.lower() for col in ha_df.columns}
    ha_df = ha_df.rename(columns=col_map)

    required_cols = ["open", "high", "low", "close"]
    for col in required_cols:
        if col not in ha_df.columns:
            raise ValueError(
                f"Ingested DataFrame must strictly contain '{col}' column."
            )

    # Calculate HA_Close: Arithmetic mean of current OHLC
    ha_df["ha_close"] = (
        ha_df["open"] + ha_df["high"] + ha_df["low"] + ha_df["close"]
    ) / 4.0

    # Initialize HA_Open contiguous memory array for state-dependent iteration
    length = len(ha_df)
    ha_open = np.zeros(length)

    # BUG FIX 1: .iloc needs an index — use .iloc[0] for genesis bar
    ha_open[0] = (ha_df["open"].iloc[0] + ha_df["close"].iloc[0]) / 2.0

    ha_close_vals = ha_df["ha_close"].values

    # Iterative recursive formulation for subsequent periods
    for i in range(1, length):
        ha_open[i] = (ha_open[i - 1] + ha_close_vals[i - 1]) / 2.0

    ha_df["ha_open"] = ha_open

    # Vectorized computation of absolute extremes
    ha_df["ha_high"] = ha_df[["ha_open", "ha_close", "high"]].max(axis=1)
    ha_df["ha_low"] = ha_df[["ha_open", "ha_close", "low"]].min(axis=1)

    return ha_df


def calculate_ut_bot_alerts(
    data: pd.DataFrame,
    key_value: float = 1.0,
    atr_period: int = 10,
    use_heikin_ashi: bool = False,
) -> pd.DataFrame:
    """
    Translates the UT Bot Alerts Pine Script indicator into a robust Python environment.
    Computes volatility-scaled trailing stops and identifies discrete, actionable crossover signals.

    Parameters:
    - df (pd.DataFrame): OHLC standard pricing data.
    - key_value (float): Sensitivity multiplier (analogous to 'a' in Pine Script).
    - atr_period (int): Lookback period for True Range smoothing (analogous to 'c').
    - use_heikin_ashi (bool): Flag to utilize HA synthetic closing prices as the input signal.

    Returns:
    - pd.DataFrame: Appended dataframe containing actionable signals and risk parameters.
    """
    data = data.copy()
    col_map = {col: col.lower() for col in data.columns}
    data = data.rename(columns=col_map)

    # Determine execution Source Price series based on parameter toggle
    if use_heikin_ashi:
        ha_dataframe = compute_heikin_ashi(data)
        src = ha_dataframe["ha_close"].values
        # Use HA OHLC for True Range to replicate TradingView behavior exactly
        h_series = ha_dataframe["ha_high"]
        l_series = ha_dataframe["ha_low"]
        c_series = ha_dataframe["ha_close"]
    else:
        src = data["close"].values
        h_series = data["high"]
        l_series = data["low"]
        c_series = data["close"]

    # True Range (TR) Matrix Computation via Vectorization
    high_low = h_series - l_series
    high_close = np.abs(h_series - c_series.shift(1))
    low_close = np.abs(l_series - c_series.shift(1))
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    # Wilder's Smoothing / Running Moving Average (RMA) calculation for ATR
    # Emulates Pine Script's default atr() native function
    alpha = 1.0 / atr_period
    atr = tr.ewm(alpha=alpha, adjust=False).mean().values

    # Establish dynamic volatility threshold variable
    nLoss = key_value * atr

    # Pre-allocate memory arrays for state machine execution
    length = len(data)
    xATRTrailingStop = np.zeros(length)
    pos = np.zeros(length)

    # Explicit path-dependent state loop resolving Pine Script 'iff()' statements
    for i in range(1, length):
        prev_stop = xATRTrailingStop[i - 1]
        curr_src = src[i]
        prev_src = src[i - 1]
        curr_nLoss = nLoss[i]

        # 1. Trailing Stop Ratchet Logic emulation
        if curr_src > prev_stop and prev_src > prev_stop:
            xATRTrailingStop[i] = max(prev_stop, curr_src - curr_nLoss)
        elif curr_src < prev_stop and prev_src < prev_stop:
            xATRTrailingStop[i] = min(prev_stop, curr_src + curr_nLoss)
        elif curr_src > prev_stop:
            xATRTrailingStop[i] = curr_src - curr_nLoss
        else:
            xATRTrailingStop[i] = curr_src + curr_nLoss

        # 2. Market Posture State Tracking (1 for Long, -1 for Short)
        if prev_src < prev_stop and curr_src > prev_stop:
            pos[i] = 1
        elif prev_src > prev_stop and curr_src < prev_stop:
            pos[i] = -1
        else:
            pos[i] = pos[i - 1]

    # Epsilon Guard to prevent Stop equating Close price
    eps = 1e-10
    mask = xATRTrailingStop == src
    if mask.any():
        for i in np.where(mask)[0]:
            if i > 0 and src[i - 1] > xATRTrailingStop[i - 1]:
                xATRTrailingStop[i] = src[i] - eps
            else:
                xATRTrailingStop[i] = src[i] + eps

    # BUG FIX 2: Assign to column, not overwrite the entire DataFrame
    data["xATRTrailingStop"] = xATRTrailingStop
    data["Position"] = pos
    data["UT_TrailingStop"] = xATRTrailingStop
    # EMA(src, 1) is identity — just the source price itself
    data["ema_1"] = src

    # BUG FIX 3: Assign to new columns (Buy/Sell), compare against the correct column name
    data["entry_buy_signal"] = (
        (data["Position"] == 1)
        & (data["Position"].shift(1) != 1)
        & (data["ema_1"] > data["xATRTrailingStop"])
    )
    data["entry_sell_signal"] = (
        (data["Position"] == -1)
        & (data["Position"].shift(1) != -1)
        & (data["ema_1"] < data["xATRTrailingStop"])
    )

    return data


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

"""
UT Bot Alerts — Pine Script v4 → Python (merged & optimized)
=============================================================
Combines Pine-accurate ATR (on regular candles), correct bar-0 init,
epsilon guard, input validation, and extra analytics columns.

Usage:
    df = pd.read_csv("ohlcv.csv")  # needs: open, high, low, close
    result = ut_bot_alerts(df, key_value=1, atr_period=10)
"""

# import warnings


# def calculate_ut_bot_alerts(
#     data: pd.DataFrame,
#     key_value: float = 1.0,
#     atr_period: int = 10,
#     use_heikin_ashi: bool = False,
# ) -> pd.DataFrame:
#     """
#     UT Bot Alerts indicator.

#     Parameters
#     ----------
#     df : DataFrame with columns: open, high, low, close.
#     key_value : ATR multiplier — controls trailing stop sensitivity.
#     atr_period : ATR lookback period.
#     use_heikin_ashi : Use Heikin Ashi close as source (ATR stays on regular candles).

#     Returns
#     -------
#     DataFrame with columns:
#         xATR, nLoss, trailing_stop, direction, buy, sell,
#         bar_buy, bar_sell, position, distance, distance_pct
#     """
#     # ── Validation ─────────────────────────────────────────────────────
#     required = ["open", "high", "low", "close"]
#     missing = [c for c in required if c not in data.columns]
#     if missing:
#         raise ValueError(f"Missing columns: {missing}")
#     if len(data) < atr_period:
#         raise ValueError(f"Need >= {atr_period} rows (atr_period), got {len(data)}")

#     out = data.copy()

#     # ── Source (HA close or regular close) ──────────────────────────────
#     # Pine: atr() always uses REGULAR candles; only `src` switches to HA
#     if use_heikin_ashi:
#         ha_close = (data["open"] + data["high"] + data["low"] + data["close"]) / 4
#         ha_open = np.empty(len(data))
#         ha_open[0] = (data["open"].iat[0] + data["close"].iat[0]) / 2
#         ha_close_arr = ha_close.values
#         for i in range(1, len(data)):
#             ha_open[i] = (ha_open[i - 1] + ha_close_arr[i - 1]) / 2
#         src = ha_close.values
#     else:
#         src = data["close"].values.copy()

#     # ── ATR on REGULAR candles (Pine-accurate) ─────────────────────────
#     high = data["high"].values
#     low = data["low"].values
#     close = data["close"].values

#     prev_close = np.empty(len(data))
#     prev_close[0] = np.nan
#     prev_close[1:] = close[:-1]

#     tr = np.maximum(
#         high - low,
#         np.maximum(
#             np.abs(high - prev_close),
#             np.abs(low - prev_close),
#         ),
#     )
#     tr[0] = high[0] - low[0]  # bar 0: no prev_close → TR = H-L

#     # RMA (Wilder's smoothing) = EWM alpha=1/period
#     atr = pd.Series(tr).ewm(alpha=1 / atr_period, adjust=False).mean().values
#     n_loss = key_value * atr

#     # ── ATR Trailing Stop ──────────────────────────────────────────────
#     n = len(data)
#     ts = np.empty(n)
#     # Bar 0: Pine evaluates src > nz(ts[1],0) → True (price>0),
#     #         but src[1] is na → falls to 3rd branch → src - nLoss
#     ts[0] = src[0] - n_loss[0]

#     for i in range(1, n):
#         prev = ts[i - 1]
#         s = src[i]
#         s1 = src[i - 1]
#         nl = n_loss[i]

#         if s > prev and s1 > prev:
#             ts[i] = max(prev, s - nl)  # uptrend: ratchet up
#         elif s < prev and s1 < prev:
#             ts[i] = min(prev, s + nl)  # downtrend: ratchet down
#         elif s > prev:
#             ts[i] = s - nl  # flip to uptrend
#         else:
#             ts[i] = s + nl  # flip to downtrend

#     # ── Epsilon guard: nudge if ts == src exactly ──────────────────────
#     eps = 1e-10
#     mask = ts == src
#     if mask.any():
#         for i in np.where(mask)[0]:
#             if i > 0 and src[i - 1] > ts[i - 1]:
#                 ts[i] = src[i] - eps  # keep uptrend
#             else:
#                 ts[i] = src[i] + eps  # keep downtrend

#     # ── Signals ────────────────────────────────────────────────────────
#     direction = src > ts  # True = bullish

#     # Crossover: direction flips from False→True (buy) / True→False (sell)
#     prev_dir = np.empty(n, dtype=bool)
#     prev_dir[0] = False
#     prev_dir[1:] = direction[:-1]

#     buy = direction & ~prev_dir
#     sell = ~direction & prev_dir
#     bar_buy = direction  # bar coloring
#     bar_sell = ~direction

#     # ── Position tracking ──────────────────────────────────────────────
#     pos = np.zeros(n, dtype=np.int8)
#     for i in range(n):
#         if buy[i]:
#             pos[i] = 1
#         elif sell[i]:
#             pos[i] = -1
#         elif i > 0:
#             pos[i] = pos[i - 1]

#     # ── Distance metrics ───────────────────────────────────────────────
#     dist = np.abs(src - ts)
#     dist_pct = np.where(src != 0, (dist / src) * 100, 0.0)

#     # ── Assemble output ────────────────────────────────────────────────
#     idx = data.index
#     out["xATR"] = pd.Series(atr, index=idx)
#     out["nLoss"] = pd.Series(n_loss, index=idx)
#     out["UT_TrailingStop"] = pd.Series(ts, index=idx)
#     out["direction"] = pd.Series(direction, index=idx)
#     out["entry_buy_signal"] = pd.Series(buy, index=idx)
#     out["entry_sell_signal"] = pd.Series(sell, index=idx)
#     out["bar_buy"] = pd.Series(bar_buy, index=idx)
#     out["bar_sell"] = pd.Series(bar_sell, index=idx)
#     out["position"] = pd.Series(pos, index=idx)
#     out["distance"] = pd.Series(dist, index=idx)
#     out["distance_pct"] = pd.Series(dist_pct, index=idx)

#     # ── NaN audit ──────────────────────────────────────────────────────
#     output_cols = [
#         "UT_TrailingStop",
#         "direction",
#         "entry_buy_signal",
#         "entry_sell_signal",
#     ]
#     nan_count = out[output_cols].isna().sum().sum()
#     if nan_count > 0:
#         warnings.warn(
#             f"Found {nan_count} NaN(s) in output — check input data quality.",
#             UserWarning,
#             stacklevel=2,
#         )

#     return out


# Example Usage:
# data = pd.read_csv('your_data.csv')
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
