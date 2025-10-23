<div align="center"> 
  # Bprice_api
  <h1> Bprice v3</h1>
  <p>Bprice api to deal with dataframe and add data or cal indicator</p>

# 🎯Price Analysis with Lorentzian Classification and Technical Indicators

## 📌 Overview

This project provides a framework for analyzing price data using various technical indicators and Lorentzian Classification. , and multiple functions are implemented to calculate key trading indicators.

## 🚀 Features

✅ **Lorentzian Classification**: A machine learning approach for trend analysis.  
✅ **Technical Indicators**: Includes RSI, EMA, MACD, SMA, Bollinger Bands, VWAP, ATR, CCI, ADX, and Supertrend.  
✅ **Data Cleaning**: Provides functionality to format and clean floating-point values.

## ⚙️ Installation

"pip install git+https://github.com/bethofen/Bprice_api.git"

</div>

## 🧹 Data Cleaning

```python
round_dataframe(df,2)
```

## 🧠 Applying Lorentzian Classification

```python
lc = LorentzianClassification(
df,
    settings=LorentzianClassification.Settings(
        source=df['close'],
        neighborsCount=21,
        maxBarsBack=4000,
        useDynamicExits=False
    ),
    filterSettings=LorentzianClassification.FilterSettings(
        useVolatilityFilter=True,
        useRegimeFilter=True,
        useAdxFilter=True,
        regimeThreshold=-0.1,
        adxThreshold=20,
        kernelFilter=LorentzianClassification.KernelFilter(
            useKernelSmoothing=False,
            lookbackWindow=21,
            relativeWeight=14.0,
            regressionLevel=50,
            crossoverLag=2
        )
    )
)
```

## 📊 Technical Indicators

```python
# 📈 RSI Calculation
rsi = calculate_rsi(data=df["close"], period=14)

# 📊 Percentage Change
percent_change = calculate_percent_change(start_prices=df["open"],end_prices=df["close"])

# 📉 EMA Calculation
calculate_ema(price_series=df["close"],period=14)

# 📈 MACD Calculation
calculate_macd(df['close'], short_period=12, long_period=26, signal_period=9)

# 📊 SMA Calculation
calculate_sma(data = df["close"],period=14)

# 📈 Bollinger Bands
calculate_bollinger_bands(price_series=df['close'],period=20)

# 📊 ATR Calculation
calculate_atr(data=df, period=14)

# 📉 CCI Calculation
calculate_cci(close=df["close"],high=df["high"],low=df["low"], period=20)

# 📈 ADX and DI Calculation
adx = calculate_adx( data=df,period=14)

# 📊 Supertrend Calculation
calculate_supertrend(df=df, atr_period=14, multiplier=3)
```
