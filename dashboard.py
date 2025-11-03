from tkinter import *

window=Tk()

window.title('Dashboard')
window.geometry('1270x668+0+0')
window.resizable(0,0)
window.config(bg='#fef9fb')

bg_image=PhotoImage(file='inventory.png')
titleLable=Label(window,image=bg_image,compound=LEFT,text='                               سیستم فروش و انبار داری ',font=('Yekan',30,'bold'), bg='#813ffe',fg='#07070a',anchor='w',padx=20)
titleLable.place(x=0,y=0,relwidth=1)

logoButten=Button(window,text='خروج',font=('Yekan',16,'bold'),fg='#07070a')
logoButten.place(x=1100,y=10)

SubtitleLabel=Label(window,text='ادمین خوش آمدید\t\t تاریخ: 01-11-2025\t\t ساعت:14:36:17',font=('Yekan',15),bg='#4b39e9',fg='#fef9fb')
SubtitleLabel.place(x=0,y=70,relwidth=1)

leftFrame=Frame(window)
leftFrame.place(x=0,y=107,width=200,height=560)

LogoImage=PhotoImage(file='checklist-1.png')
imageLable=Label(leftFrame,image=LogoImage)
imageLable.grid(row=0,column=0)


window.mainloop()

