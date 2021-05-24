import baostock as bs
import pandas as pd

lg=bs.login()
rs=bs.query_stock_basic()
rs = bs.query_all_stock(day="2020-08-19")
data=[]
while(rs.error_code=='0')&rs.next():
    data.append(rs.get_row_data())
    print(rs.get_row_data())
result=pd.DataFrame(data,columns=rs.fields)
print(result)
result.to_csv("../data/basic1.csv")