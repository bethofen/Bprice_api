import pandas as pd
import numpy as np


def calculate_obv(df, ma_type="EMA", ma_length=14, bb_std=2.0):
    """
    คำนวณ OBV และเส้น Smoothing MA (เหมือนใน TradingView)

    :param df: DataFrame ที่มีคอลัมน์ 'close' และ 'volume'
    :param ma_type: ประเภทเส้นค่าเฉลี่ย ('EMA', 'SMA', 'SMA_BB', 'None')
    :param ma_length: ความยาวของเส้นค่าเฉลี่ย (เช่น 14, 20)
    :param bb_std: ค่า Standard Deviation (เฉพาะกรณีใช้ Bollinger Bands)
    :return: DataFrame ที่เพิ่มคอลัมน์ 'obv', 'obv_ma', 'obv_upper', 'obv_lower'
    """
    data = df.copy()

    # 1. คำนวณ OBV (Core Logic)
    # หาการเปลี่ยนแปลงราคา (Close ปัจจุบัน - Close ก่อนหน้า)
    price_change = data["close"].diff()

    # หาประจุ (+1 ถ้าขึ้น, -1 ถ้าลง, 0 ถ้าเท่าเดิม)
    direction = np.sign(price_change)

    # ถ้า direction เป็น NaN (แถวแรก) ให้แทนด้วย 0
    direction = direction.fillna(0)

    # คำนวณ OBV: ผลรวมสะสมของ (ทิศทาง * Volume)
    # *ใช้ .fillna(0) เพื่อป้องกัน Error ในแถวแรก
    data["obv"] = (direction * data["volume"]).cumsum()

    # 2. คำนวณ Smoothing MA (เส้นค่าเฉลี่ยของ OBV)
    data["obv_ma"] = np.nan
    data["obv_upper"] = np.nan
    data["obv_lower"] = np.nan

    if ma_type == "SMA":
        data["obv_ma"] = data["obv"].rolling(window=ma_length).mean()

    elif ma_type == "EMA":
        # ใช้สูตร EMA มาตรฐาน
        data["obv_ma"] = data["obv"].ewm(span=ma_length, adjust=False).mean()
    elif ma_type == "EMATREND":
        # ใช้สูตร EMA มาตรฐาน
        data["obv_ma"] = data["obv"].ewm(span=ma_length, adjust=False).mean()
        data["obv_trend"] = data["obv"] > data["obv_ma"]

    elif ma_type == "SMA_BB":  # SMA + Bollinger Bands
        sma = data["obv"].rolling(window=ma_length).mean()
        std = data["obv"].rolling(window=ma_length).std()

        data["obv_ma"] = sma
        data["obv_upper"] = sma + (std * bb_std)
        data["obv_lower"] = sma - (std * bb_std)

    return data
