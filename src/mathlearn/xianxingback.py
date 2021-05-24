import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import leastsq

##样本数据(Xi,Yi)，需要转换成数组(列表)形式
Xi = np.array([1, 2, 3, 4, 5, 6, 7])
Yi = np.array([4.99,4.98,5.01,5.01,5.01,5.04,5.04])


##需要拟合的函数func :指定函数的形状 k= 0.42116973935 b= -8.28830260655
def func(p, x):
    k, b = p
    return k * x + b


##偏差函数：x,y都是列表:这里的x,y更上面的Xi,Yi中是一一对应的
def error(p, x, y):
    return func(p, x) - y


# k,b的初始值，可以任意设定,经过几次试验，发现p0的值会影响cost的值：Para[1]
p0 = [1, 20]

# 把error函数中除了p0以外的参数打包到args中(使用要求)
Para = leastsq(error, p0, args=(Xi, Yi))

print(Para)
# 读取结果
k, b = Para[0]
print("k=", k, "b=", b)

# 画样本点
plt.figure(figsize=(8, 6))  ##指定图像比例： 8：6
plt.scatter(Xi, Yi, color="green", label="source", linewidth=2)

# 画拟合直线
x = np.linspace(150, 190, 100)  ##在150-190直接画100个连续点
y = k * x + b  ##函数式
plt.plot(x, y, color="red", label="target", linewidth=2)
plt.legend()  # 绘制图例
plt.show()