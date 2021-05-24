import math
import numpy as np
import matplotlib.pyplot as plt
xx=[]
yy=[]
lamd=0.7
z=30
k=0.00009
x=math.pow( 1+k, z )
month=20
n = np.arange(1, month*12, 1)
a0=5.9
dit=5.9
card=[]
bk=0.000003/365
bx=math.pow( 1+bk, z )
for i in n:
    un=a0*math.pow(x,i)+lamd*((1-math.pow(x,i-1))/(1-x))
    xx.append(i)
    yy.append(un)
    dit = a0 * math.pow(bx, i) + lamd * ((1 - math.pow(bx, i - 1)) / (1 - bx))
    card.append(dit)
str="1/10000="+str((k*10000))+",invest/month="+str(lamd*10000)+",count="+str(month)+"years\ntotal rmb="+str(yy[len(yy)-1])
plt.title(str)
plt.plot(xx, yy, label="yu e bao")
plt.plot(xx,card,label="bank",linestyle = "--")
plt.xlabel("x")
plt.ylabel("y")
plt.ylim(0, yy[len(yy)-1]+30)
plt.legend()
plt.show()
