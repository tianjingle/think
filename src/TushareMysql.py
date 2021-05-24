import baostock as bs
import pandas as pd
import numpy as np
import csv
import matplotlib.pyplot as plt

###
###将数据保存到数据库中
def baoStackReq(code,start):
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
def baoStackReqFile(code,start):
    myCode=code.replace(".","")
    myFile=open("../data/"+myCode+".csv","r",encoding="UTF-8")
    myReader=csv.reader(myFile)
    dataTemp=[]
    for zz in myReader:
        dataTemp.append(zz)
    return dataTemp


#转化成最近的多少天的数据
def parse2Current(targetData,data):
    tempData=[]
    start=len(targetData)-data
    for zz in range(len(targetData)):
        if zz> start:
            tempData.append(targetData[zz])
        else:
            continue
    return tempData


#判断最近50天是否出现价格的跳空
def tiaokong(k,tiaokongData):
    tiaokongFlag=0
    for index in range(50):
        rate = (float(tiaokongData[k - index][6]) - float(tiaokongData[k - index][7])) / float(tiaokongData[k - index][7])
        if abs(rate) >0.05:
            tiaokongFlag = 1
            break
    return tiaokongFlag



def dijian200(k,fuData):
    fu=float(fuData[k][30])-float(fuData[k-50][30])
    if fu>0:
        #200日均线的差，如果均线的差大于0，说明在上升期，如果均线的差小于零，那么就是处于下降期
        # print("200日均线的差" + str(fu))
        return 1
    return -1


# K线的展示
def show(data,code,show):
    # fig=plt.figure()
    showData=[]
    upLine=[]
    downLine=[]
    buyFlag=[]
    sallFlg=[]
    date20Buy=[]
    chaodiBuy=[]
    tongdao=[]
    for k in range(len(data)):
        if k<1:
            continue
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
        #买入逻辑：在股价上升的时候，平均移动成本却在下降。那么基本可以断定估计散户在卖出，庄家在吸筹，我们买入的时候为了保险起见。
        #选择当天和之前的20天的平均移动成本和价格分别做减法，然后进行乘法，如果为负数表示有可能吸筹了
        #TODO 前提是价格不能跳空
        #step 1 --------------吸筹开始的时候进行定位
        if k>50:
            #30表示的200日均线，6表示的收盘价，20表示移动平均成本线
            #价格要小于200日均线，价格要高于移动平均成本线
            if float(data[k][30]) < float(data[k][6]) and float(data[k][6])>float(data[k][20]) and float(data[k][6])>float(data[k][24]):
                ditPrice=float(data[k][6])-float(data[k-50][6])
                ditAcvPrice=float(data[k][20])-float(data[k-50][20])
                #价格递增，移动平均成本递减。（一般会会有一次假突破，周期20-30天，这里取25吧。。。。）
                if ditPrice>0 and ditAcvPrice <0:
                    if show==1:
                        print("当日价格："+str(data[k][6])+"    40天之前的价格:"+str(data[k-50][6]))
                        print("当日平均成本："+str(data[k][20])+"    40天之前的平均价格:"+str(data[k-50][20]))
                    tiaokongF20=tiaokong(k,data)
                    fu200=dijian200(k,data)
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
    # if show==1:
        # ax=fig.add_axes([0.1,0.35,0.8,0.6])
        # bx=fig.add_axes([0.1,0.2,0.8,0.1])
        # cx=fig.add_axes([0.1,0.05,0.8,0.1])
        #
        # myTongdao=np.array(tongdao)
        # if len(tongdao):
        #     ax.scatter(myTongdao[:,0],myTongdao[:,1],color="yellow",lw=4)
        #
        # showTX=np.array(showData)
        # #画平均成本
        # ax.plot(showTX[:,0],showTX[:,1],color="green")
        # #画移动平均成本
        # ax.plot(showTX[:,0],showTX[:,2],color="red")
        # #画五日均线
        # # ax.plot(showTX[:,0],showTX[:,3])
        # # #画十日均线
        # # ax.plot(showTX[:,0],showTX[:,4])
        # # #画十五日均线
        # # ax.plot(showTX[:,0],showTX[:,5])
        # # #画二十日均线
        # # ax.plot(showTX[:,0],showTX[:,6])
        # # #画三十日均线
        # ax.plot(showTX[:,0],showTX[:,7])
        # #画5日移动平均成本
        # ax.plot(showTX[:,0],showTX[:,9],color="black",lw=1)
        # #画100日均线
        # ax.plot(showTX[:,0],showTX[:,11])
        # #二十日之前的平均成本和价格的差的乘法
        # buy20Before=np.array(date20Buy)
        # if len(buy20Before)>0:
        #     ax.scatter(buy20Before[:,0],buy20Before[:,1],color="black",lw="0.1")
        #
        # #画成交量
        # cx.bar(showTX[:,0],showTX[:,8],color="red")
        # if len(realUp)>0:
        #     bx.plot(realUp[:,0],realUp[:,1],color="green")
        # if len(realDown)>0:
        #     bx.plot(realDown[:,0],realDown[:,1],color="red")
        #     if len(realBuy)>0:
        #         bx.scatter(realBuy[:,0],realBuy[:,1]-realBuy[:,1],marker="+")
        #     bx.scatter(realSall[:,0],realSall[:,1]-realSall[:,1],color="orange",marker="+")
        # if len(realSall)>0:
        #     ax.scatter(realSall[:, 0], realSall[:, 1], color="blue",marker="*", lw="1")
        # if len(realBuy)>0:
        #     ax.scatter(realBuy[:,0],realBuy[:,1],color="black",marker="+")
        # if len(chaodiBuy)>0:
        #     ax.scatter(chaodiBuy[:,0],chaodiBuy[:,1],color="green",marker="*")
        # cx.legend()
        # bx.legend()
        # ax.legend()
        # plt.show()
    if show==0:
        state=0
        mainLength = len(data)
        chaodiIndex=len(chaodiBuy)-1
        if chaodiIndex>=0:
            mychaodiRange=chaodiBuy[chaodiIndex][0]+20
            if mainLength<=mychaodiRange:
                state=1
        # buyIndex=len(realBuy)-1
        # if buyIndex>=0:
        #     buyRange=realBuy[buyIndex][0]+5
        #     if mainLength<=buyRange:
        #         state=1
        if state==1:
            print("---"+code)


#存入mysql
# def save2mysql(data,code):
#     engine = create_engine('mysql://root:tianjingle@127.0.0.1/baostock?charset=utf8')
#     realCode=code.replace(".","");
#     print(realCode)
#     sqlData=pd.DataFrame(data)
#     sqlData.to_sql(realCode,engine,if_exists='replace')




#程序的运行
csvFile=open("../data/basic.csv","r",encoding="UTF-8")
reader=csv.reader(csvFile)
myflag=0
date=800
stockCode="1369"
for stock in reader:
    if myflag==0:
        myflag=1
        continue
    else:
        myflag=myflag+1
    if int(stock[0])<115:
        continue
    if int(stock[0]) >= 1 and stock[4] == '':
        # data = baoStackReq(stock[1],stock[3])
        mydata = baoStackReqFile(stock[1],stock[3])
        data=pd.DataFrame(mydata)
        #平均成本19
        data['avccost'] = 0
        #移动平均成本20
        data['moveavccost']=0
        data['ma5'] = 0
        #十日均线
        data['ma10'] = 0
        #20日均线
        data['ma15'] = 0
        #30日均线
        data['ma20'] = 0
        data['ma30'] = 0
        data['vma5'] = 0
        data['vma10'] = 0
        data['vma15'] = 0
        data['pricecost'] = 0
        data['mav100']=0
        data['secure'] = 0
        targetData=np.array(data)
        avcCost=0
        Ktemp=[]
        for i in range(len(targetData)):
            if i>=1:
                if float(targetData[i][8])!=0:
                    avcCost=float(targetData[i][9])/float(targetData[i][8])
                else:
                    avcCost=Ktemp[19]
                #当日的平均价格
                targetData[i][19] = avcCost
                if i==1:
                    targetData[i][20]=avcCost
                else:
                     #移动平均成本
                    if targetData[i][11]!='' and int(targetData[i][12])==1:
                       targetData[i][20]=float(targetData[i-1][20])*(1-float(targetData[i][11])/100)+float(targetData[i][19])*(float(targetData[i][11])/100)
                    else:
                      targetData[i][20]=Ktemp[20]
            Ktemp = targetData[i]
            mav=[0,0,0,0,0]
            vav=[0,0,0]
            mav100=0
            #五日均线
            if i>5:
                mav[0]=(float(targetData[i][19])+float(targetData[i-1][19])+float(targetData[i-2][19])+float(targetData[i-3][19])+float(targetData[4][19]))/5
                vav[0]=(float(targetData[i][8])+float(targetData[i-1][8])+float(targetData[i-2][8])+float(targetData[i-3][8])+float(targetData[4][8]))/5
            #十日均线
            if i>10:
                k=targetData[i]
                mav[1]=(float(targetData[i][19])+float(targetData[i-1][19])+float(targetData[i-2][19])+
                             float(targetData[i-3][19])+float(targetData[i-4][19])+float(targetData[i-5][19])+
                        float(targetData[i-6][19])+float(targetData[i-7][19])+float(targetData[i-8][19])+
                             float(targetData[i-9][19]))/10
                test=float(targetData[i][8])+float(targetData[i-1][8])+float(targetData[i-2][8])+float(targetData[i-3][8])+float(targetData[i-4][8])+float(targetData[i-5][8])+float(targetData[i-6][8])+float(targetData[i-7][8])+float(targetData[i-8][8])+float(targetData[i-9][8])
                vav[1]=float(test/10)
            #十五日均线
            if i>15:
                mav[2] = float((float(targetData[i][19]) + float(targetData[i - 1][19]) + float(
                    targetData[i - 2][19]) + float(targetData[i - 3][19]) + float(targetData[i - 4][19]) + float(
                    targetData[i - 5][19]) +
                                float(targetData[i - 6][19]) + float(targetData[i - 7][19]) + float(
                            targetData[i - 8][19]) + float(targetData[i - 9][19]) +
                                float(targetData[i - 10][19]) + float(targetData[i - 11][19]) + float(
                            targetData[i - 12][19]) + float(targetData[i - 13][19]) + float(
                            targetData[i - 14][19])) / 15)
                vav[2] = float((float(targetData[i][8]) + float(targetData[i - 1][8]) + float(
                    targetData[i - 2][8]) + float(targetData[i - 3][8]) + float(targetData[4][8]) + float(
                    targetData[i - 5][8]) +
                                float(targetData[i - 6][8]) + float(targetData[i - 7][8]) + float(
                            targetData[i - 8][8]) + float(targetData[i - 9][8]) +
                                float(targetData[i - 10][8]) + float(targetData[i - 11][8]) + float(
                            targetData[i - 12][8]) + float(targetData[i - 13][8]) + float(targetData[i - 14][8])) / 15)
                # 十五日均线
            if i > 20:
                mav[3] = float((float(targetData[i][19]) + float(targetData[i - 1][19]) + float(
                    targetData[i - 2][19]) + float(targetData[i - 3][19]) +
                                float(targetData[i - 4][19]) + float(targetData[i - 5][19]) +
                                float(targetData[i - 6][19]) + float(targetData[i - 7][19]) + float(
                            targetData[i - 8][19]) + float(targetData[i - 9][19]) +
                                float(targetData[i - 10][19]) + float(targetData[i - 11][19]) + float(
                            targetData[i - 12][19]) +
                                float(targetData[i - 13][19]) + float(targetData[i - 14][19]) + float(
                            targetData[i - 15][19]) + float(targetData[i - 16][19]) + float(targetData[i - 17][19]
                                                                                            ) + float(
                            targetData[i - 18][19]) + float(targetData[i - 19][19])) / 20)

            if i>30:
                mav[4]=float((float(targetData[i][19] )+ float(targetData[i - 1][19] )+ float(targetData[i - 2][19] )+ float(targetData[i - 3][19] )+
                            float(targetData[i-4][19] )+ float(targetData[i - 5][19] )+
                            float(targetData[i - 6][19] )+ float(targetData[i - 7][19] )+ float(targetData[i - 8][19] )+ float(targetData[i - 9][19] )+
                            float(targetData[i - 10][19] )+ float(targetData[i - 11][19] )+ float(targetData[i - 12][19] )+
                            float(targetData[i - 13][19] )+ float(targetData[i - 14][19] )+ float(targetData[i - 15][19] )+
                            float(targetData[i - 16][19] )+ float(targetData[i - 17][19]
                            )+ float(targetData[i - 18][19] )+ float(targetData[i - 19][19])+float(targetData[i - 20][19] )+ float(targetData[i - 21][19] )+ float(targetData[i - 12][19] )+
                            float(targetData[i - 22][19] )+ float(targetData[i - 23][19] )+ float(targetData[i - 24][19] )+
                            float(targetData[i - 25][19] )+ float(targetData[i - 26][19]
                            )+ float(targetData[i - 27][19] )+ float(targetData[i - 28][19])+targetData[i-29][19])) / 30
            if  i>200:
                mavSum=0
                for mavindex in range(200):
                    mavSum=mavSum+float(targetData[i-mavindex][19])
                mav100=mavSum/200

            #设置移动均线
            targetData[i][21]=mav[0]
            targetData[i][22]=mav[1]
            targetData[i][23]=mav[2]
            targetData[i][24]=mav[3]
            targetData[i][25]=mav[4]

            #设置移动均量
            targetData[i][26]=vav[0]
            targetData[i][27]=vav[1]
            targetData[i][28]=vav[2]
            targetData[i][29]=targetData[i][19]-targetData[i][20]
            targetData[i][30]=mav100
            # print(targetData[i])
        # save2mysql(targetData,stock[1])
        # print(stock[0]+"--"+stock[1])
        #395
        # if stock[0]=='598':
        #     break
        # if stock[0]==stockCode:
        #     currentData=[]
        #     currentData=parse2Current(targetData,date)
        #     show(currentData)
        #     break
        currentData=[]
        currentData=parse2Current(targetData,date)
        show(currentData,stock[1],0)
