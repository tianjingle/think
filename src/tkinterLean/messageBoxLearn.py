import tkinter as tk
import tkinter.messagebox
window=tk.Tk()
window.geometry('500x300')

def show():
    tkinter.messagebox.showinfo(title='hello',message='你好')

    newwindow = tk.Toplevel(window)
    newwindow.geometry('400x67')
    # tkinter.messagebox.showerror(title='1',message='error')
    # print("三种："+tkinter.messagebox.askquestion(title='2',message='asdfsadfsa'))
    # print(tkinter.messagebox.askyesno(title='3',message='asfsafsadfaf'))
    # print(tkinter.messagebox.askyesnocancel(title='4',message='asfasfsfsfsf'))

button1=tk.Button(window,text='in frame1',command=show)
button1.place(x=100,y=100)
window.mainloop()