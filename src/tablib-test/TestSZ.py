import talib
import matplotlib.pyplot as plt
from matplotlib.pylab import date2num
import matplotlib.ticker as ticker  # 用于日期刻度定制
import baostock as bs
import pandas as pd
import numpy as np
import datetime
from matplotlib import colors as mcolors  # 用于颜色转换成渲染时顶点需要的颜色格式
from matplotlib.collections import LineCollection, PolyCollection  # 用于绘制直线集合和多边形集合
from matplotlib.widgets import Cursor  # 处理鼠标
#线性回归
from scipy.optimize import leastsq
import math

#牛顿策略
NewtonBuySall=[]
newTonTemp=[]


totalRmb=10000
handTotal=0
buysell=[]
myRmb=[]
#线性回归横坐标
XI=[]
#线性回归纵坐标
YI=[]
erChengPrice=[]
Kflag=[]
erjieK=[]
KlineBuySellFlag=[]


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
def BuySallForEmv(Emv,MaEmv,M30,T30,Tprice,kPrice,dPrice,jPrice):
    BuyIndex=[]
    SallIndex=[]
    temp=pd.DataFrame({ 'emv' :Emv, 'maemv' :MaEmv,'m30':M30,'t30':T30,'tprice':Tprice,'kP':kPrice,'dP':dPrice,'jP':jPrice})
    print(temp)
    for index, row in temp.iterrows():
        if row['emv'] is None or row['t30'] is None or row['m30'] is None or row['kP'] is None or row['dP'] is None or row['jP'] is None:
            continue
            #如果30日均线大于30日T3线就买入
        # if row['emv'] > 0 and row['maemv']>0 and row['emv']>row['maemv'] and row['tprice']>row['m30'] and row['m30']>row['t30']:
        if row['kP']<=30 and row['dP']<=30 and row['jP']<=30 and row['jP']>row['dP'] and row['kP']:
            BuyIndex.append(index)
        # elif row['emv']>=0 and row['maemv']>=0 and row['emv']<row['maemv']:
        elif row['kP']>=80 and row['dP']>=80 and row['jP']>=80:
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

##需要拟合的函数func :指定函数的形状 k= 0.42116973935 b= -8.28830260655
def func(p, x):
    k, b = p
    return k * x + b


##偏差函数：x,y都是列表:这里的x,y更上面的Xi,Yi中是一一对应的
def error(p, x, y):
    return func(p, x) - y


def everyErChengPrice(sourceResult,step):
    # k,b的初始值，可以任意设定,经过几次试验，发现p0的值会影响cost的值：Para[1]
    p0=[1,20]
    global erChengPrice
    #最前的7天都不计算
    count=len(sourceResult)
    if count-step<0:
        return
    for i in range(count):
        temp=[]
        ktemp=[]
        myStart=i
        myEnd=i+step
        if myEnd>count:
            break
        print(myStart)
        print(myEnd)
        XI=sourceResult.values[myStart:myEnd][:,0]
        YI=sourceResult['tprice'][myStart:myEnd]
        print(XI)
        print(YI)
        # 把error函数中除了p0以外的参数打包到args中(使用要求)
        Para = leastsq(error, p0, args=(XI, YI))
        print(Para)
        # 读取结果
        k, b = Para[0]
        print("i=",i,"k=", k, "b=", b)
        temp.append(XI)
        temp.append(k * XI + b)
        erChengPrice.append(temp)
        #回归的变化率
        ktemp.append(myEnd)
        ktemp.append(k*1000)
        Kflag.append(ktemp)


def doubleErJie(yijieList,step):
    # k,b的初始值，可以任意设定,经过几次试验，发现p0的值会影响cost的值：Para[1]
    p0 = [1, 20]
    # 最前的7天都不计算
    count = len(yijieList)
    if count - step < 0:
        return
    for i in range(count):
        ktemp = []
        myStart = i
        myEnd = i + step
        if myEnd > count:
            break
        tempX=[]
        tempY=[]
        for j in range(step):
            tempX.append(yijieList[i+j][0])
            tempY.append(yijieList[i+j][1])

        print(tempX)
        print(tempY)
        # 把error函数中除了p0以外的参数打包到args中(使用要求)
        Para = leastsq(error, p0, args=(np.array(tempX), np.array(tempY)))
        print(Para)
        # 读取结果
        k, b = Para[0]
        # 回归的变化率
        ktemp.append(myEnd)
        ktemp.append(k*5)
        erjieK.append(ktemp)

lg = bs.login()
rs = bs.query_history_k_data_plus("sh.000001",
    "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
    start_date='1999-07-01', end_date='2020-10-24',
    frequency="d", adjustflag="3")

#### 打印结果集 ####
data_list = []
while (rs.error_code == '0') & rs.next():
    data_list.append(rs.get_row_data())
result = pd.DataFrame(data_list, columns=rs.fields)
window=300
start=len(result)-window
#二维数组
result=result.loc[:,['date','open','high','low','close','volume'] ]
result=result[-window:]

# result['temp']=1000
# result['open']=talib.DIV(result['open'],result['temp'])
# result['high']=talib.DIV(result['high'],result['temp'])
# result['low']=talib.DIV(result['low'],result['temp'])
# result['close']=talib.DIV(result['close'],result['temp'])


#计算三十日均线
result['M30']=talib.SMA(result['close'],30)
result['T30']=talib.T3(result['close'],timeperiod=30, vfactor=0)
result['tprice']=talib.TYPPRICE(result['high'],result['low'],result['close'])
slowk, slowd = talib.STOCH(result['high'],result['low'],result['close'], fastk_period=9, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
slowj= list(map(lambda x,y: 3*x-2*y, slowk, slowd))
result['k']=slowk
result['d']=slowd
result['j']=slowj
# 计算KDJ值，数据存于DataFrame中
date_tickers=result.date.values
result.date = range(0, len(result))  # 日期改变成序号
matix = result.values  # 转换成绘制蜡烛图需要的数据格式(date, open, close, high, low, volume)



#逐个计算最近7天的趋势
everyErChengPrice(result,14)




xdates = matix[:,0] # X轴数据(这里用的天数索引)


#将收盘价转化为字典
testX=[]
testY=[]
for index, row in result.iterrows():
    currentIndex=index-start
    price=row['close']
    testX.append(currentIndex)
    testY.append(price)
indexCloseDict=dict(zip(testX,testX))


#总投资金额为5000元，买入信号出现时每次买一手。如果有卖出信号则全部卖出

t3Price = talib.T3(result['close'], timeperiod=30, vfactor=0)
Adxprice = talib.ADX(result['high'],result['low'],result['close'], timeperiod=5)
Adxrprice = talib.ADXR(result['high'],result['low'],result['close'], timeperiod=5)

emv,maemv,subemv=TEMV(result,5,10)


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

#通过kdj来买卖的策略，太low
# calculateHistory(doBuy,doSell)

#线性回归展示
for item in erChengPrice:
    myX=item[0]
    myY=item[1]
    ax1.plot(myX, myY, color="yellow", linewidth=0.3)


ax1.plot(xdates,t3Price,label='t3price')
ax1.set_title('sz.002918')  # 标题
ax1.grid(True)  # 画网格
ax1.legend(loc='upper left')  # 图例放置于右上角
ax1.xaxis_date()  # 好像要不要效果一样？

ax3.plot(xdates, Adxprice, c='w', label='Adxprice')
ax3.plot(xdates, Adxrprice, c='b', label='Adxrprice')
ax3.legend(loc='upper left')  # 图例放置于右上角
ax3.grid(True)  # 画网格
ax4.axhline(0, ls='-', c='w', lw=0.5)  # 水平线

#计算二阶导数
doubleErJie(Kflag,2)
kdict={}
#线性回归展示
wangX=[]
wangY=[]
for item in Kflag:
    kX=item[0]
    kk=item[1]

    wangX.append(kX)
    wangY.append(kk)
ax2.plot(wangX, wangY, color="w", linewidth=0.6,label='一阶导数')
yijiedict=dict(zip(wangX,wangY))

print(erjieK)

wangX=[]
wangY=[]
for item in erjieK:
    kX=item[0]+14
    kk=item[1]
    wangX.append(kX)
    wangY.append(kk)
ax2.plot(wangX, wangY, color="y", linewidth=0.6,label='二阶导数')



oldTwok=0
for i in range(len(erjieK)):
    item=erjieK[i]
    currentx=item[0]+14
    twok=item[1]
    onek=yijiedict.get(currentx)
    if onek==None:
        continue
    print(str(i)+"一阶"+str(onek)+"二阶"+str(twok))
    #一阶导数大于0，二阶导数大于0，一阶导数大于二阶导数，二阶导数递减
    if onek>0 and twok<onek and oldTwok>onek:
        #添加历史回测里
        ax1.axvline(currentx,ls='-', c='r', lw=0.5)
        ax2.scatter(currentx, twok, color="r", linewidth=0.0004)
    #一阶导数小于0，二阶导数小于0,一阶导数小于二阶导数，二阶导数递增,并且在之前的三天都被一阶导数压制
    if onek<=0 and twok<=0 and twok>onek and oldTwok<onek:
        #二次筛选
        if i>3:
            yesToday1TwoK=erjieK[i-1]
            yesToday2TwoK=erjieK[i-2]
            yesToday1oneK=yijiedict.get(currentx-1)
            yesToday2oneK=yijiedict.get(currentx-2)
            if yesToday1TwoK[1]<yesToday1oneK and yesToday2TwoK[1]<yesToday2oneK:
                #添加到历史回测里
                ax2.scatter(currentx, twok, color="g", linewidth=0.0004)
                ax1.axvline(currentx)
    oldTwok=twok
ax2.axhline(0, ls='-', c='g', lw=0.5)  # 水平线







# 绘制KDJ
# K, D, J = matix[:, 9], matix[:, 10], matix[:, 11]  # 取出KDJ值
ax4.axhline(20, ls='-', c='g', lw=0.5)  # 水平线
ax4.axhline(40, ls='-', c='g', lw=0.5)  # 水平线
ax4.axhline(60, ls='-', c='g', lw=0.5)  # 水平线
ax4.axhline(80, ls='-', c='g', lw=0.5)  # 水平线
ax4.yaxis.set_ticks_position('right')  # y轴显示在右边
ax4.plot(xdates, slowk, c='y', label='K')  # 绘制K线
ax4.plot(xdates, slowd, c='c', label='D')  # 绘制D线
ax4.plot(xdates, slowj, c='m', label='J')  # 绘制J线
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