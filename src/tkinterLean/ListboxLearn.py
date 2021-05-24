import tkinter as tk

window=tk.Tk()
window.geometry('500x500')
window.title('test list box')
showText=tk.StringVar()
labelName=tk.Label(window,bg='red',width=30,textvariable=showText)
labelName.pack()

def listenerOne(event):
    var=listBoxOne.get(listBoxOne.curselection())
    print(var)
    showText.set(var)

def multiSelect():
    value=''
    for item in listBoxTwo.curselection():
        var=listBoxTwo.get(item)
        value+=var
    showText.set(value)

#单选模式
listBoxOne=tk.Listbox(window)
#多选模式
listBoxTwo=tk.Listbox(window,selectmode=tk.EXTENDED)

listBoxOne.bind('<Double-Button-1>',listenerOne)
lanaguage=['java','python','c','c++','js']
for item in lanaguage:
    listBoxOne.insert('end',item)
    listBoxTwo.insert('end',item)

listBoxOne.pack()
listBoxTwo.pack()


buttonOne=tk.Button(window,text='extended button',command=multiSelect)
buttonOne.pack()

window.mainloop()