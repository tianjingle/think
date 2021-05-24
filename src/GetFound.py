import json

import requests
from prettytable import *


# def FundsItem(scrapy):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#
#     code = scrapy.Field()   # 基金代码
#     name = scrapy.Field()   # 基金名称
#     unitNetWorth = scrapy.Field()   # 单位净值
#     day = scrapy.Field()    # 日期
#     dayOfGrowth = scrapy.Field()  # 日增长率
#     recent1Week = scrapy.Field()    # 最近一周
#     recent1Month = scrapy.Field()   # 最近一月
#     recent3Month = scrapy.Field()   # 最近三月
#     recent6Month = scrapy.Field()   # 最近六月
#     recent1Year = scrapy.Field()    # 最近一年
#     recent2Year = scrapy.Field()    # 最近二年
#     recent3Year = scrapy.Field()    # 最近三年
#     fromThisYear = scrapy.Field()   # 今年以来
#     fromBuild = scrapy.Field()  # 成立以来
#     serviceCharge = scrapy.Field()  # 手续费
#     upEnoughAmount = scrapy.Field()     # 起够金额
#
#     pass

def get_url(url, params=None, proxies=None):
    rsp = requests.get(url, params=params, proxies=proxies)
    rsp.raise_for_status()
    return rsp.text


def start_requests():
    url = 'https://fundapi.eastmoney.com/fundtradenew.aspx?ft=pg&sc=1n&st=desc&pi=1&pn=5000&cp=&ct=&cd=&ms=&fr=&plevel=&fst=&ftype=&fr1=&fl=0&isab='
    html = get_url(url)
    return html


def parse_funds_list(response):
    # datas = response.body.decode('UTF-8')
    datas = response
    # 取出json部门
    datas = datas[datas.find('{'):datas.find('}') + 1]  # 从出现第一个{开始，取到}
    # 给json各字段名添加双引号
    datas = datas.replace('datas', '\"datas\"')
    datas = datas.replace('allRecords', '\"allRecords\"')
    datas = datas.replace('pageIndex', '\"pageIndex\"')
    datas = datas.replace('pageNum', '\"pageNum\"')
    datas = datas.replace('allPages', '\"allPages\"')

    jsonBody = json.loads(datas)
    jsonDatas = jsonBody['datas']
    table = PrettyTable()
    table.field_names = ['code', 'name', 'day', 'unitNetWorth', 'dayOfGrowth', 'recent1Week', 'recent1Month',
                         'recent3Month', 'recent6Month', 'recent1Year', 'recent2Year'
        , 'recent3Year', 'fromThisYear', 'fromBuild', 'serviceCharge', 'upEnoughAmount']
    for data in jsonDatas:
        fundsArray = data.split('|')
        table.add_row([fundsArray[0], fundsArray[1], fundsArray[3], fundsArray[4], fundsArray[5], fundsArray[6],
                      fundsArray[7], fundsArray[8], fundsArray[9], fundsArray[10], fundsArray[11]
                      , fundsArray[12], fundsArray[13], fundsArray[14], fundsArray[18], fundsArray[24]])
    return table


# fundsItem = FundsItem()
# fundsItem['code'] = fundsArray[0]
# fundsItem['name'] = fundsArray[1]
# fundsItem['day'] = fundsArray[3]
# fundsItem['unitNetWorth'] = fundsArray[4]
# fundsItem['dayOfGrowth'] = fundsArray[5]
# fundsItem['recent1Week'] = fundsArray[6]
# fundsItem['recent1Month'] = fundsArray[7]
# fundsItem['recent3Month'] = fundsArray[8]
# fundsItem['recent6Month'] = fundsArray[9]
# fundsItem['recent1Year'] = fundsArray[10]
# fundsItem['recent2Year'] = fundsArray[11]
# fundsItem['recent3Year'] = fundsArray[12]
# fundsItem['fromThisYear'] = fundsArray[13]
# fundsItem['fromBuild'] = fundsArray[14]
# fundsItem['serviceCharge'] = fundsArray[18]
# fundsItem['upEnoughAmount'] = fundsArray[24]

if __name__ == "__main__":
    response = start_requests()
    table=parse_funds_list(response)
    print(table)
