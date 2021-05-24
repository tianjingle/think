import talib
import pymysql.cursors
import pandas as pd

from src.NewTun.Connection import Connection


class QueryStock:

    window=200
    code=''
    start=0
    isIndex=False

    def init(self,window):
        self.window=window+80

    def queryStock(self, stackCode):
        # 连接数据库
        connection=Connection()
        connect = pymysql.Connect(
            host=connection.host,
            port=connection.port,
            user=connection.user,
            passwd=connection.passwd,
            db=connection.db,
            charset=connection.charset
        )
        # 获取游标
        cursor = connect.cursor()
        # 查询数据
        sql = "SELECT * FROM `"+stackCode+"` where tradestatus=1 and turn is not null order by date desc limit %i"
        data = (self.window+80)
        cursor.execute(sql % data)
        fs = cursor.description
        filelds = []
        for field in fs:
            filelds.append(field[0])
        rs = cursor.fetchall()
        result = pd.DataFrame(list(rs), columns=filelds)
        # 关闭连接
        cursor.close()
        connect.close()
        #二维数组
        result=result.loc[:,['date','open','high','low','close','volume','turn','tradestatus'] ]

        #计算三十日均线
        result['M30']=talib.SMA(result['close'],30)
        result['T30']=talib.T3(result['close'],timeperiod=30, vfactor=0)
        result['tprice']=talib.TYPPRICE(result['high'],result['low'],result['close'])
        slowk, slowd = talib.STOCH(result['high'],result['low'],result['close'], fastk_period=9, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        slowj= list(map(lambda x,y: 3*x-2*y, slowk, slowd))
        result['k']=slowk
        result['d']=slowd
        result['j']=slowj
        result.date = range(0, len(result))  # 日期改变成序号
        return result