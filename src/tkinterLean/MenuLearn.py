import tkinter as tk
window=tk.Tk()
window.geometry('500x300')

#主菜单
mainMenu=tk.Menu(window)

first=tk.Menu(mainMenu,tearoff=0)
#将主菜单设置为空，其子菜单为first
mainMenu.add_cascade(label='文件',menu=first)

def new():
    print()


first.add_command(label='one',command=new)
first.add_command(label='two',command=new)
first.add_command(label='three',command=new)
first.add_separator()
first.add_command(label='exit',command=window.quit)

two=tk.Menu(mainMenu,tearoff=0)
mainMenu.add_cascade(label='设置',menu=two)
two.add_command(label='one',command=new)
two.add_command(label='one1',command=new)
two.add_command(label='one2',command=new)


window.config(menu=mainMenu)
window.mainloop()