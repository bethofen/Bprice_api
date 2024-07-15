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
btc_price = clean_data_frame(btc_price)

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
  columns = dataframe.columns.tolist()
  print(columns)
  for col in columns:
    dataframe.loc[:,str(col)] = [round(i,demical) for i in dataframe[str(col)].values.tolist()]
  return dataframe
