import tkinter as tk
# 拿到总窗口
window=tk.Tk()
#定义一个字符串
wordTest=tk.StringVar()
#用于设置按钮的切换，走不同的逻辑
hind=True
def testButton():
    print("点击了")
    global hind
    if hind==False:
        print("1")
        hind=True
        wordTest.set('tij')
    else:
        print("2")
        wordTest.set('please click me')
        hind=False

# 设置标题
window.title('tkinter study')
# window.geometry('500x300')
# 设置窗口大小
window.geometry('888x500')
# 设置lable的名称，背景颜色，字体，宽长，
lableOne=tk.Label(window,textvariable=wordTest,bg='red',font=('Arial',12),width=10,height=2)
# 创建一个按钮
buttonOne=tk.Button(window,text='button',command=testButton)
# 放置lable
lableOne.pack()
# 放置按钮
buttonOne.pack()
# 显示窗口
window.mainloop()


