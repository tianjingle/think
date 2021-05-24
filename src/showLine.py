import baostock as bs
import pandas as pd
import numpy as np
import csv
import matplotlib.pyplot as plt
#start 开始 1386,1926,1937,1506,863,507
from src.ChouMa import ChouMa

# 121
# sh
# .600015
# 华夏银行
# 165
# sh
# .600115
# 东方航空
# 188
# shf
# .600169
# 太原重工
# 212
# sh
# .600221
# 海航控股
# 227
# sh
# .600255 * ST梦舟
# 253
# sh
# .600311 * ST荣华
# 263
# sh
# .600333
# 长春燃气
# 293
# sh
# .600405
# 动力源
myflag=0
date=240
isShow=0
stockCode="989"

class showLine:
    cleanFlag=0
    index=""

    ###
    ###将数据保存到数据库中
    def baoStackReq(self,code,start):
        lg=bs.login()
        print(lg)
        data=bs.query_history_k_data(code,"date,code,open,high,low,close,preclose,"
                                                 "volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,"
                                          "pbMRQ,psTTM,pcfNcfTTM,isST",start_date=start)
        targetData=[]
        while (data.error_code=="0")&data.next():
            targetData.append(data.get_row_data())
        result=pd.DataFrame(targetData,columns=data.fields)
        return result



    ###从文件中读取所有股票信息
    def baoStackReqFile(self,code,start):
        myCode=code.replace(".","")
        myFile=open("../data/"+myCode+".csv","r",encoding="UTF-8")
        myReader=csv.reader(myFile)
        dataTemp=[]
        for zz in myReader:
            dataTemp.append(zz)
        return dataTemp


    #转化成最近的多少天的数据
    def parse2Current(self,targetData,data):
        tempData=[]
        start=len(targetData)-data
        for zz in range(len(targetData)):
            if zz> start:
                tempData.append(targetData[zz])
            else:
                continue
        return tempData


    #判断最近50天是否出现价格的跳空
    def tiaokong(self,k,tiaokongData):
        tiaokongFlag=0
        for index in range(50):
            rate = (float(tiaokongData[k - index][6]) - float(tiaokongData[k - index][7])) / float(tiaokongData[k - index][7])
            if abs(rate) >0.05:
                tiaokongFlag = 1
                break
        return tiaokongFlag



    def dijian200(self,k,fuData):
        fu=float(fuData[k][30])-float(fuData[k-50][30])
        if fu>0:
            #200日均线的差，如果均线的差大于0，说明在上升期，如果均线的差小于零，那么就是处于下降期
            # print("200日均线的差" + str(fu))
            return 1
        return -1


    # K线的展示
    def show(self,data, code, name,show,choumaList,TavcPrice,tmax,csdnPrice):
        currentIndex=0
        showData=[]
        upLine=[]
        downLine=[]
        buyFlag=[]
        sallFlg=[]
        date20Buy=[]
        date20Buy1=[]
        chaodiBuy=[]
        tongdao=[]
        for k in range(len(data)):
            if k<1:
                continue
            currentIndex=int(data[k][0])
            line=[]
            #添加时间序列
            line.append(int(data[k][0]))
            #添加当日平均成本
            line.append(float(data[k][19]))
            #添加移动平均成本
            line.append(float(data[k][20]))
            #添加五日均线
            line.append(float(data[k][21]))
            #添加十日均线
            line.append(float(data[k][22]))
            #添加15日均线
            line.append(float(data[k][23]))
            #添加20均线
            line.append(float(data[k][24]))
            #添加30均线
            line.append(float(data[k][25]))
            #添加成交量
            line.append(float(data[k][8]))
            #添加5日平均成本均线
            avcCost5=(float(data[k][20])+float(data[k-1][20])
                      +float(data[k-2][20])+float(data[k-3][20])+float(data[k-4][20]))/5
            line.append(avcCost5)
            if float(data[k][29])>0:
                up=[]
                up.append(int(data[k][0]))
                up.append(float(data[k][29]))
                upLine.append(up)
            else:
                down=[]
                down.append(int(data[k][0]))
                down.append(float(data[k][29]))
                downLine.append(down)
            line.append(float(data[k][29]))
            #添加100日均线
            line.append(float(data[k][30]))
            #添加比较正式的成本线
            line.append(float(data[k][31]))
            #买入逻辑：在股价上升的时候，平均移动成本却在下降。那么基本可以断定估计散户在卖出，庄家在吸筹，我们买入的时候为了保险起见。
            #选择当天和之前的20天的平均移动成本和价格分别做减法，然后进行乘法，如果为负数表示有可能吸筹了
            #TODO 前提是价格不能跳空
            #step 1 --------------吸筹开始的时候进行定位
            if k>50:
                #30表示的200日均线，6表示的收盘价，20表示移动平均成本线
                #价格要小于200日均线，价格要高于移动平均成本线
                # float(data[k][30]) < float(data[k][6]) and
                if float(data[k][6])>float(data[k][20]) and float(data[k][6])>float(data[k][24]):
                    #当前的收盘价要高于50天前的收盘价（价格在递增）大于0
                    ditPrice=float(data[k][6])-float(data[k-50][6])

                    #当前的移动平均成本与50天之前的移动平均成本之差（递减） 小于 0
                    ditAcvPrice=float(data[k][24])-float(data[k-50][24])
                    #价格递增，移动平均成本递减。（一般会会有一次假突破，周期20-30天，这里取25吧。。。。）
                    if ditPrice>0 and ditAcvPrice <0:
                        if show==1:
                            print("当日价格："+str(data[k][6])+"    40天之前的价格:"+str(data[k-50][6]))
                            print("当日平均成本："+str(data[k][20])+"    40天之前的平均价格:"+str(data[k-50][20]))
                        tiaokongF20=self.tiaokong(k,data)
                        fu200=self.dijian200(k,data)
                        # if tiaokongF20==0:
                        date20temp=[]
                        date20temp.append(int(data[k][0]))
                        date20temp.append(float(data[k][6]))
                        date20Buy.append(date20temp)
                        #1表示庄家在吸筹了，大于零表示安全，小于0表示危险
                        data[k][31]=1
                    #设置安全标志，2表示安全
                    data[k][31]=2
                    td=[]
                    td.append(int(data[k][0]))
                    td.append(float(data[k][6]))
                    tongdao.append(td)
                #30表示的200日均线，6表示的收盘价，20表示移动平均成本线
                #价格要小于200日均线，价格要高于移动平均成本线 float(data[k][30]) < float(data[k][6]) and
                if float(data[k][24])<float(data[k][31]) and float(data[k][6])>float(data[k][24]):
                    ditPrice=float(data[k][24])-float(data[k-25][14])
                    ditAcvPrice=float(data[k][31])-float(data[k-25][31])
                    #价格递增，移动平均成本递减。（一般会会有一次假突破，周期20-30天，这里取25吧。。。。）


                    if ditPrice>0 and ditAcvPrice <0:
                        absPrice=abs(ditPrice)
                        absAvcPrice=abs(ditAcvPrice)
                        if absAvcPrice/absPrice>2:
                            date20temp = []
                            date20temp.append(int(data[k][0]))
                            date20temp.append(float(data[k][6]))
                            date20Buy1.append(date20temp)
                        if show==1:
                            print("当日价格："+str(data[k][6])+"    40天之前的价格:"+str(data[k-25][6]))
                            print("当日平均成本："+str(data[k][31])+"    40天之前的平均价格:"+str(data[k-25][31]))
                        tiaokongF20=self.tiaokong(k,data)
                        fu200=self.dijian200(k,data)
                        # if tiaokongF20==0:
                        date20temp=[]
                        date20temp.append(int(data[k][0]))
                        date20temp.append(float(data[k][6]))
                        date20Buy1.append(date20temp)
                        #1表示庄家在吸筹了，大于零表示安全，小于0表示危险
                        data[k][31]=1
                    #设置安全标志，2表示安全
                    data[k][31]=2
                    td=[]
                    td.append(int(data[k][0]))
                    td.append(float(data[k][6]))
                    tongdao.append(td)
                #吸筹买入
                if int(data[k-25][31])==1:
                    if float(data[k][6])<float(data[k-25][6]) or float(data[k][6])>float(data[k-25][6]):
                        chaodi=[]
                        chaodi.append(int(data[k][0]))
                        chaodi.append(float(data[k][6]))
                        chaodiBuy.append(chaodi)

            if k>6:
                #卖出策略，当平均成本和价格的距离越来越大，说明庄家在拉升股价，当价格与平均价格跳空很大的时候，基本就是定点时候
                if data[k][31]>=1:
                    # 计算变化快慢
                    currentRate = float(data[k][29]) - float(data[k - 1][29])
                    d1 = float(data[k - 1][29]) - float(data[k - 2][29])
                    d2 = float(data[k - 2][29]) - float(data[k - 3][29])
                    d3 = float(data[k - 3][29]) - float(data[k - 4][29])
                    d4 = float(data[k - 4][29]) - float(data[k - 5][29])
                    d5 = float(data[k - 5][29]) - float(data[k - 6][29])
                    ditAvcCostPrice = (d1 + d2 + d3 + d4 + d5) / 5
                    # d1 < 0 and d2 < 2 and d3 < 0 and d4 < 0 and d5 < 0 and
                    if ditAvcCostPrice > 0 and currentRate > 0 and currentRate > ditAvcCostPrice:
                        myBuy=[]
                        myBuy.append(int(data[k][0]))
                        myBuy.append(data[k][19])
                        sallFlg.append(myBuy)

                #使用价格与平均移动成本的差的变化率作为买入标志，当处于安全期的时候变化率到底就买入，但是变化率不能变为负数
                if data[k][31]>0:
                    #计算变化快慢
                    currentRate=float(data[k][29])-float(data[k-1][29])
                    d1=float(data[k-1][29])-float(data[k-2][29])
                    d2=float(data[k-2][29])-float(data[k-3][29])
                    d3=float(data[k-3][29])-float(data[k-4][29])
                    d4=float(data[k-4][29])-float(data[k-5][29])
                    d5=float(data[k-5][29])-float(data[k-6][29])
                    ditAvcCostPrice=(d1+d2+d3+d4+d5)/5
                    # d1 < 0 and d2 < 2 and d3 < 0 and d4 < 0 and d5 < 0 and
                    if  ditAvcCostPrice<0 and currentRate>0 and currentRate > ditAvcCostPrice:
                        #回调到了低点
                        #如果价格跳空了就不能买
                        # tiaokongF=tiaokong(k,data)
                        # fu50=dijian200(k,data)
                        # if tiaokongF==1 and fu50==1:
                        myBuy=[]
                        myBuy.append(int(data[k][0]))
                        myBuy.append(data[k][19])
                        buyFlag.append(myBuy)

            showData.append(line)
        # 需要显示的时候进行显示
        realUp = np.array(upLine)
        realDown = np.array(downLine)
        realSall = np.array(sallFlg)
        realBuy = np.array(buyFlag)
        chaodiBuy = np.array(chaodiBuy)
        buy20Before = np.array(date20Buy)
        buy20Before1 = np.array(date20Buy1)
        if show==1:
            fig=plt.figure()
            ax=fig.add_axes([0.1,0.35,0.6,0.6])
            bx=fig.add_axes([0.1,0.2,0.6,0.1])
            cx=fig.add_axes([0.1,0.05,0.6,0.1])
            cmx=fig.add_axes([0.7,0.35,0.2,0.6])
            print(choumaList)
            chouMalit=np.array(choumaList)
            cmx.barh(chouMalit[:,0],chouMalit[:,1],color="lightblue",align="center")
            cmx.barh(TavcPrice,tmax,color="red",lw="3")
            cmx.axvline(0,color="gray",linewidth=0)

            ax.set(title=code+"-"+name+"--avcPrice"+str(round(TavcPrice/100,2)))
            myTongdao=np.array(tongdao)
            if len(tongdao):
                ax.scatter(myTongdao[:,0],myTongdao[:,1],color="yellow",lw=4)

            csdnList=np.array(csdnPrice)
            showTX=np.array(showData)
            #画平均成本
            ax.plot(showTX[:,0],showTX[:,1],color="green")
            ax.plot(csdnList[:,0],csdnList[:,1],color="#28FE3f")
            #画移动平均成本
            ax.plot(showTX[:,0],showTX[:,2],color="red")
            #画五日均线
            # ax.plot(showTX[:,0],showTX[:,3])
            # #画十日均线
            # ax.plot(showTX[:,0],showTX[:,4])
            # #画十五日均线
            ax.plot(showTX[:,0],showTX[:,5])
            # #画二十日均线
            # ax.plot(showTX[:,0],showTX[:,6])
            # #画三十日均线
            # ax.plot(showTX[:,0],showTX[:,7],color="black")
            #画5日移动平均成本
            # ax.plot(showTX[:,0],showTX[:,9],color="black",lw=1)
            #画100日均线
            ax.plot(showTX[:,0],showTX[:,11],color="#899F86")
            #二十日之前的平均成本和价格的差的乘法
            if len(buy20Before)>0:
                ax.scatter(buy20Before[:,0],buy20Before[:,1],color="black",lw="0.1")
            if len(buy20Before1)>0:
                ax.scatter(buy20Before1[:,0],buy20Before1[:,1],color="blue",lw="0.05")

            #画成交量
            cx.bar(showTX[:,0],showTX[:,8],color="red")
            if len(realUp)>0:
                bx.plot(realUp[:,0],realUp[:,1],color="green")
            if len(realDown)>0:
                bx.plot(realDown[:,0],realDown[:,1],color="red")
                if len(realBuy)>0:
                    bx.scatter(realBuy[:,0],realBuy[:,1]-realBuy[:,1],marker="+")
                if len(realSall)>0:
                    bx.scatter(realSall[:,0],realSall[:,1]-realSall[:,1],color="orange",marker="+")
            if len(realSall)>0:
                ax.scatter(realSall[:, 0], realSall[:, 1], color="blue",marker="*", lw="1")
            if len(realBuy)>0:
                ax.scatter(realBuy[:,0],realBuy[:,1],color="black",marker="+")
            if len(chaodiBuy)>0:
                ax.scatter(chaodiBuy[:,0],chaodiBuy[:,1],color="green",marker="*")
            cx.legend()
            bx.legend()
            ax.legend()
            # plt.show()
            plt.savefig("E:\\"+code+".png")
        if show==0:
            state=0
            mainLength = currentIndex
            chaodiIndex=len(buy20Before1)-1
            # print(buy20Before)
            if chaodiIndex>=0:
                #mychaodiRange=buy20Before[chaodiIndex][0]+5
                mychaodiRange=buy20Before1[chaodiIndex][0]+5
                # buy20Before1[chaodiIndex][0]+5;
                if mainLength<=mychaodiRange:
                    state=1
            # buyIndex=len(realBuy)-1
            # if buyIndex>=0:
            #     buyRange=realBuy[buyIndex][0]+5
            #     if mainLength<=buyRange:
            #         state=1
            if state==0:
                self.cleanFlag=1
                print("\r %s      %s     %s" % (self.index,code,name), end=" ")
            else:
              if self.cleanFlag==0:
                print(" %s      %s       %s" % (self.index,code,name), end="\n")
              else:
                  print("\r %s      %s      %s" % (self.index,code,name))



    # 存入mysql
    # def save2mysql(data,code):
    #     engine = create_engine('mysql://root:tianjingle@127.0.0.1/baostock?charset=utf8')
    #     realCode=code.replace(".","");
    #     print(realCode)
    #     sqlData=pd.DataFrame(data)
    #     sqlData.to_sql(realCode,engine,if_exists='replace')


    def start(self,myflag,date,isShow,stockCode):
        csvFile = open("../data/basic_tushare.csv", "r", encoding="UTF-8")
        reader = csv.reader(csvFile)
        for stock in reader:
            self.index=stock[0]
            if myflag == 0:
                myflag = 1
                continue
            else:
                myflag = myflag + 1
            # 排除指数
            #115

            if int(len(stock[3])<8) or int(stock[0])<943:
                continue
            # 查看个别
            if isShow == 1:
                if int(stock[0]) != int(stockCode):
                    continue
            if int(stock[0]) >= 1 and stock[4] == '':
                # data = baoStackReq(stock[1],stock[3])
                mydata = self.baoStackReqFile(stock[1], stock[3])
                data = pd.DataFrame(mydata)
                # 平均成本19
                data['avccost'] = 0
                # 移动平均成本20
                data['moveavccost'] = 0
                data['ma5'] = 0
                # 十日均线
                data['ma10'] = 0
                # 20日均线
                data['ma15'] = 0
                # 30日均线
                data['ma20'] = 0
                data['ma30'] = 0
                data['vma5'] = 0
                data['vma10'] = 0
                data['vma15'] = 0
                data['pricecost'] = 0
                data['mav100'] = 0
                data['secure'] = 0
                data['csdn']=0
                targetData = np.array(data)
                Ktemp = []
                for i in range(len(targetData)):
                    if i >= 1:
                        if targetData[i][8] == '':
                            targetData[i][8] = 0
                        if float(targetData[i][8]) != 0:
                            avcCost = float(targetData[i][9]) / float(targetData[i][8])
                        else:
                            avcCost = Ktemp[19]
                        # 当日的平均价格
                        targetData[i][19] = avcCost
                        if i == 1:
                            targetData[i][20] = avcCost
                        else:
                            # 移动平均成本
                            if targetData[i][11] != '' and int(targetData[i][12]) == 1:
                                targetData[i][20] = float(targetData[i - 1][20]) * (
                                            1 - float(targetData[i][11]) / 100) + float(targetData[i][19]) * (
                                                                float(targetData[i][11]) / 100)
                            else:
                                targetData[i][20] = Ktemp[20]
                    Ktemp = targetData[i]
                    mav = [0, 0, 0, 0, 0]
                    vav = [0, 0, 0]
                    mav100 = 0
                    # 五日均线
                    if i > 5:
                        mavSum=0
                        for mvindex in range(5):
                            mavSum=mavSum+float(targetData[i-mvindex][6])
                        mav[1]=mavSum/5
                        mavSum=0
                        for mvindex in range(5):
                            mavSum=mavSum+float(targetData[i-mvindex][8])
                        vav[0]=mavSum/5
                    # 十日均线
                    if i > 10:
                        k = targetData[i]
                        mavSum=0
                        for mvindex in range(10):
                            mavSum=mavSum+float(targetData[i-mvindex][6])
                        mav[1]=mavSum/10
                        mavSum=0
                        for mvindex in range(10):
                            mavSum=mavSum+float(targetData[i-mvindex][8])
                        vav[1]=mavSum/10
                    # 十五日均线
                    if i > 15:
                        mavSum=0
                        for mvindex in range(15):
                            mavSum=mavSum+float(targetData[i-mvindex][6])
                        mav[2]=mavSum/15

                        mavSum=0
                        for mvindex in range(15):
                            mavSum=mavSum+float(targetData[i-mvindex][8])
                        vav[2]=mavSum/15
                        # 十五日均线
                    if i > 20:
                        mavSum=0
                        for mvindex in range(20):
                            mavSum=mavSum+float(targetData[i-mvindex][6])
                        mav[3]=mavSum/20

                    if i > 31:
                        mavSum=0
                        for mvindex in range(30):
                            mavSum=mavSum+float(targetData[i-mvindex][6])
                        mav[4]=mavSum/30
                    if i > 200:
                        mavSum = 0
                        for mavindex in range(200):
                            mavSum = mavSum + float(targetData[i - mavindex][6])
                        mav100 = mavSum / 200

                    # 设置移动均线
                    targetData[i][21] = mav[0]
                    targetData[i][22] = mav[1]
                    targetData[i][23] = mav[2]
                    targetData[i][24] = mav[3]
                    targetData[i][25] = mav[4]

                    # 设置移动均量
                    targetData[i][26] = vav[0]
                    targetData[i][27] = vav[1]
                    targetData[i][28] = vav[2]
                    targetData[i][29] = targetData[i][20] - targetData[i][19]
                    targetData[i][30] = mav100
                # save2mysql(targetData,stock[1])
                currentData = self.parse2Current(targetData, date)
                chouma=ChouMa()
                currentData,chouMaList,TavcPrice,tmax,csdnPrice=chouma.getDataByShowLine(currentData)
                self.show(currentData, stock[1],stock[2], isShow,chouMaList,TavcPrice,tmax,csdnPrice)


#程序的运行
if __name__ == '__main__':
    myShowLine=showLine()
    myShowLine.start(myflag,date,isShow,stockCode)
