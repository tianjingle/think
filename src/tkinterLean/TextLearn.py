import tkinter as tk

def insert_action():
    var=insert.get()
    print(var)
    text.insert('insert',var)
def insert_end_action():
    var=insert.get()
    print(var)
    text.insert('end',var)

window=tk.Tk()
window.geometry('500x300')
insert=tk.Entry(window,show=None)
insert.pack()
text=tk.Text(window,height=5)
text.pack()
button=tk.Button(window,text='insert',command=insert_action)
buttonEnd=tk.Button(window,text='end',command=insert_end_action)
button.pack()
buttonEnd.pack()
window.mainloop()

