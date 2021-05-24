import baostock as bs
import pandas as pd
import csv


baseStockFile="../data/basic_tushare.csv"
baseStockFile="../data/basic_tushare.csv"
csvFile=open(baseStockFile,"r",encoding="UTF-8")
reader=csv.reader(csvFile)

def baoStackReq(code,start):
    lg=bs.login()
    print(lg)
    data=bs.query_history_k_data(code,"date,code,open,high,low,close,preclose,"
                                             "volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,"
                                      "pbMRQ,psTTM,pcfNcfTTM,isST",start_date=start)
    targetData=[]
    while (data.error_code=="0")&data.next():
        targetData.append(data.get_row_data())
    result=pd.DataFrame(targetData,columns=data.fields)
    print(result)
    code=code.replace(".","")
    result.to_csv("../data/"+code+".csv")


for item in reader:
    print(item)
    line=item[0]
    if line=='':
        continue
    code=item[1]
    start=item[3]
    if int(line)<943 or len(start)<10:
        continue
    print(type(start))
    if code =='0':
        continue
    baoStackReq(code,start)