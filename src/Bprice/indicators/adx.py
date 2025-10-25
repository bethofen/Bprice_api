import pandas as pd
import numpy as np

def calculate_adx(data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    # 1. Input Validation
    required_cols = ['high', 'low', 'close']
    if not all(col in data.columns for col in required_cols):
        raise ValueError(f"Input DataFrame must contain columns: {required_cols}")

    # 2. Calculate True Range (TR) and Directional Movements (+DM, -DM)
    high = data['high']
    low = data['low']
    close = data['close']
    
    # Moves
    up_move = high.diff()
    down_move = low.diff() * -1 # Make down_move positive

    # +DM and -DM
    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)

    # True Range
    tr1 = high - low
    tr2 = np.abs(high - close.shift(1))
    tr3 = np.abs(low - close.shift(1))
    true_range = np.maximum.reduce([tr1, tr2, tr3])

    # 3. Smooth the values using Wilder's Smoothing (equivalent to ewm with alpha = 1/period)
    # This replaces all the custom "To14" and "toAdx" functions
    alpha = 1 / period
    atr = pd.Series(true_range).ewm(alpha=alpha, adjust=False).mean()
    plus_dm_smoothed = plus_dm.ewm(alpha=alpha, adjust=False).mean()
    minus_dm_smoothed = minus_dm.ewm(alpha=alpha, adjust=False).mean()

    # 4. Calculate Directional Indicators (+DI, -DI)
    # Handle division by zero by replacing it with 0
    with np.errstate(divide='ignore', invalid='ignore'):
        plus_di = 100 * (plus_dm_smoothed / atr)
        minus_di = 100 * (minus_dm_smoothed / atr)
        plus_di.replace([np.inf, -np.inf], 0, inplace=True)
        minus_di.replace([np.inf, -np.inf], 0, inplace=True)

    # 5. Calculate the Directional Index (DX)
    di_sum = plus_di + minus_di
    di_diff = np.abs(plus_di - minus_di)
    with np.errstate(divide='ignore', invalid='ignore'):
        dx = 100 * (di_diff / di_sum)
        dx.replace([np.inf, -np.inf], 0, inplace=True)

    # 6. Calculate the ADX by smoothing the DX
    adx = dx.ewm(alpha=alpha, adjust=False).mean()

    # 7. Combine all results into a single DataFrame
    adx_df = pd.DataFrame({
        f'ADX_{period}': adx,
        f'PLUS_DI_{period}': plus_di,
        f'MINUS_DI_{period}': minus_di
    })

    return adx_df.round(2)