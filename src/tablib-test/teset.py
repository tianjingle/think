
import talib
import matplotlib.pyplot as plt
from matplotlib.pylab import date2num
import matplotlib.ticker as ticker  # 用于日期刻度定制
import baostock as bs
import pandas as pd
import datetime
from matplotlib import colors as mcolors  # 用于颜色转换成渲染时顶点需要的颜色格式
from matplotlib.collections import LineCollection, PolyCollection  # 用于绘制直线集合和多边形集合
from matplotlib.widgets import Cursor  # 处理鼠标

totalRmb=10000
handTotal=0
buysell=[]
myRmb=[]
def date_to_num(dates):
    num_time = []
    for date in dates:
        date_time = datetime.datetime.strptime(date,'%Y-%m-%d')
        num_date = date2num(date_time)
        num_time.append(num_date)
    return num_time

# 绘制蜡烛图
def format_date(x, pos=None):
    # 日期格式化函数，根据天数索引取出日期值
    return '' if x < 0 or x > len(date_tickers) - 1 else date_tickers[int(x)]

#EMV技术计算
def TEMV(data,fasttimeperiod,lasttimeperiod):
    temp=data
    temp['sub']=2
    emFront=talib.DIV(talib.ADD(temp['high'],temp['low']),temp['sub'])
    emFrontSub=talib.DIV(talib.ADD(temp['high'].shift(1),temp['low'].shift(1)),temp['sub'])
    emEnd=talib.DIV(talib.SUB(temp['high'],temp['low']),temp['volume'])
    em= talib.SUB(emFront,emFrontSub)*emEnd
    EMV=talib.SMA(em,fasttimeperiod)
    MAEMV=talib.SMA(EMV,lasttimeperiod)
    SubEmv=talib.SUB(EMV,MAEMV)
    return EMV,MAEMV,SubEmv

#策略
def BuySallForEmv(Emv,MaEmv,M30,T30,Tprice,K,D,J):
    BuyIndex=[]
    SallIndex=[]
    temp=pd.DataFrame({ 'emv' :Emv, 'maemv' :MaEmv,'m30':M30,'t30':T30,'tprice':Tprice,'k':K,'d':D,'j':J})
    print(temp)
    for index, row in temp.iterrows():
        if row['emv'] is None or row['t30'] is None or row['m30'] is None or row['k'] is None or row['d'] is None or row['j'] is None:
            continue
            #如果30日均线大于30日T3线就买入
        # if row['emv'] > 0 and row['maemv']>0 and row['emv']>row['maemv'] and row['tprice']>row['m30'] and row['m30']>row['t30']:
        if row['tprice']>row['m30'] and row['m30']>row['t30'] and row['k']<=20 and row['d']<20 and row['j']<20:
            BuyIndex.append(index)
        # elif row['emv']>=0 and row['maemv']>=0 and row['emv']<row['maemv']:
        elif row['tprice']<=row['m30'] and row['m30']>row['t30'] and row['k']>=80 and row['d']>=80 and row['j']>=80:
            SallIndex.append(index)
    return BuyIndex,SallIndex


#买股票
def Dobuy(index,price):
    global totalRmb, handTotal
    global buysell, myRmb
    currentRmb=price*100*1.002
    if totalRmb-currentRmb>0:
        totalRmb=totalRmb-currentRmb
        handTotal=handTotal+1
        buysell.append(index-start)
        myRmb.append(totalRmb+handTotal*100*price)
        print("总金额：" + str(totalRmb) + "   总手数" + str(handTotal)+"   账户总金额："+str(totalRmb+handTotal*100*price))
    else:
        print("资金不足")

#卖股票
def Dosell(index,price):
    global buysell, myRmb
    global totalRmb, handTotal
    if handTotal>0:
        currentRmb=handTotal*100*price*0.998
        totalRmb=totalRmb+currentRmb
        buysell.append(index-start)
        myRmb.append(totalRmb)
        handTotal=0
        print("总金额："+str(totalRmb)+"   总手数"+str(handTotal)+"   账户总金额："+str(totalRmb))
    else:
        print("不用再往出卖了")

#历史回测
def calculateHistory(doBuy,doSell):
    bySort=doBuy.index
    bySell=doSell.index
    doBuy['could']=1
    doBuy['sort']=bySort
    doSell['could']=-1
    doSell['sort']=bySell
    temp=pd.concat([doBuy,doSell])
    wang=temp.sort_values(by="sort", ascending=True)
    for index, row in wang.iterrows():
        print(str(index)+"  "+str(row['could'])+"  "+str(row['sort'])+"   "+str(row['low']))
        if row['could']==1:
            Dobuy(index,float(row['close']))
        elif row['could']==-1:
            price=float(row['close'])
            Dosell(index,price)




lg = bs.login()
rs = bs.query_history_k_data_plus("sh.600567",
    "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
    start_date='2019-07-01', end_date='2020-12-31',
    frequency="d", adjustflag="3")

#### 打印结果集 ####
data_list = []
while (rs.error_code == '0') & rs.next():
    data_list.append(rs.get_row_data())
result = pd.DataFrame(data_list, columns=rs.fields)
window=500
start=len(result)-window
#二维数组
result=result.loc[:,['date','open','high','low','close','volume'] ]
result=result[-window:]

slowk, slowd = talib.STOCH(result['high'],result['low'],result['close'], fastk_period=9, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
slowj= list(map(lambda x,y: 3*x-2*y, slowk, slowd))
#计算三十日均线
result['M30']=talib.SMA(result['close'],30)
result['T30']=talib.T3(result['close'],timeperiod=30, vfactor=0)
result['tprice']=talib.TYPPRICE(result['high'],result['low'],result['close'])
result['k']=slowk
result['d']=slowd
result['j']=slowj
print(result['close'])
# 计算KDJ值，数据存于DataFrame中
date_tickers=result.date.values
result.date = range(0, len(result))  # 日期改变成序号
matix = result.values  # 转换成绘制蜡烛图需要的数据格式(date, open, close, high, low, volume)
xdates = matix[:,0] # X轴数据(这里用的天数索引)
#总投资金额为5000元，买入信号出现时每次买一手。如果有卖出信号则全部卖出

t3Price = talib.T3(result['close'], timeperiod=30, vfactor=0)
Adxprice = talib.ADX(result['high'],result['low'],result['close'], timeperiod=5)
Adxrprice = talib.ADXR(result['high'],result['low'],result['close'], timeperiod=5)
emv,maemv,subemv=TEMV(result,5,10)
#策略
buy,sell=BuySallForEmv(emv,maemv,result['M30'],result['T30'],result['tprice'],result['k'],result['d'],result['j'])


realBuy=result.index.isin(buy)
doBuy=result[realBuy]
realSell=result.index.isin(sell)
doSell=result[realSell]

upperband, middleband, lowerband = talib.BBANDS(result['close'], timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
# 设置外观效果
plt.rc('font', family='Microsoft YaHei')  # 用中文字体，防止中文显示不出来
plt.rc('figure', fc='k')  # 绘图对象背景图
plt.rc('text', c='#800000')  # 文本颜色
plt.rc('axes', axisbelow=True, xmargin=0, fc='k', ec='#800000', lw=1.5, labelcolor='#800000',
       unicode_minus=False)  # 坐标轴属性(置底，左边无空隙，背景色，边框色，线宽，文本颜色，中文负号修正)
plt.rc('xtick', c='#d43221')  # x轴刻度文字颜色
plt.rc('ytick', c='#d43221')  # y轴刻度文字颜色
plt.rc('grid', c='#800000', alpha=0.9, ls=':', lw=0.8)  # 网格属性(颜色，透明值，线条样式，线宽)
plt.rc('lines', lw=0.8)  # 全局线宽

# 创建绘图对象和4个坐标轴
fig = plt.figure(figsize=(16, 8))
left, width = 0.05, 0.9
ax1 = fig.add_axes([left, 0.6, width, 0.4])  # left, bottom, width, height
ax2 = fig.add_axes([left, 0.5, width, 0.15], sharex=ax1)  # 共享ax1轴
ax3 = fig.add_axes([left, 0.35, width, 0.15], sharex=ax1)  # 共享ax1轴
ax4 = fig.add_axes([left, 0.2, width, 0.15], sharex=ax1)  # 共享ax1轴
ax5 = fig.add_axes([left, 0.05, width, 0.15], sharex=ax1)  # 共享ax1轴
plt.setp(ax1.get_xticklabels(), visible=False)  # 使x轴刻度文本不可见，因为共享，不需要显示
plt.setp(ax2.get_xticklabels(), visible=False)  # 使x轴刻度文本不可见，因为共享，不需要显示
plt.setp(ax3.get_xticklabels(), visible=False)  # 使x轴刻度文本不可见，因为共享，不需要显示

ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))  # 设置自定义x轴格式化日期函数
ax1.xaxis.set_major_locator(ticker.MultipleLocator(max(int(len(result) / 15), 5)))  # 横向最多排15个左右的日期，最少5个，防止日期太拥挤
# # 下面这一段代码，替换了上面注释的这个函数，因为上面的这个函数达不到同花顺的效果
opens, closes, highs, lows = matix[:, 1], matix[:, 4], matix[:, 2], matix[:, 3]  # 取出ochl值
avg_dist_between_points = (xdates[-1] - xdates[0]) / float(len(xdates))  # 计算每个日期之间的距离
delta = avg_dist_between_points / 4.0  # 用于K线实体(矩形)的偏移坐标计算
barVerts = [((date - delta, open), (date - delta, close), (date + delta, close), (date + delta, open)) for date, open, close in zip(xdates, opens, closes)]  # 生成K线实体(矩形)的4个顶点坐标
rangeSegLow = [((date, low), (date, min(open, close))) for date, low, open, close in  zip(xdates, lows, opens, closes)]  # 生成下影线顶点列表
rangeSegHigh = [((date, high), (date, max(open, close))) for date, high, open, close in zip(xdates, highs, opens, closes)]  # 生成上影线顶点列表
rangeSegments = rangeSegLow + rangeSegHigh  # 上下影线顶点列表
cmap = {
        True: mcolors.to_rgba('#000000', 1.0),
        False: mcolors.to_rgba('#54fcfc', 1.0)
   }  # K线实体(矩形)中间的背景色(True是上涨颜色，False是下跌颜色)
inner_colors = [cmap[opn < cls] for opn, cls in zip(opens, closes)]  # K线实体(矩形)中间的背景色列表
cmap = {True: mcolors.to_rgba('#ff3232', 1.0),
        False: mcolors.to_rgba('#54fcfc', 1.0)}  # K线实体(矩形)边框线颜色(上下影线和后面的成交量颜色也共用)
updown_colors = [cmap[opn < cls] for opn, cls in zip(opens, closes)]  # K线实体(矩形)边框线颜色(上下影线和后面的成交量颜色也共用)列表
#
ax1.add_collection(LineCollection(rangeSegments, colors=updown_colors, linewidths=0.5,antialiaseds=False))
# 生成上下影线的顶点数据(颜色，线宽，反锯齿，反锯齿关闭好像没效果)
ax1.add_collection(PolyCollection(barVerts, facecolors=inner_colors, edgecolors=updown_colors, antialiaseds=False,linewidths=0.5))
# 生成多边形(矩形)顶点数据(背景填充色，边框色，反锯齿，线宽)

# 绘制均线
mav_colors = ['#ffffff', '#d4ff07', '#ff80ff', '#00e600', '#02e2f4', '#ffffb9', '#2a6848']  # 均线循环颜色
# mav_period = [5, 10, 20, 30, 60, 120, 180]  # 定义要绘制的均线周期，可增减
mav_period = [30]  # 定义要绘制的均线周期，可增减
# mav_period = [5]  # 定义要绘制的均线周期，可增减
n = len(result)
for i in range(len(mav_period)):
    if n >= mav_period[i]:
        mav_vals = result['close'].rolling(mav_period[i]).mean().values
        ax1.plot(xdates, mav_vals, c=mav_colors[i % len(mav_colors)], label='MA' + str(mav_period[i]))
for index, row in doBuy.iterrows():
    ax1.scatter(index-start, float(row['close']), color="Y", marker="*")
for index, row in doSell.iterrows():
    ax1.scatter(index-start, float(row['close']), color="b", marker="^")

calculateHistory(doBuy,doSell)
ax1.plot(xdates,t3Price,label='t3price')
ax1.set_title('sz.002918')  # 标题
ax1.grid(True)  # 画网格
ax1.legend(loc='upper left')  # 图例放置于右上角
ax1.xaxis_date()  # 好像要不要效果一样？

# barVerts = [((date - delta, 0), (date - delta, vol), (date + delta, vol), (date + delta, 0)) for date, vol in zip(xdates, matix[:, 5])]
# # 生成K线实体(矩形)的4个顶点坐标
# ax2.add_collection(PolyCollection(barVerts, facecolors=inner_colors, edgecolors=updown_colors, antialiaseds=False,linewidths=0.5))
# # 生成多边形(矩形)顶点数据(背景填充色，边框色，反锯齿，线宽)
# if n >= 5:  # 5日均线，作法类似前面的均线
#     vol5 = result['volume'].rolling(5).mean().values
#     ax2.plot(xdates, vol5, c='y', label='VOL5')
# if n >= 10:  # 10日均线，作法类似前面的均线
#     vol10 = result['volume'].rolling(10).mean().values
#     ax2.plot(xdates, vol10, c='w', label='VOL10')
# ax2.yaxis.set_ticks_position('right')  # y轴显示在右边
# ax2.legend(loc='upper left')  # 图例放置于右上角
# ax2.grid(True)  # 画网格


# 绘制KDJ
ax2.axhline(20, ls='-', c='g', lw=0.5)  # 水平线
ax2.axhline(40, ls='-', c='g', lw=0.5)  # 水平线
ax2.axhline(60, ls='-', c='g', lw=0.5)  # 水平线
ax2.axhline(80, ls='-', c='g', lw=0.5)  # 水平线
ax2.yaxis.set_ticks_position('right')  # y轴显示在右边
ax2.plot(xdates, slowk, c='y', label='K')  # 绘制K线
ax2.plot(xdates, slowd, c='c', label='D')  # 绘制D线
ax2.plot(xdates, slowj, c='m', label='J')  # 绘制J线
ax2.legend(loc='upper left')  # 图例放置于右上角
ax2.grid(True)  # 画网格



ax3.plot(xdates, Adxprice, c='w', label='Adxprice')
ax3.plot(xdates, Adxrprice, c='b', label='Adxrprice')
ax3.legend(loc='upper left')  # 图例放置于右上角
ax3.grid(True)  # 画网格

# ax4.plot(xdates,emv,c='r',label='EMV')
# ax4.plot(xdates,maemv,c='g',label='MAEMV')
ax4.plot(xdates,subemv,c='g',label='subemv')
ax4.axhline(0, ls='-', c='w', lw=0.5)  # 水平线
ax4.legend(loc='upper left')  # 图例放置于右上角
ax4.grid(True)  # 画网格

ax5.axhline(10000, ls='-', c='w', lw=0.5)  # 水平线
ax5.plot(buysell, myRmb, c='g', label='割韭菜')
ax5.legend(loc='upper left')  # 图例放置于右上角
ax5.grid(True)  # 画网格

cursor = Cursor(ax1, useblit=True, color='w', linewidth=0.5, linestyle='--')
cursor1 = Cursor(ax3, useblit=True, color='w', linewidth=0.5, linestyle='--')
cursor2 = Cursor(ax4, useblit=True, color='w', linewidth=0.5, linestyle='--')

# 登出系统
bs.logout()

plt.show()