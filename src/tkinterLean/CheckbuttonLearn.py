import tkinter as tk

window=tk.Tk()
window.geometry('500x300')
showText=tk.StringVar()
labelOne=tk.Label(window,textvariable=showText,width=40,bg='red')
labelOne.pack()
def show():
    v1=int(var.get())
    v2=int(var1.get())
    print(v1)
    print(v2)
    if v1==1 and v2==1:
        showText.set('select all')
    elif v1==0 and v2==1:
        showText.set('select two')
    elif v1==1 and v2==0:
        showText.set('select one')
    else:
        showText.set('no select ')

var=tk.StringVar()
var1=tk.StringVar()
CheckOne=tk.Checkbutton(window,text='java',variable=var,onvalue=1,offvalue=0,command=show)
CheckTwo=tk.Checkbutton(window,text='python',variable=var1,onvalue=1,offvalue=0,command=show)
CheckOne.pack()
CheckTwo.pack()
window.mainloop()


