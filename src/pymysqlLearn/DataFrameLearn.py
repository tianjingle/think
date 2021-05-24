import pandas as pd
from sqlalchemy import create_engine
import baostock as bs

lg = bs.login()
rs = bs.query_history_k_data_plus("sh.600567",
    "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
    start_date='1999-07-01', end_date='2020-10-18',
    frequency="d", adjustflag="3")

#### 打印结果集 ####
data_list = []
while (rs.error_code == '0') & rs.next():
    data_list.append(rs.get_row_data())
result = pd.DataFrame(data_list, columns=rs.fields)

##将数据写入mysql的数据库，但需要先通过sqlalchemy.create_engine建立连接,且字符编码设置为utf8，否则有些latin字符不能处理
engine = create_engine('mysql+pymysql://root:tianjingle@localhost:3307/noun?charset=utf8')
#插入数据库
result.to_sql(name = 'sh.600567',con = engine,if_exists = 'append',index = False,index_label = False)

