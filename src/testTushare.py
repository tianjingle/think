import tushare as ts
# data=ts.get_hist_data("600848",start="2018-01-23",end='2020-06-09');
# print(data)
# data=ts.get_hist_data('300274')
# kdate=ts.get_k_data("600663")
# print(kdate)

# import tushare as ts
"http://datainterface3.eastmoney.com/EM_DataCenter_V3/api/JGDYHZ/GetJGDYMX?js=datatable435798&tkn=eastmoney&secuCode=002541&sortfield=4&sortdirec=1&pageNum=2&pageSize=50&cfg=jgdyhz&p=2&pageNo=2&_=1610583145484"

import tushare as ts
ts.set_token('f8b3f28da1e0f8eb79b7789b9ec7a6ceea9b8bfa68e5051bdff9c07d')
pro = ts.pro_api()
df = pro.anns(start_date='20190401', end_date='20190402', year='2019')
df.to_csv('home/lipeng/Desktop/4.csv')
print(df)