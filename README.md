
<div align="center"> 
  # Bprice_api
  <h1> Bprice </h1>
  <p>Bprice api to deal with dataframe and add data or cal indicator</p>

# 🎯Price Analysis with Lorentzian Classification and Technical Indicators

## 📌 Overview

This project provides a framework for analyzing Bitcoin price data using various technical indicators and Lorentzian Classification. The dataset used is `btc_price.csv`, and multiple functions are implemented to calculate key trading indicators.

## 🚀 Features

✅ **Lorentzian Classification**: A machine learning approach for trend analysis.  
✅ **Technical Indicators**: Includes RSI, EMA, MACD, SMA, Bollinger Bands, VWAP, ATR, CCI, ADX, and Supertrend.  
✅ **Data Cleaning**: Provides functionality to format and clean floating-point values.

## ⚙️ Installation
"pip install git+https://github.com/bethofen/Bprice_api.git"
📥 Importing Required Modules

</div>
### 🧹 Data Cleaning

```python
ClearFloatDF(dataframe=df, decimal=2)
```

### 🧠 Applying Lorentzian Classification

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

### 📊 Technical Indicators

```python
# 📈 RSI Calculation
rsi = Get_Rsi(data=df["close"], period=14)

# 📊 Percentage Change
percent_change = Get_percen(open=df["open"], close=df["close"])

# 📉 EMA Calculation
ema = Get_ema(data=df["close"], period=14)

# 📈 MACD Calculation
macd = Get_macd(df['close'], short_period=12, long_period=26, signal_period=9)

# 📊 SMA Calculation
sma = Get_sma(data=df["close"], period=14)

# 📈 Bollinger Bands
bollinger = Get_bollinger(data=df['close'], period=20)

# 📊 Bollinger Upper Band
boll_upband = Get_boll_upband(data=df['close'], period=12, trend="UP")

# 📉 VWAP Calculation
vwap = Get_VWap(close=df["close"], high=df["high"], low=df["low"], volume=df["volume"])
vwap2 = Get_VWap2(df)

# 📊 ATR Calculation
atr = Get_atr(data=df, period=14)

# 📉 CCI Calculation
cci = Get_cci(close=df["close"], high=df["high"], low=df["low"], period=20)

# 📈 ADX and DI Calculation
adx, DiPlus, DiMinus = Get_AdxandDi(High=df["high"], Low=df["low"], Close=df["close"], GetDi=True)

# 📊 Supertrend Calculation
supertrend = Get_Supertrend(df=df, atr_period=14, multiplier=3)
```


## 🤝 Contributing

Feel free to contribute by submitting issues or pull requests.

## 📜 License

This project is licensed under the MIT License.

## ✨ Author

Your Name










