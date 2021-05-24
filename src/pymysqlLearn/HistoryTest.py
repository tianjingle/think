import pymysql.cursors
import pandas as pd
# 连接数据库
connect = pymysql.Connect(
    host='localhost',
    port=3307,
    user='root',
    passwd='tianjingle',
    db='pymysql',
    charset='utf8'
)
# 获取游标
cursor = connect.cursor()
# 查询数据
sql = "SELECT * FROM history order by date desc"
data = (1)
cursor.execute(sql)
fs = cursor.description
filelds=[]
for field in fs:
    filelds.append(field[0])
rs=cursor.fetchall()
data_list = []
result = pd.DataFrame(list(rs),columns=filelds)
print(result)
# 关闭连接
cursor.close()
connect.close()