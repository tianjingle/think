import tkinter as tk
window=tk.Tk()
window.geometry('500x300')
canvasOne=tk.Canvas(window,bg='red',height=500,width=200)


x0, y0, x1, y1 = 100, 100, 150, 150
line = canvasOne.create_line(x0-50, y0-50, x1-50, y1-50)                   # 画直线
oval = canvasOne.create_oval(x0+120, y0+50, x1+120, y1+50, fill='yellow')  # 画圆 用黄色填充
arc = canvasOne.create_arc(x0, y0+50, x1, y1+50, start=0, extent=180)      # 画扇形 从0度打开收到180度结束
rect = canvasOne.create_rectangle(330, 30, 330+20, 30+20)                  # 画矩形正方形

canvasOne.pack()
window.mainloop()