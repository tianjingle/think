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
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import os

import os
import sys
cur_path=os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, cur_path+"/..")

#线性回归
from scipy.optimize import leastsq
import time

from src.ChipCalculate import ChipCalculate

stackCode="sz.000918"
# isIndex=True
isIndex=False
window=200
totalRmb=5000
baseRmb=totalRmb
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
downlimit=-100
date_tickers=[]
priceJJJ=0
currentPrice=0
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


##需要拟合的函数func :指定函数的形状 k= 0.42116973935 b= -8.28830260655
def func(p, x):
    k, b = p
    return k * x + b


##偏差函数：x,y都是列表:这里的x,y更上面的Xi,Yi中是一一对应的
def error(p, x, y):
    return func(p, x) - y


def everyErChengPrice(sourceResult,step):
    # k,b的初始值，可以任意设定,经过几次试验，发现p0的值会影响cost的值：Para[1]
    Kflag=[]
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
        XI=sourceResult.values[myStart:myEnd][:,0]
        YI=sourceResult['tprice'][myStart:myEnd]
        # 把error函数中除了p0以外的参数打包到args中(使用要求)
        Para = leastsq(error, p0, args=(XI, YI))
        # 读取结果
        k, b = Para[0]
        temp.append(XI)
        temp.append(k * XI + b)
        erChengPrice.append(temp)
        #回归的变化率
        ktemp.append(myEnd)
        ktemp.append(k)
        Kflag.append(ktemp)
    return Kflag


def everyErChengPriceForArray(sourceX,sourceY,step):
    # k,b的初始值，可以任意设定,经过几次试验，发现p0的值会影响cost的值：Para[1]
    Kflag=[]
    p0=[1,20]
    global erChengPrice
    #最前的7天都不计算
    count=len(sourceX)
    if count-step<0:
        return
    for i in range(count):
        XI = []
        YI = []
        temp=[]
        ktemp=[]
        myStart=i
        myEnd=i+step
        if myEnd>count:
            break
        XI=sourceX[myStart:myEnd]
        YI=sourceY[myStart:myEnd]
        # 把error函数中除了p0以外的参数打包到args中(使用要求)
        Para = leastsq(error, p0, args=(XI, YI))
        # 读取结果
        k, b = Para[0]
        temp.append(XI)
        temp.append(k * XI + b)
        erChengPrice.append(temp)
        #回归的变化率
        ktemp.append(myEnd)
        ktemp.append(k)
        Kflag.append(ktemp)
    return Kflag

def doubleErJie(yijieList,step):
    erjieK=[]
    # k,b的初始值，可以任意设定,经过几次试验，发现p0的值会影响cost的值：Para[1]
    p0 = [1, 20]
    # 最前的7天都不计算
    count = len(yijieList)
    if count - step < 0:
        return
    for i in range(count):
        ktemp = []
        myEnd = i + step
        if myEnd > count:
            break
        tempX=[]
        tempY=[]
        for j in range(step):
            tempX.append(yijieList[i+j][0])
            tempY.append(yijieList[i+j][1])
        # 把error函数中除了p0以外的参数打包到args中(使用要求)
        Para = leastsq(error, p0, args=(np.array(tempX), np.array(tempY)))
        # 读取结果
        k, b = Para[0]
        # 回归的变化率
        ktemp.append(myEnd)
        ktemp.append(k*5)
        ktemp.append(0)
        erjieK.append(ktemp)
    return erjieK

def init():
    global buysell, myRmb
    global totalRmb, handTotal

    stackCode = "sh.000001"
    isIndex = True
    # isIndex=False
    window = 200
    totalRmb = 5000
    baseRmb = totalRmb
    handTotal = 0
    buysell = []
    myRmb = []
    # 线性回归横坐标
    XI = []
    # 线性回归纵坐标
    YI = []
    erChengPrice = []
    Kflag = []
    erjieK = []
    KlineBuySellFlag = []
    downlimit = -100
    date_tickers = []

def testNewTon(NewtonBuySall,indexCloseDict):
    global buysell, myRmb
    global totalRmb, handTotal
    for item in NewtonBuySall:
        if indexCloseDict.get(item[0]+1)!= None:
            price = float(indexCloseDict.get(item[0]+1))
        else:
            continue
        # 买入
        print("当前价格"+str(price))
        if item[1] == 1:
            currentRmb = price * 100 * 1.002
            if totalRmb - currentRmb > 0:
                totalRmb = totalRmb - currentRmb
                handTotal = handTotal + 1
                buysell.append(item[0])
                myRmb.append(totalRmb + handTotal * 100 * price)
                print("总金额：" + str(totalRmb) + "   总手数" + str(handTotal) + "   账户总金额：" + str(
                    totalRmb + handTotal * 100 * price))
            else:
                buysell.append(item[0])
                myRmb.append(totalRmb + handTotal * 100 * price)
                print("资金不足")
        elif item[1] == -1:
            if handTotal > 0:
                currentRmb = handTotal * 100 * price * 0.998
                totalRmb = totalRmb + currentRmb
                buysell.append(item[0])
                myRmb.append(totalRmb)
                handTotal = 0
                print("总金额：" + str(totalRmb) + "   总手数" + str(handTotal) + "   账户总金额：" + str(totalRmb))
            else:
                buysell.append(item[0])
                myRmb.append(totalRmb)
                print("不用再往出卖了")


def chipCalculate(result,start):
    chipCalculateList=[]
    #传入的数据id,open,high,low,close,volume,typePrice,turn
    #          0,   1,   2,  3,   4,    5,    6,       7
    for index, row in result.iterrows():
        temp=[]
        currentIndex=index-start
        temp.append(currentIndex)
        temp.append(row['open'])
        temp.append(row['high'])
        temp.append(row['low'])
        temp.append(row['close'])
        temp.append(row['volume'])
        temp.append(row['tprice'])
        temp.append(row['turn'])
        chipCalculateList.append(temp)
    calcualate=ChipCalculate()
    resultEnd=calcualate.getDataByShowLine(chipCalculateList)
    print(resultEnd)
    return resultEnd

def execute(code):
    init()
    global priceJJJ,currentPrice
    endDate=time.strftime('%Y-%m-%d',time.localtime(time.time()))
    lg = bs.login()
    rs = bs.query_history_k_data_plus(code,
        "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
        start_date='2018-01-01', end_date=endDate,
        frequency="d", adjustflag="3")

    #### 打印结果集 ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    start=len(result)-window
    #二维数组
    result=result.loc[:,['date','open','high','low','close','volume','turn'] ]
    if code=='sh.000001':
        result['temp']=1000
        result['open']=talib.DIV(result['open'],result['temp'])
        result['high']=talib.DIV(result['high'],result['temp'])
        result['low']=talib.DIV(result['low'],result['temp'])
        result['close']=talib.DIV(result['close'],result['temp'])

    result=result[-window:]
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


    current=result[-1:]
    #逐个计算最近7天的趋势
    currentPrice=float(current.iloc[0].iat[4])
    print(currentPrice)
    Kflag=everyErChengPrice(result,14)
    erjieSlow=everyErChengPrice(result,30)

    #将收盘价转化为字典
    testX=[]
    testY=[]
    for index, row in result.iterrows():
        currentIndex=index-start
        price=row['close']
        testX.append(currentIndex)
        testY.append(price)
    indexCloseDict=dict(zip(testX,testY))


    xdates = matix[:,0] # X轴数据(这里用的天数索引)


    t3Price = talib.T3(result['close'], timeperiod=30, vfactor=0)
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
    ax1 = fig.add_axes([left, 0.5, width, 0.48])  # left, bottom, width, height
    ax2 = fig.add_axes([left, 0.4, width, 0.1], sharex=ax1)  # 共享ax1轴
    ax3 = fig.add_axes([left, 0.3, width, 0.09], sharex=ax1)  # 共享ax1轴
    ax4 = fig.add_axes([left, 0.2, width, 0.09], sharex=ax1)  # 共享ax1轴
    ax5 = fig.add_axes([left, 0.1, width, 0.09], sharex=ax1)  # 共享ax1轴
    plt.setp(ax1.get_xticklabels(), visible=True)  # 使x轴刻度文本不可见，因为共享，不需要显示
    plt.setp(ax2.get_xticklabels(), visible=True)  # 使x轴刻度文本不可见，因为共享，不需要显示
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
    ax1.add_collection(LineCollection(rangeSegments, colors=updown_colors, linewidths=0.5,antialiaseds=True))
    # 生成上下影线的顶点数据(颜色，线宽，反锯齿，反锯齿关闭好像没效果)
    ax1.add_collection(PolyCollection(barVerts, facecolors=inner_colors, edgecolors=updown_colors, antialiaseds=True,linewidths=0.5))
    # 生成多边形(矩形)顶点数据(背景填充色，边框色，反锯齿，线宽)

    # 绘制均线
    mav_colors = ['#ffffff', '#d4ff07', '#ff80ff', '#00e600', '#02e2f4', '#ffffb9', '#2a6848']  # 均线循环颜色
    mav_period = [5, 10, 20, 30, 60, 120, 180]  # 定义要绘制的均线周期，可增减
    n = len(result)
    priceTwo=[]
    for i in range(len(mav_period)):
        if n >= mav_period[i]:
            mav_vals = result['close'].rolling(mav_period[i]).mean().values
            if i==0:
                priceTwo=mav_vals
            ax1.plot(xdates, mav_vals, c=mav_colors[i % len(mav_colors)], label='MA' + str(mav_period[i]))
    #everyErChengPrice(result, 7)
    #线性回归展示
    # for item in erChengPrice:
    #     myX=item[0]
    #     myY=item[1]
    #     ax1.plot(myX, myY, color="yellow", linewidth=0.3)


    ax1.plot(xdates,t3Price,label='t3price')
    ax1.set_title('sz.002918')  # 标题
    ax1.grid(True)  # 画网格
    ax1.legend(loc='upper left')  # 图例放置于右上角
    ax1.xaxis_date()  # 好像要不要效果一样？


    #计算二阶导数
    erjieK=doubleErJie(Kflag,3)
    x1=[]
    y1=[]
    for index, row in result.iterrows():
        currentIndex=index-start
        x1.append(currentIndex)
        y1.append(row['tprice'])
    #筹码计算
    resultEnd=chipCalculate(result,start)

    Kflag = everyErChengPrice(result, 14)
    x=[]
    p=[]
    resultEnd.sort(key=lambda resultEnd: resultEnd[0])
    resultEndLength=len(resultEnd)
    string=""
    mystart=0
    for i in range(len(resultEnd)):
        if i==0:
            mystart=resultEnd[i][0]
        x.append(resultEnd[i][0])
        string=string+","+str(resultEnd[i][1])
        p.append(resultEnd[i][1])
        if i==resultEndLength-1:
            priceJJJ=resultEnd[i][1]
    myResult = pd.DataFrame()
    myResult['tprice']=p
    tianjingle=everyErChengPriceForArray(np.array(x),np.array(p),30)
    x1=[]
    y1=[]
    for item in tianjingle:
        kX = item[0]
        kk = item[1]
        x1.append(kX+mystart)
        y1.append(kk)
    pingjunchengbendic = dict(zip(x1, y1))
    ax3.plot(x1, y1, color="r", linewidth=0.6, label='一阶导数')

    print("平均成本移动")
    print(tianjingle)
    ax4.plot(x, p, c='b', label='移动成本')
    ax1.plot(x, p, c='b', label='移动成本')
    ax4.plot(xdates, priceTwo, c='r', label='jaige')
    ax4.grid(True)  # 画网格
    kdict={}
    #线性回归展示
    wangX=[]
    wangY=[]
    for item in Kflag:
        kX=item[0]
        kk=item[1]
        wangX.append(kX)
        wangY.append(kk)
    # ax2.plot(wangX, wangY, color="w", linewidth=0.6,label='一阶导数')
    yijiedict=dict(zip(wangX,wangY))


    wangX=[]
    wangY=[]
    for item in erjieK:
        kX=item[0]+14
        kk=item[1]
        wangX.append(kX)
        wangY.append(kk)
    ax2.plot(wangX, wangY, color="y", linewidth=0.6,label='二阶导数')


    wangXSlow=[]
    wangYSlow=[]
    for item in erjieSlow:
        kX1=item[0]
        kk1=item[1]
        wangXSlow.append(kX1)
        wangYSlow.append(kk1)
    ax3.axhline(0,ls='-', c='g', lw=0.5)
    ax3.plot(wangXSlow, wangYSlow, color="#33FFff", linewidth=0.6,label='慢速导数')
    yijieSlowdict=dict(zip(wangXSlow,wangYSlow))
    print(yijieSlowdict)
    NewtonBuySall=[]

    oldTwok=0
    oldOne=0
    #牛顿策略

    downlimitTemp=0
    #找到最小的那一个
    for item in erjieK:
        if item[1]!=None and item[1]<downlimitTemp:
            downlimitTemp=item[1]
    downlimitTemp=abs(downlimitTemp)

    print("最小值"+str(downlimitTemp))
    for item in erjieK:
        item[2]=item[1]/downlimitTemp*100
        print("最小值："+str(downlimitTemp)+"  当前二阶："+str(item[1])+"  百分比："+str(item[2]))

    print(yijieSlowdict)
    print("---------------")
    print(pingjunchengbendic)
    for i in range(len(erjieK)):
        item=erjieK[i]
        currentx=item[0]+14
        twok=item[1]
        downParent=item[2]
        onek=yijiedict.get(currentx)
        onkslow=yijieSlowdict.get(currentx)
        onkchengben=pingjunchengbendic.get(currentx)




        print(str(onkslow)+"--"+str(onkchengben))
        if onek==None or onkslow ==None or onkchengben==None:
            continue
        if onkslow<0 and onkchengben<0:
            print("ytes")
            onslowyestaday=yijieSlowdict.get(currentx-1)
            chengbenyestaday=pingjunchengbendic.get(currentx-1)
            if onslowyestaday == None or chengbenyestaday == None:
                continue
            if onslowyestaday<0 and chengbenyestaday<0 and onslowyestaday<onkslow and onkchengben<chengbenyestaday:
                newTonTemp = []
                newTonTemp.append(currentx)
                newTonTemp.append(1)
                NewtonBuySall.append(newTonTemp)
                ax1.axvline(currentx,ls='-', c='g', lw=0.5)
                ax2.scatter(currentx, twok, color="g", linewidth=0.0004)
        if onkslow<0:
            newTonTemp = []
            newTonTemp.append(currentx)
            newTonTemp.append(-1)
            NewtonBuySall.append(newTonTemp)
            # ax1.axvline(currentx,ls='-', c='orange', lw=0.5)
            # ax2.scatter(currentx, twok, color="orange", linewidth=0.0004)
            continue
        #一阶导数大于0，二阶导数大于0，一阶导数大于二阶导数，二阶导数递减
        if oldTwok>0 and oldOne>0 and oldTwok>=oldOne and onek>0 and onek>twok:
            #添加历史回测里
            newTonTemp = []
            newTonTemp.append(currentx)
            newTonTemp.append(-1)
            NewtonBuySall.append(newTonTemp)
            ax1.axvline(currentx,ls='-', c='r', lw=0.5)
            ax2.scatter(currentx, twok, color="r", linewidth=0.0004)
        if oldOne>0 and onek>0 and oldOne>onek and oldTwok>oldOne and onek>twok:
            #添加历史回测里
            newTonTemp = []
            newTonTemp.append(currentx)
            newTonTemp.append(-1)
            NewtonBuySall.append(newTonTemp)
            ax1.axvline(currentx,ls='-', c='r', lw=0.5)
            ax2.scatter(currentx, twok, color="r", linewidth=0.0004)
        # if  onek>0 and oldOne<0:
        #     #添加历史回测里
        #     newTonTemp = []
        #     newTonTemp.append(currentx)
        #     newTonTemp.append(-1)
        #     NewtonBuySall.append(newTonTemp)
        #     ax1.axvline(currentx,ls='-', c='orange', lw=0.5)
        #     ax2.scatter(currentx, twok, color="orange", linewidth=0.0004)
        #一阶导数小于0，二阶导数小于0,一阶导数小于二阶导数，二阶导数递增,并且在之前的三天都被一阶导数压制
        if onek<=0 and twok>onek and oldTwok<oldOne and downParent<downlimit and abs(twok-oldTwok)>abs(onek-oldOne):
            #添加到历史回测里
            newTonTemp = []
            newTonTemp.append(currentx)
            newTonTemp.append(1)
            NewtonBuySall.append(newTonTemp)
            # ax2.scatter(currentx, twok, color="g", linewidth=0.0004)
            # ax1.axvline(currentx,ls='-', c='g', lw=0.5)
        elif onek <= 0 and twok > onek and oldTwok < oldOne and downParent > downlimit and twok>0:
            newTonTemp = []
            newTonTemp.append(currentx)
            newTonTemp.append(1)
            NewtonBuySall.append(newTonTemp)
            ax2.scatter(currentx, twok, color="#5EA26B", linewidth=0.0004)
            ax1.axvline(currentx,ls='-', c='#5EA26B', lw=0.5)
        elif onek <= 0 and twok > onek and oldTwok < oldOne and downParent > downlimit and twok<0:
            newTonTemp = []
            newTonTemp.append(currentx)
            newTonTemp.append(1)
            NewtonBuySall.append(newTonTemp)
            ax2.scatter(currentx, twok, color="g", linewidth=0.0004)
            ax1.axvline(currentx,ls='-', c='g', lw=0.5)
        oldTwok=twok
        oldOne=onek

    ax2.axhline(0, ls='-', c='g', lw=0.5)  # 水平线
    ax1.axhline(3.291, ls='-', c='g', lw=0.5)  # 水平线
    ax2.axhline(abs(downlimitTemp)*(downlimit/100), ls='-', c='b', lw=0.5)  # 水平线
    ax2.grid(True)  # 画网格
    ax1.axhline(priceJJJ,ls='-',c='#c7001b',lw=0.5)
    # ax1.axvline(currentPrice,ls='-',c='#c7001b',lw=0.5)
    ax2.axhline(0, ls='-', c='g', lw=0.5)  # 水平线
    oldKK=0
    oldTwokk=0
    old2=0
    #线性回归展示
    newYY=[]
    newXX=[]
    for item in erjieK:
        kX=item[0]+14
        kk=item[1]
        item[2]=0
        print(old2)
        olddictvalue=yijiedict.get(kX)
        if olddictvalue==None:
            continue
        newXX.append(kX)
        newYY.append(float(kk)+float(olddictvalue))
        # ax2.scatter(kX, float(kk)+float(olddictvalue), color="r", linewidth=0.0004)
        #二阶上穿
        if kk>=0 and oldKK<0:

            if old2==-1:
                # ax2.scatter(kX, kk, color="b", linewidth=0.0004)
                # ax1.axvline(kX, ls='-', c='b', lw=0.5)
                item[2] = 1
                # print("买入"+str(kX))
                # #买入
                # newTonTemp = []
                # newTonTemp.append(kX)
                # newTonTemp.append(1)
                # NewtonBuySall.append(newTonTemp)
        #二阶下穿越
        if kk<=0 and oldKK>0:
            ax1.axvline(kX, ls='-', c='y', lw=0.5)
            ax2.scatter(kX, kk, color="y", linewidth=0.0004)
            item[2] = -1

        old2=item[2]
        oldKK=kk
        oldTwokk=olddictvalue
    ax2.plot(newXX, newYY, color="#B22222", linewidth=0.6,label='total qushi')


    testNewTon(NewtonBuySall,indexCloseDict)
    ax5.axhline(baseRmb, ls='-', c='w', lw=0.5)  # 水平线
    ax5.plot(buysell, myRmb, c='g', label='测试')
    ax5.legend(loc='upper left')  # 图例放置于右上角
    ax5.grid(True)  # 画网格

    cursor = Cursor(ax1, useblit=True, color='w', linewidth=0.5, linestyle='--')

    # 登出系统
    bs.logout()
    # plt.show()
    plt.savefig("E:\\"+code+".png")


def start():
    global buysell, myRmb
    global totalRmb, handTotal,priceJJJ
    codes=[['sh.000001',0,0,'上证指数'],['sz.002659',4.070,100,'凯文教育'],['sh.600336',6.855,200,'澳柯玛'],['sh.600340',6.340,100,'华夏幸福'],['sh.600543',6.975,200,'莫高股份']]
    imgsOKstr=""
    imgsOK=[]
    imgsOFF=[]
    oldTotal=0
    currentTotal=0
    for items in codes:
        item=items[0]
        execute(item)
        color="red"
        shouyi=0
        if items[1]!=0:
            shouyi=float(currentPrice)-float(items[1])
            oldTotal=oldTotal+(items[1]*items[2])
            currentTotal=currentTotal+(float(currentPrice)*items[2])
        if shouyi>0:
            shouyidisc="<font color='red'>" + str(round(shouyi*items[2],2)) + "</font>"
        else:
            shouyidisc = "<font color='green'>" + str(round(shouyi*items[2],2)) + "</font>"
        if currentPrice>items[1]:
            color="green"
        imgsOKstr = imgsOKstr + str(items[3])+"<font color='"+color+"'>"+str(currentPrice)+"-"+str(items[1])+"="+str(round(currentPrice-items[1],2))+"  "+shouyidisc+"<img src='cid:" + item + "'></front>"
        imgsOK.append(item)
    endDate=time.strftime('%Y-%m-%d',time.localtime(time.time()))
    my_pass = 'tmugmrbimrcddead'  # 发件人邮箱密码
    my_user = '2695062879@qq.com'  # 收件人邮箱账号，我这边发送给自己
    sender = '2695062879@qq.com'
    receivers = ['2695062879@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    msgRoot = MIMEMultipart('related')
    dic=currentTotal - oldTotal
    mycolor="red"
    if dic<=0:
        mycolor="green"
    zijingbiandong=str(currentTotal) + "-" + str(oldTotal) + "=" + str(dic)
    msgRoot['From'] = Header(str(endDate)+"  "+str(currentTotal - oldTotal), 'utf-8')
    msgRoot['To'] = Header("测试", 'utf-8')
    subject = str(endDate)+' 收益：'+str(dic)
    msgRoot['Subject'] = Header(subject, 'utf-8')

    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    mail_msg = "<p><font color='"+mycolor+"'>"+zijingbiandong+"</font></p><p>"+imgsOKstr+"</p>"
    msgAlternative.attach(MIMEText(mail_msg, 'html', 'utf-8'))

    # 指定图片为当前目录
    for item in imgsOK:
        fp = open('E:\\'+item+".png", 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        temp="<"+item+">"
        # 定义图片 ID，在 HTML 文本中引用
        msgImage.add_header('Content-ID', temp)
        msgRoot.attach(msgImage)

    # 指定图片为当前目录
    for item in imgsOFF:
        fp = open('E:\\'+item+".png", 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        temp="<"+item+">"
        # 定义图片 ID，在 HTML 文本中引用
        msgImage.add_header('Content-ID', temp)
        msgRoot.attach(msgImage)
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect('smtp.qq.com', 25)    # 25 为 SMTP 端口号
        smtpObj.login(my_user,my_pass)
        smtpObj.sendmail(sender, receivers, msgRoot.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")
    # os.system('shutdown -s -f -t 180')

start()
