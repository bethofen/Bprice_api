import numpy as np
import pandas as pd
#@title def clean dataframe
def clean_data_frame(data_frame):
  if not isinstance(data_frame,pd.DataFrame):
    print("True")
  #cut out of open hight low close volume
  columns = data_frame.columns.tolist()
  columns = [i.lower() for i in columns]
  for i in columns:
    if i not in ['open', 'high', 'low', 'close', 'volume']:
      data_frame.drop([i], axis=1)
  #cut out of open hight low close volume
  print(columns)
  return data_frame.rename(str.lower, axis='columns')

#@title def get rsi14
def Get_Rsi(day,price):
    time = day
    #switch price to up or down
    Mainprice = []
    for i in range(0,len(price)-1):
        Mainprice.append(price[i+1] - price[i])
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
def Get_percen(price):
  ram_price = [0]
  for i in range(1,len(price)):
    ram_price.append((price[i-1]-price[i])/price[i-1] * 100)
  return ram_price

#@title def update dataframe insert
def up_date_dataframe(dataframe,listupdate):
  for i in listupdate:
    dataframe.insert(len(dataframe.columns.tolist()), i[0], i[1], True)
  return dataframe

#@title def clear float
def ClearFloatDF(dataframe,demical):
  dataframe = dataframe.applymap(lambda x: round(x, decimal) if isinstance(x, (int, float)) else x)
  return dataframe

def Get_ema(Period,price):
    period = Period
    ema = [0 for i in range(period-1)]
    ema.append(float("%.2f" % round(sum(price[:period]) / period, 2)))
    Multi = 2/(period+1)
    Multi = float(str(round(Multi, 5)))
    #Xema = (price[5] * Multi) + (ema[4] * (1-Multi))
    # print(type(price[period]))
    for i in range(len(price)-period):
        #print(price[period + i] * Multi) + (ema[(period-1)+i] * (1-Multi))
        ema.append(float(str(round((price[period + i] * Multi) + (ema[(period-1)+i] * (1-Multi)), 2))))
    return ema

def Get_sma(Period,price):
    period = Period
    sma = [0 for i in range(period-1)]
    for i in range(len(price)-period+1):
        #print(price[period + i] * Multi) + (ema[(period-1)+i] * (1-Multi))
        sma.append(float(str(round((sum(price[i:period+i]) /period), 2))))
    return sma


def Get_bollinger(Period,price):
    period = Period
    bollin = [0 for i in range(period-1)]
    for i in range(len(price)-period+1):
        bollram = float(str(round((sum(price[i:period+i]) /period), 2)))
        bollram2 = price[i:period+i]
        bollram2 = [(i-bollram) **2 for i in bollram2]
        bollram3 = sum(bollram2) / (period-1)
        bollin.append(float(str(round(math.sqrt(bollram3), 2))))
    return bollin


# Sd standard Deviation
def Get_boll_upband(Period,Price,trend,Sd=None,Ma=None):
    period = Period
    if Sd:
        boll = Sd
    else:
        boll = Get_bollinger(period,Price)
    if Ma:
        MA = Ma
    else:
        MA = Get_sma(Period,Price)
    bolltrend = []
    if trend == "UP":
        for i in range(len(Price)):
            bolltrend.append(float(str(round(MA[i] + (boll[i] * 2), 2))))
    elif trend == "LOW":
        for i in range(len(Price)):
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

def get_macd(ema12,ema26):
  macd = []
  for i in range(len(ema26)):
    macd.append(float(str(round((ema12[i] - ema26[i]), 2))))
  return macd

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
