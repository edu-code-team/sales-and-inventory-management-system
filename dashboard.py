from tkinter import *
from employees import employee_form
from supplier import supplier_form
from category import category_form

#GUI Part
window=Tk()

def toggle_window():
    if window.state() == "zoomed":
        window.state("normal")
    else:
        window.state("zoomed")
        Button(window, 
       text="🗕", 
       font=("Yekan", 14, "bold"),
       width=4, 
       height=1,
       bg="#00198f",
       fg="white",
       command=toggle_window
).place(x=1250, y=10)
window.config(bg='#fef9fb')

bg_image=PhotoImage(file='images/inventory.png')
titleLable=Label(window,image=bg_image,compound=LEFT,text='                               سیستم فروش و انبار داری ',
                 font=('fonts/Persian-Yekan.ttf',30,'bold'), bg='#813ffe',fg='#07070a',anchor='w',padx=20)
titleLable.place(x=0,y=0,relwidth=1)

logoButten=Button(window,text='  خروج  ',bg='#4b39e9',font=('Yekan',16,'bold'),fg='#fef9fb')
logoButten.place(x=1100,y=10)

SubtitleLabel=Label(window,text='ادمین خوش آمدید\t\t تاریخ: 01-11-2025\t\t ساعت:14:36:17',
                    font=('fonts/Persian-Yekan.ttf',15),bg='#4b39e9',fg='#fef9fb')
SubtitleLabel.place(x=0,y=70,relwidth=1)

leftFrame=Frame(window)
leftFrame.place(x=0,y=120,width=200,height=560)

LogoImage=PhotoImage(file='images/checklist-1.png')
imageLable=Label(leftFrame,image=LogoImage)
imageLable.pack()


menuLabel=Label(leftFrame,text='منو',font=('fonts/Persian-Yekan.ttf',14,'bold'),bg='#00198f',fg='#fef9fb')
menuLabel.pack(fill=X)


employee_icon=PhotoImage(file='images/employee.png')
employee_button=Button(leftFrame,image=employee_icon,compound=LEFT,text='          کارمندان',
                       font=('fonts/Persian-Yekan.ttf',15,'bold'),anchor='w', padx=10, command=lambda :employee_form(window))
employee_button.pack(fill=X)


supplier_icon=PhotoImage(file='images/supplier.png')
supplier_button=Button(leftFrame,image=supplier_icon,compound=LEFT,text='   تامین کنندگان',
                       font=('fonts/Persian-Yekan.ttf',15,'bold'),padx=10,command=lambda:supplier_form(window))
supplier_button.pack(fill=X)


category_icon=PhotoImage(file='images/category.png')
category_button=Button(leftFrame,image=category_icon,compound=LEFT,text='       دسته بندی ',
                       font=('fonts/Persian-Yekan.ttf',15,'bold'),command=lambda :category_form(window))
category_button.pack(fill=X)

products_icon=PhotoImage(file='images/products.png')
products_button=Button(leftFrame,image=products_icon,compound=LEFT,text='         محصولات ',
                       font=('fonts/Persian-Yekan.ttf',15,'bold'))
products_button.pack(fill=X)

sale_icon=PhotoImage(file='images/sale.png')
sale_button=Button(leftFrame,image=sale_icon,compound=LEFT,text='             فروش',
                   font=('fonts/Persian-Yekan.ttf',15,'bold'))
sale_button.pack(fill=X)

exit_icon=PhotoImage(file='images/exit.png')
exit_button=Button(leftFrame,image=exit_icon,compound=LEFT,text='             خروج',
                   font=('fonts/Persian-Yekan.ttf',15,'bold'))
exit_button.pack(fill=X)


emp_frame=Frame(window,bg='#00198f',bd=4,relief=RIDGE)
emp_frame.place(x=400,y=125,height=170,width=280)
totl_emp_icon=PhotoImage(file='images/total_employee.png')
totl_emp_icon_label=Label(emp_frame,image=totl_emp_icon,bg='#00198f')
totl_emp_icon_label.pack(pady=8)

totl_emp_label=Label(emp_frame,text='تعداد کارمندان',bg='#00198f',fg='#fef9fb',
                     font=('fonts/Persian-Yekan.ttf',15,'bold'))
totl_emp_label.pack()

totl_emp_count=Label(emp_frame,text='0',bg='#00198f',fg='#fef9fb',font=('fonts/Persian-Yekan.ttf',25,'bold'))
totl_emp_count.pack()




sup_frame=Frame(window,bg='#00198f',bd=4,relief=RIDGE)
sup_frame.place(x=800,y=125,height=170,width=280)
totl_sup_icon=PhotoImage(file='images/total_sup.png')
totl_sup_icon_label=Label(sup_frame,image=totl_sup_icon,bg='#00198f')
totl_sup_icon_label.pack(pady=8)

totl_sup_label=Label(sup_frame,text=' تعداد تامین کنندگان  ',bg='#00198f',fg='#fef9fb',
                     font=('fonts/Persian-Yekan.ttf',15,'bold'))
totl_sup_label.pack()

totl_sup_count=Label(sup_frame,text='0',bg='#00198f',fg='#fef9fb',font=('fonts/Persian-Yekan.ttf',25,'bold'))
totl_sup_count.pack()




category_frame=Frame(window,bg='#00198f',bd=4,relief=RIDGE)
category_frame.place(x=400,y=310,height=170,width=280)
totl_category_icon=PhotoImage(file='images/total_category.png')
totl_category_icon_label=Label(category_frame,image=totl_category_icon,bg='#00198f')
totl_category_icon_label.pack(pady=8)

totl_category_label=Label(category_frame,text=' تعداد دسته بندی ها  ',bg='#00198f',fg='#fef9fb',
                          font=('fonts/Persian-Yekan.ttf',15,'bold'))
totl_category_label.pack()

totl_category_count=Label(category_frame,text='0',bg='#00198f',fg='#fef9fb',font=('fonts/Persian-Yekan.ttf',25,'bold'))
totl_category_count.pack()


product_frame=Frame(window,bg='#00198f',bd=4,relief=RIDGE)
product_frame.place(x=800,y=310,height=170,width=280)
totl_product_icon=PhotoImage(file='images/total_product.png')
totl_product_icon_label=Label(product_frame,image=totl_product_icon,bg='#00198f')
totl_product_icon_label.pack(pady=8)

totl_product_label=Label(product_frame,text='    تعداد محصولات     ',bg='#00198f',fg='#fef9fb',
                         font=('fonts/Persian-Yekan.ttf',15,'bold'))
totl_product_label.pack()

totl_product_count=Label(product_frame,text='0',bg='#00198f',fg='#fef9fb',font=('fonts/Persian-Yekan.ttf',25,'bold'))
totl_product_count.pack()




sale_frame=Frame(window,bg='#00198f',bd=4,relief=RIDGE)
sale_frame.place(x=600,y=495,height=170,width=280)
totl_sale_icon=PhotoImage(file='images/total_sale.png')
totl_sale_icon_label=Label(sale_frame,image=totl_sale_icon,bg='#00198f')
totl_sale_icon_label.pack(pady=8)

totl_sale_label=Label(sale_frame,text=' تعداد فروش ',bg='#00198f',fg='#fef9fb',font=('fonts/Persian-Yekan.ttf',15,'bold'))
totl_sale_label.pack()

totl_sale_count=Label(sale_frame,text='0',bg='#00198f',fg='#fef9fb',font=('fonts/Persian-Yekan.ttf',25,'bold'))
totl_sale_count.pack()
window.mainloop()

