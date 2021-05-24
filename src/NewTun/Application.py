import pandas as pd

from src.NewTun.ChipCalculate import ChipCalculate
from src.NewTun.DrawPicture import DrawPicture
from src.NewTun.LeastSquare import LeastSquare
from src.NewTun.LoopBack import LoopBack
from src.NewTun.QueryStock import QueryStock
import numpy as np

class Application:


    window=160
    downlimit=-20
    indexCloseDict={}
    least = LeastSquare()
    draw=DrawPicture()
    loopBack=LoopBack()
    queryStock=QueryStock()
    avgCostGrad=0


    def setStackCode(self):
        least=LeastSquare()
        draw = DrawPicture()
        loopBack = LoopBack()
        queryStock = QueryStock()
        queryStock.init(self.window)
        self.indexCloseDict={}


    #筹码计算
    def chipCalculate(self,result, start):
        chipCalculateList = []
        for index, row in result.iterrows():
            temp = []
            currentIndex = index - start
            temp.append(currentIndex)
            temp.append(row['open'])
            temp.append(row['high'])
            temp.append(row['low'])
            temp.append(row['close'])
            temp.append(row['volume'])
            temp.append(row['tprice'])
            temp.append(row['turn'])
            temp.append(int(row['tradestatus']))
            chipCalculateList.append(temp)
        calcualate = ChipCalculate()
        resultEnd = calcualate.getDataByShowLine(chipCalculateList)
        return resultEnd



    #执行器
    def execute(self,code,isShow):
        result=self.queryStock.queryStock(code)
        if len(result)<200:
            return self
        return self.core(result,code,isShow)

    #核心调度器
    def core(self,result,code,isShow):
        self.draw.showK(code,result,isShow)
        #十四天
        Kflag=self.least.everyErChengPrice(result,14)
        #三十天
        erjieSlow = self.least.everyErChengPrice(result, 30)
        # 三天二阶导数
        erjieK=self.least.doubleErJie(Kflag, 3)
        #将收盘价转化为字典
        testX=[]
        testY=[]
        for index, row in result.iterrows():
            currentIndex=index-self.queryStock.start
            price=row['close']
            testX.append(currentIndex)
            testY.append(price)
        self.indexCloseDict=dict(zip(testX,testY))

        #一阶导数
        wangX = []
        wangY = []
        for item in Kflag:
            kX = item[0]
            kk = item[1]
            wangX.append(kX)
            wangY.append(kk)
        self.draw.ax1Show(wangX,wangY)
        yijiedict = dict(zip(wangX, wangY))

        #二阶导数
        wangX = []
        wangY = []
        for item in erjieK:
            kX = item[0] + 14
            kk = item[1]
            wangX.append(kX)
            wangY.append(kk)
        self.draw.ax2Show(wangX,wangY)

        #慢速一阶导数
        wangXSlow = []
        wangYSlow = []
        for item in erjieSlow:
            kX1 = item[0]
            kk1 = item[1]
            wangXSlow.append(kX1)
            wangYSlow.append(kk1)
        self.draw.ax3showSlow(wangXSlow, wangYSlow)
        yijieSlowdict = dict(zip(wangXSlow, wangYSlow))


        # 筹码计算
        resultEnd = self.chipCalculate(result, self.queryStock.start)
        x = []
        p = []
        resultEnd.sort(key=lambda resultEnd: resultEnd[0])
        resultEndLength = len(resultEnd)
        string = ""
        mystart = 0
        for i in range(len(resultEnd)):
            if i == 0:
                mystart = resultEnd[i][0]
            x.append(resultEnd[i][0])
            string = string + "," + str(resultEnd[i][1])
            p.append(resultEnd[i][1])
            if i == resultEndLength - 1:
                priceJJJ = resultEnd[i][1]
        myResult = pd.DataFrame()
        myResult['tprice'] = p
        tianjingle = self.least.everyErChengPriceForArray(np.array(x), np.array(p), 30)
        x1 = []
        y1 = []
        if tianjingle==None:
            return
        for item in tianjingle:
            kX = item[0]
            kk = item[1]
            x1.append(kX + mystart)
            y1.append(kk)
        pingjunchengbendic = dict(zip(x1, y1))
        self.draw.ax3Show(x1,y1,'r','一阶导数')


        oldTwok=0
        oldOne=0
        #牛顿策略
        NewtonBuySall=[]
        downlimitTemp=0

        #回测的缓存数据
        buyList=[]
        sellList=[]
        total=len(result)
        for i in range(len(erjieK)):
            item = erjieK[i]
            currentx = item[0] + 14
            twok = item[1]
            downParent = item[2]
            onek = yijiedict.get(currentx)
            onkslow = yijieSlowdict.get(currentx)
            onkchengben = pingjunchengbendic.get(currentx)
            buyTemp=[]
            sellTemp=[]
            if onek == None or onkslow == None or onkchengben == None:
                continue
            if onkslow < 0 and onkchengben < 0:
                onslowyestaday = yijieSlowdict.get(currentx - 1)
                chengbenyestaday = pingjunchengbendic.get(currentx - 1)
                if onslowyestaday == None or chengbenyestaday == None:
                    continue
                if onslowyestaday < 0 and chengbenyestaday < 0 and onslowyestaday < onkslow and onkchengben < chengbenyestaday:
                    buyTemp.append(currentx)
                    buyTemp.append(twok)
                    buyTemp.append("g")
                    buyList.append(buyTemp)
                    if currentx==total-1:
                        self.avgCostGrad=onkchengben

            # 一阶导数大于0，二阶导数大于0，一阶导数大于二阶导数，二阶导数递减
            if oldTwok > 0 and oldOne > 0 and oldTwok >= oldOne and onek > 0 and onek > twok:
                sellTemp.append(currentx)
                sellTemp.append(twok)
                sellTemp.append("r")
                sellList.append(sellTemp)
            if oldOne > 0 and onek > 0 and oldOne > onek and oldTwok > oldOne and onek > twok:
                # 添加历史回测里
                sellTemp.append(currentx)
                sellTemp.append(twok)
                sellTemp.append("r")
                sellList.append(sellTemp)
            if onek > 0 and oldOne < 0:
                # 添加历史回测里
                sellTemp.append(currentx)
                sellTemp.append(twok)
                sellTemp.append("orange")
                sellList.append(sellTemp)
            # 一阶导数小于0，二阶导数小于0,一阶导数小于二阶导数，二阶导数递增,并且在之前的三天都被一阶导数压制
            if onek <= 0 and twok > onek and oldTwok < oldOne and downParent < self.downlimit and abs(twok - oldTwok) > abs(
                    onek - oldOne):
                # 添加到历史回测里
                buyTemp.append(currentx)
                buyTemp.append(twok)
                buyTemp.append("g")
                buyList.append(buyTemp)
            oldTwok = twok
            oldOne = onek

        #画线条
        self.draw.klineInfo(buyList,sellList)

        #找到最小的那一个
        for item in erjieK:
            if item[1]!=None and item[1]<downlimitTemp:
                downlimitTemp=item[1]
        downlimitTemp=abs(downlimitTemp)
        self.draw.drawDownLine(abs(downlimitTemp) * (self.downlimit / 100))
        for item in erjieK:
            item[2]=item[1]/downlimitTemp*100
        self.loopBack.testNewTon(NewtonBuySall,self.indexCloseDict)
        self.draw.ax5Show(self.loopBack.baseRmb,self.loopBack.buysell,self.loopBack.myRmb)
        return self





