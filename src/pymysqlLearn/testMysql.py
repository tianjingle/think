import pymysql.cursors

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

# 插入数据
sql = "INSERT INTO test (id, name, age) VALUES ( '%s', '%s', %.2f )"
data = (8, 'zhangsan', 24)
cursor.execute(sql % data)
connect.commit()
print('成功插入', cursor.rowcount, '条数据')

# 修改数据
sql = "UPDATE test SET name = '%s' WHERE id = %i "
data = ('zhangsan', 1)
cursor.execute(sql % data)
connect.commit()
print('成功修改', cursor.rowcount, '条数据')

# 查询数据
sql = "SELECT id,name,age FROM test WHERE id = '%i' "
data = (1)
cursor.execute(sql % data)
for row in cursor.fetchall():
    print(row)
    # print("Name:%s\tSaving:%.2f" % row)
print('共查找出', cursor.rowcount, '条数据')

# 删除数据
sql = "DELETE FROM test WHERE id = %i LIMIT %d"
data = (2, 1)
cursor.execute(sql % data)
connect.commit()
print('成功删除', cursor.rowcount, '条数据')

# 事务处理
sql_1 = "UPDATE test SET age = age + 1000 WHERE id = 1 "
sql_2 = "UPDATE test SET age = age + 1000 WHERE id = 1 "
sql_3 = "UPDATE test SET age = age + 2000 WHERE id = 1 "

try:
    cursor.execute(sql_1)  # 储蓄增加1000
    cursor.execute(sql_2)  # 支出增加1000
    cursor.execute(sql_3)  # 收入增加2000
except Exception as e:
    connect.rollback()  # 事务回滚
    print('事务处理失败', e)
else:
    connect.commit()  # 事务提交
    print('事务处理成功', cursor.rowcount)

# 关闭连接
cursor.close()
connect.close()