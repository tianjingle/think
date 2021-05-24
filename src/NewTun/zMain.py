import time
import os,sys



from src.NewTun.Application import  Application
from src.NewTun.SendEmail import SendEmail
from src.NewTun.StockInfoSyn import StockInfoSyn

class zMain:

    #是否显示出来
    isShow=False

    candidate=[]

    #通过股票数据
    def synHistoryStock(self):
        print("-----------------------------syn stock------------------------------------")
        print("start time:"+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        syn=StockInfoSyn()
        syn.synStockInfo()
        print("start time:"+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))


    #扫描潜在可以投资的股票
    def scanStock(self):
        print("-----------------------------scan stock------------------------------------")
        print("start time:" + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        syn=StockInfoSyn()
        basicStock=syn.getBiscicStock()
        count=0
        for item in basicStock:
            # if item =='sz.000029':
            #     continue
            count=count+1
            test = Application()
            print(item)
            test.execute("sz.002014",self.isShow)
            if test.avgCostGrad<0:
                candidateTemp=[]
                candidateTemp.append(item)
                candidateTemp.append(test.avgCostGrad)
                self.candidate.append(candidateTemp)
            # if count==1:
            #     print("测试退出")
            #     break

    #按照程度的梯度排序
    def sortByStockGrad(self):
        self.candidate=sorted(self.candidate, key=lambda s: s[1])


    #展示筛选的股票
    def stockShow(self):
        for item in self.candidate:
            test = Application()
            test.execute(item[0],True)
            print(str(item[1])+"   "+item[0])

sys.path.append("path")
test=zMain()
# test.synHistoryStock()
test.scanStock()
test.sortByStockGrad()
test.stockShow()
sendEmail=SendEmail()
sendEmail.sendStockInfo(test.candidate)

