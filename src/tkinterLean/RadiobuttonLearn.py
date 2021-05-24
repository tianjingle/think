import tkinter as tk

window=tk.Tk()
window.geometry('500x300')
showText=tk.StringVar()
var=tk.StringVar()
labelOne=tk.Label(window,textvariable=showText,bg='red',width=50)
labelOne.pack()
def show():
    showText.set(var.get())
radio1=tk.Radiobutton(window,text='java',variable=var,value='1',command=show)
radio2=tk.Radiobutton(window,text='python',variable=var,value='2',command=show)
radio3=tk.Radiobutton(window,text='c',variable=var,value='3',command=show)
radio1.pack()
radio2.pack()
radio3.pack()
window.mainloop()