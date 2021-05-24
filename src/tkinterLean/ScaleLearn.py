import tkinter as tk
window=tk.Tk()
window.geometry('500x300')
showText=tk.StringVar()
lableOne=tk.Label(window,textvariable=showText,width=50,bg='red')
lableOne.pack()
def show(value):
    print(value)
    showText.set(value)
scaleOne=tk.Scale(window,label='scale',from_=0,to=100,orient=tk.HORIZONTAL,length=600,showvalue=0,tickinterval=1,resolution=1,command=show)
scaleOne.pack()
window.mainloop()