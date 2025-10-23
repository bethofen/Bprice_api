import pandas as pd
def calculate_rsi(data:pd.DataFrame, period :int=14)-> pd.DataFrame:
    """Calculate RSI using pandas optimized operations."""

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
    
    return rsi.fillna(0).round(2)