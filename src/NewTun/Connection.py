import configparser
class Connection:

    host = 'localhost'
    port = 3307
    user = 'root'
    passwd = 'tianjingle'
    db = 'noun'
    charset = 'utf8'

    def __init__(self):
        cf = configparser.ConfigParser()
        cf.read("config.ini")  # 读取配置文件，如果写文件的绝对路径，就可以不用os模块
        # secs = cf.sections()  # 获取文件中所有的section(一个配置文件中可以有多个配置，如数据库相关的配置，邮箱相关的配置，
        # # print(secs)
        # #
        # # options = cf.options("Mysql-Database")  # 获取某个section名为Mysql-Database所对应的键
        # # print(options)
        # #
        # # items = cf.items("Mysql-Database")  # 获取section名为Mysql-Database所对应的全部键值对
        # # print(items)

        self.host = cf.get("Mysql-Database", "host")  # 获取[Mysql-Database]中host对应的值
        self.user = cf.get("Mysql-Database", "user")  # 获取[Mysql-Database]中host对应的值
        self.passwd = cf.get("Mysql-Database", "passwd")  # 获取[Mysql-Database]中host对应的值
        self.db = cf.get("Mysql-Database", "db")  # 获取[Mysql-Database]中host对应的值
        self.charset = cf.get("Mysql-Database", "charset")  # 获取[Mysql-Database]中host对应的值
        # print(host)
