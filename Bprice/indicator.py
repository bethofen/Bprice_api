import numpy as np
import pandas as pd
import math


#@title def get rsi14
def Get_Rsi(data,period):
    time = period
    #switch price to up or down
    Mainprice = []
    for i in range(0,len(data)-1):
        Mainprice.append(data[i+1] - data[i])
    #print(Mainprice)
    #price ot gain or losee
        i = 0
        gain = []
        loss = []
    for i in range(0,len(Mainprice)):
        if Mainprice[i] > 0:
            gain.append(np.around(Mainprice[i],2))
        else:
            gain.append(0)
        if Mainprice[i] < 0:
            loss.append(abs(np.around(Mainprice[i],2)))
        else:
            loss.append(0)
    i = 0
    xgain = []
    xloss = []
    xAvggain = 0.00
    xAvgloss = 0.00
    Avggain = []
    Avgloss = []
    Rs = []
    for i in range(0,time-1):
        xAvggain += gain[i]
        Avggain.append(np.around(gain[i], 2))
        xAvgloss += loss[i]
        Avgloss.append(np.around(loss[i], 2))
    Avggain13 = xAvggain / (time - 1)
    Avgloss13 = xAvgloss / (time - 1)
    i = 0
    Avggain.append(np.around((((Avggain13 * (time - 1)) + gain[(time - 1)]) / time),2))
    Avgloss.append(np.around((((Avgloss13 * (time - 1)) + loss[(time - 1)]) / time),2))
    for i in range(0,len(Mainprice)):
        if i >= time:
            Avggain.append(np.around((((Avggain[i-1] * (time - 1)) + gain[i]) / time),2))
            Avgloss.append(np.around((((Avgloss[i-1] * (time - 1)) + loss[i]) / time),2))
        if Avgloss[i] != 0:
            Rs.append(Avggain[i] / Avgloss[i])
        else:
            Rs.append(100)
    i = 0
    Rsi = []
    for i in range(0,len(Rs)):
        if Avgloss[i] == 0:
            Rsi.append(0)
        else:
            Rsi.append(100-(100/(1+Rs[i])))

    #float to .00
    Rsi = [float(str(round(i, 2))) for i in Rsi]
    Rsi.insert(0, 0.00)
    return Rsi

#@title def get percen
def Get_percen(open,close):
  ram_price = []
  for i in range(len(open)):
    #close come before because open 100 close 102 - = 2% up
    ram_price.append((close[i]-open[i])/open[i] * 100)
  return ram_price

def Get_ema(data, period):
    if not isinstance(data, (list, tuple)):
        data = list(data)
    if len(data) < period:
        raise ValueError("Data length must be greater than or equal to the period.")
    ema = []
    multiplier = 2 / (period + 1)
    sma = sum(data[:period]) / period
    ema.append(sma)
    # Calculate EMA for the rest of the data
    for price in data[period:]:
        ema_value = (price - ema[-1]) * multiplier + ema[-1]
        ema.append(ema_value)

    return [None] * (period - 1) + ema

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


def Get_sma(data,period):
    sma = [0 for i in range(period-1)]
    for i in range(len(data)-period+1):
        #print(price[period + i] * Multi) + (ema[(period-1)+i] * (1-Multi))
        sma.append(float(str(round((sum(data[i:period+i]) /period), 2))))
    return sma


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
    """Calculates the Average True Range (ATR)."""
    high_low = data['high'] - data['low']
    high_close = np.abs(data['high'] - data['close'].shift(1))
    low_close = np.abs(data['low'] - data['close'].shift(1))

    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=period, min_periods=1).mean()
    return atr

def Get_UT_Bot_Alerts(data, sen_key=1, atr=10, h=False):
    """
    UT Bot Alerts indicator converted from Pine Script to Python.

    Parameters:
    - data: DataFrame containing OHLC data with 'open', 'high', 'low', 'close' columns.
    - a: Sensitivity value (Key Value in Pine Script).
    - c: ATR Period.
    - h: Use Heikin Ashi candles (bool).

    Returns:
    - DataFrame with buy and sell signals, and trailing stop.
    """
    # Calculate ATR
    data['ATR'] = Get_atr(data, atr)
    nLoss = sen_key * data['ATR']

    # Heikin Ashi close or normal close
    data['src'] = data['close']
    if h:
        data['HA_close'] = (data['open'] + data['high'] + data['low'] + data['close']) / 4
        data['src'] = data['HA_close']

    # Initialize xATRTrailingStop
    data['xATRTrailingStop'] = 0.0
    for i in range(1, len(data)):
        prev_stop = data.loc[i - 1, 'xATRTrailingStop']
        prev_src = data.loc[i - 1, 'src']
        curr_src = data.loc[i, 'src']

        if curr_src > prev_stop and prev_src > prev_stop:
            data.loc[i, 'xATRTrailingStop'] = max(prev_stop, curr_src - nLoss.iloc[i])
        elif curr_src < prev_stop and prev_src < prev_stop:
            data.loc[i, 'xATRTrailingStop'] = min(prev_stop, curr_src + nLoss.iloc[i])
        else:
            data.loc[i, 'xATRTrailingStop'] = curr_src - nLoss.iloc[i] if curr_src > prev_stop else curr_src + nLoss.iloc[i]

    # Position signal based on crossover
    data['pos'] = 0
    for i in range(1, len(data)):
        prev_stop = data.loc[i - 1, 'xATRTrailingStop']
        curr_stop = data.loc[i, 'xATRTrailingStop']
        if data.loc[i - 1, 'src'] < prev_stop and data.loc[i, 'src'] > curr_stop:
            data.loc[i, 'pos'] = 1
        elif data.loc[i - 1, 'src'] > prev_stop and data.loc[i, 'src'] < curr_stop:
            data.loc[i, 'pos'] = -1
        else:
            data.loc[i, 'pos'] = data.loc[i - 1, 'pos']

    # Buy/Sell Signal
    data['EMA'] = Get_ema(data['src'], period=1)
    data['above'] = (data['EMA'] > data['xATRTrailingStop']).astype(int)
    data['below'] = (data['EMA'] < data['xATRTrailingStop']).astype(int)
    data['buy'] = (data['src'] > data['xATRTrailingStop']) & (data['above'].shift(1) < data['above'])
    data['sell'] = (data['src'] < data['xATRTrailingStop']) & (data['below'].shift(1) < data['below'])

    # Optional color columns to visualize bars
    # data['barcolor'] = np.where(data['src'] > data['xATRTrailingStop'], 'green',
    #                             np.where(data['src'] < data['xATRTrailingStop'], 'red', ''))

    data.drop(['xATRTrailingStop', 'pos', 'EMA', 'src'], axis=1, inplace=True)

    return data

# Example Usage:
# df = pd.read_csv('your_data.csv')
# df = UT_Bot_Alerts(df, a=1, c=10, h=False)
# print(df[['close', 'xATRTrailingStop', 'pos', 'buy', 'sell', 'barcolor']].tail())



def Get_Supertrend(df, atr_period, multiplier):

    high = df['high']
    low = df['low']
    close = df['close']

    # calculate ATR
    price_diffs = [high - low,
                   high - close.shift(),
                   close.shift() - low]
    true_range = pd.concat(price_diffs, axis=1)
    true_range = true_range.abs().max(axis=1)
    # default ATR calculation in supertrend indicator
    atr = true_range.ewm(alpha=1/atr_period,min_periods=atr_period).mean()
    # df['atr'] = df['tr'].rolling(atr_period).mean()

    # HL2 is simply the average of high and low prices
    hl2 = (high + low) / 2
    # upperband and lowerband calculation
    # notice that final bands are set to be equal to the respective bands
    final_upperband = upperband = hl2 + (multiplier * atr)
    final_lowerband = lowerband = hl2 - (multiplier * atr)

    # initialize Supertrend column to True
    supertrend = [True] * len(df)

    for i in range(1, len(df.index)):
        curr, prev = i, i-1

        # if current close price crosses above upperband
        if close[curr] > final_upperband[prev]:
            supertrend[curr] = True
        # if current close price crosses below lowerband
        elif close[curr] < final_lowerband[prev]:
            supertrend[curr] = False
        # else, the trend continues
        else:
            supertrend[curr] = supertrend[prev]

            # adjustment to the final bands
            if supertrend[curr] == True and final_lowerband[curr] < final_lowerband[prev]:
                final_lowerband[curr] = final_lowerband[prev]
            if supertrend[curr] == False and final_upperband[curr] > final_upperband[prev]:
                final_upperband[curr] = final_upperband[prev]

        # to remove bands according to the trend direction
        if supertrend[curr] == True:
            final_upperband[curr] = np.nan
        else:
            final_lowerband[curr] = np.nan
    df['Supertrend'] = supertrend
    df['Final Lowerband'] = final_lowerband
    df['Final Upperband'] = final_upperband
    return df

# data = Supertrend(data, 10, 3.0)
