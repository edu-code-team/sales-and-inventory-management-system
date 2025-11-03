from tkinter import *

window=Tk()

window.title('Dashboard')
window.geometry('1270x668+0+0')
window.resizable(0,0)
window.config(bg='#fef9fb')

bg_image=PhotoImage(file='inventory.png')
titleLable=Label(window,image=bg_image,compound=LEFT,text='                               سیستم فروش و انبار داری ',font=('Yekan',30,'bold'), bg='#813ffe',fg='#07070a',anchor='w',padx=20)
titleLable.place(x=0,y=0,relwidth=1)

logoButten=Button(window,text='  خروج  ',bg='#4b39e9',font=('Yekan',16,'bold'),fg='#fef9fb')
logoButten.place(x=1100,y=10)

SubtitleLabel=Label(window,text='ادمین خوش آمدید\t\t تاریخ: 01-11-2025\t\t ساعت:14:36:17',font=('Yekan',15),bg='#4b39e9',fg='#fef9fb')
SubtitleLabel.place(x=0,y=70,relwidth=1)

leftFrame=Frame(window)
leftFrame.place(x=0,y=107,width=200,height=560)

LogoImage=PhotoImage(file='checklist-1.png')
imageLable=Label(leftFrame,image=LogoImage)
imageLable.pack()


menuLabel=Label(leftFrame,text='منو',font=('Yekan',13),bg='#00198f')
menuLabel.pack(fill=X)


employee_icon=PhotoImage(file='employee.png')
employee_button=Button(leftFrame,image=employee_icon,compound=LEFT,text='         کارمندان',font=('Yekan',15,'bold'))
employee_button.pack(fill=X)


supplier_icon=PhotoImage(file='supplier.png')
supplier_button=Button(leftFrame,image=supplier_icon,compound=LEFT,text='  تامین کنندگان',font=('Yekan',15,'bold'))
supplier_button.pack(fill=X)


category_icon=PhotoImage(file='category.png')
category_button=Button(leftFrame,image=category_icon,compound=LEFT,text='       دسته بندی ',font=('Yekan',15,'bold'))
category_button.pack(fill=X)

products_icon=PhotoImage(file='products.png')
products_button=Button(leftFrame,image=products_icon,compound=LEFT,text='         محصولات ',font=('Yekan',15,'bold'))
products_button.pack(fill=X)

sale_icon=PhotoImage(file='sale.png')
sale_button=Button(leftFrame,image=sale_icon,compound=LEFT,text='          تخفیفات',font=('Yekan',15,'bold'))
sale_button.pack(fill=X)

exit_icon=PhotoImage(file='exit.png')
exit_button=Button(leftFrame,image=exit_icon,compound=LEFT,text='             خروج',font=('Yekan',15,'bold'))
exit_button.pack(fill=X)




window.mainloop()

