import tkinter as tk
window=tk.Tk()
window.geometry('500x300')

frame1=tk.Frame(window)
lable1=tk.Label(frame1,text='in frame1',bg='red').pack()
frame1.pack()
window.mainloop()