import requests
from bs4 import BeautifulSoup
from prettytable import *


def get_url(url, params=None, proxies=None):
    rsp = requests.get(url, params=params, proxies=proxies)
    rsp.raise_for_status()
    return rsp.text

def get_fund_total(code,start='', end=''):
    record = {'Code': code}
    url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx'
    params = {'type': 'lsjz', 'code': code, 'page': 10, 'per': 49, 'sdate': start, 'edate': end}
    html = get_url(url, params)
    temp =html.split(',')
    return temp[1].split(':')[1],temp[2].split(':')[1],temp[3].replace("};","").split(':')[1]

def get_fund_data(code, start='', end='',p=0):
    record = {'Code': code}
    url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx'
    params = {'type': 'lsjz', 'code': code, 'page': p+1, 'per': 49, 'sdate': start, 'edate': end}
    html = get_url(url, params)
    soup = BeautifulSoup(html, 'html.parser')
    # temp =html.split(',')
    # print(temp[1].split(':')[1])
    # print(temp[2].split(':')[1])
    # print(temp[3].replace("};","").split(':')[1])
    records = []
    tab = soup.findAll('tbody')[0]
    for tr in tab.findAll('tr'):
        if tr.findAll('td') and len((tr.findAll('td'))) == 7:
            record['Date'] = str(tr.select('td:nth-of-type(1)')[0].getText().strip())
            record['NetAssetValue'] = str(tr.select('td:nth-of-type(2)')[0].getText().strip())
            record['ChangePercent'] = str(tr.select('td:nth-of-type(4)')[0].getText().strip())
            records.append(record.copy())
    return records


def demo(code, start, end):
    table = PrettyTable()
    table.field_names = ['Code', 'Date', 'NAV', 'Change']
    table.align['Change'] = 'r'
    total, pages, currentpage = get_fund_total(code, start, end)
    print("total:"+total)
    for i in range(int(pages)):
        records = get_fund_data(code, start, end,i)
        for record in records:
            table.add_row([record['Code'], record['Date'], record['NetAssetValue'], record['ChangePercent']])
    return table


if __name__ == "__main__":
    print(demo('003358', '2010-03-02', '2020-09-30'))
