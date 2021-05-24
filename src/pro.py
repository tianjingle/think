import tushare as ts
ts.set_token('f8b3f28da1e0f8eb79b7789b9ec7a6ceea9b8bfa68e5051bdff9c07d')
pro = ts.pro_api()
df = pro.trade_cal(exchange='', start_date='20180901', end_date='20181001', fields='exchange,cal_date,is_open,pretrade_date,turnover', is_open='0')