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


#@title def update dataframe insert
def up_date_dataframe(dataframe,listupdate):
  for i in listupdate:
    dataframe.insert(len(dataframe.columns.tolist()), i[0], i[1], True)
  return dataframe

#@title def clear float
def ClearFloatDF(dataframe, decimal):
    return dataframe.apply(lambda col: col.map(lambda x: round(x, decimal) if isinstance(x, (int, float)) else x))
