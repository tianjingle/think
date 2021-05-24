import tkinter as tk

window=tk.Tk()
#设置窗口大小
window.geometry('300x200')
#获取一个输入框，展示的时候显示&
entry1=tk.Entry(window,show='&',font=('Arial', 14))
#获取一个输入框，展示的时候采用明文
entry2=tk.Entry(window,show=None,font=('Arial', 14))
entry1.pack()
entry2.pack()
window.mainloop()