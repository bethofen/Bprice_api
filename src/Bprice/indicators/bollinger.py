import pandas as pd

def calculate_bollinger_bands(
    price_series: pd.Series,
    period: int = 20,
    std_dev: int = 2
) -> pd.DataFrame:
    # 1. คำนวณเส้นกลาง (Middle Band) ซึ่งก็คือ Simple Moving Average (SMA)
    middle_band = price_series.rolling(window=period).mean()

    # 2. คำนวณ Standard Deviation ในแต่ละช่วงเวลา
    # นี่คือสิ่งที่มาแทนที่ฟังก์ชัน Get_bollinger() ทั้งหมด
    rolling_std = price_series.rolling(window=period).std()

    # 3. คำนวณ Upper Band และ Lower Band
    upper_band = middle_band + (rolling_std * std_dev)
    lower_band = middle_band - (rolling_std * std_dev)

    # 4. รวมผลลัพธ์ทั้งหมดเข้าเป็น DataFrame เดียว
    bollinger_df = pd.DataFrame({
        f'BBM_{period}': middle_band,  # Middle Band
        f'BBU_{period}': upper_band,   # Upper Band
        f'BBL_{period}': lower_band    # Lower Band
    })

    return bollinger_df.round(2)