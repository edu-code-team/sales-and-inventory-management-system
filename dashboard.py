from tkinter import *
from tkinter import ttk

#Functionality Part
def employee_form():
    global back_image
    employee_frame = Frame(window, width=1070, height=567, bg='white')
    employee_frame.place(x=200, y=100)

    heading_label = Label(employee_frame,text='مدیریت کارمندان',font=('fonts/Persian-Yekan.ttf', 16, 'bold'),bg='#00198f',fg='white')
    heading_label.place(x=0, y=0, relwidth=1)

    back_image = PhotoImage(file='images/back_button.png')
    back_button = Button(employee_frame,image=back_image,bd=0,cursor='hand2',bg='white', command=lambda: employee_frame.place_forget())
    back_button.place(x=10, y=30)

    top_Frame=Frame(employee_frame)
    top_Frame.place(x=0 ,y=70 , relwidth=1 , height=235)
    search_frame=Frame(top_Frame)
    search_frame.pack()
    Search_combobox = ttk.Combobox(search_frame,
                                   values=('شماره پرسنلی', 'نام و نام خانوادگی', 'شماره تماس'),
                                   font=('fonts/Persian-Yekan.ttf', 12),
                                   state='readonly', justify='center')
    Search_combobox.set('جستجو بر اساس')
    Search_combobox.grid(row=0, column=0, padx=20)

    search_entry = Entry(search_frame, font=('fonts/Persian-Yekan.ttf', 12), bg='lightblue')
    search_entry.grid(row=0, column=1)

    search_button = Button(search_frame, text='جستجو',
                           font=('fonts/Persian-Yekan.ttf', 12), fg='white', bg='#00198f')
    search_button.grid(row=0, column=2, padx=20)

    show_button = Button(search_frame, text='نمایش همه',
                         font=('fonts/Persian-Yekan.ttf', 12), width=10,
                         cursor='hand2', fg='white', bg='#00198f')
    show_button.grid(row=0, column=3)

    style = ttk.Style()
    style.configure("Treeview.Heading", font=('fonts/Persian-Yekan.ttf', 12, 'bold'),
                    background='#00198f', foreground='black')
    style.configure("Treeview", font=('fonts/Persian-Yekan.ttf', 11), rowheight=25)

    horizontal_scrollbar = Scrollbar(top_Frame, orient=HORIZONTAL)
    vertical_scrollbar = Scrollbar(top_Frame, orient=VERTICAL)

    employee_treeview = ttk.Treeview(
        top_Frame,
        columns=('empid', 'empname', 'empnumber', 'gender', 'work_shift', 'address'),
        show='headings',
        yscrollcommand=vertical_scrollbar.set,
        xscrollcommand=horizontal_scrollbar.set
    )

    horizontal_scrollbar.config(command=employee_treeview.xview)
    vertical_scrollbar.config(command=employee_treeview.yview)

    horizontal_scrollbar.pack(side=BOTTOM, fill=X)
    vertical_scrollbar.pack(side=RIGHT, fill=Y)
    employee_treeview.pack(fill=BOTH, expand=True)

    employee_treeview.heading('empid', text='شماره پرسنلی')
    employee_treeview.heading('empname', text='نام و نام خانوادگی')
    employee_treeview.heading('empnumber', text='شماره تماس')
    employee_treeview.heading('gender', text='جنسیت')
    employee_treeview.heading('work_shift', text='شیفت کاری')
    employee_treeview.heading('address', text='آدرس')

    employee_treeview.column('empid', width=100)
    employee_treeview.column('empname', width=140)
    employee_treeview.column('empnumber', width=100)
    employee_treeview.column('gender', width=80)
    employee_treeview.column('work_shift', width=200)
    employee_treeview.column('address', width=300)



#GUI Part
window=Tk()

window.title('Dashboard')
window.state('zoomed')
window.resizable(0,0)
window.config(bg='#fef9fb')

bg_image=PhotoImage(file='images/inventory.png')
titleLable=Label(window,image=bg_image,compound=LEFT,text='                               سیستم فروش و انبار داری ',font=('fonts/Persian-Yekan.ttf',30,'bold'), bg='#813ffe',fg='#07070a',anchor='w',padx=20)
titleLable.place(x=0,y=0,relwidth=1)

logoButten=Button(window,text='  خروج  ',bg='#4b39e9',font=('Yekan',16,'bold'),fg='#fef9fb')
logoButten.place(x=1100,y=10)

SubtitleLabel=Label(window,text='ادمین خوش آمدید\t\t تاریخ: 01-11-2025\t\t ساعت:14:36:17',font=('fonts/Persian-Yekan.ttf',15),bg='#4b39e9',fg='#fef9fb')
SubtitleLabel.place(x=0,y=70,relwidth=1)

leftFrame=Frame(window)
leftFrame.place(x=0,y=120,width=200,height=560)

LogoImage=PhotoImage(file='images/checklist-1.png')
imageLable=Label(leftFrame,image=LogoImage)
imageLable.pack()


menuLabel=Label(leftFrame,text='منو',font=('fonts/Persian-Yekan.ttf',14,'bold'),bg='#00198f')
menuLabel.pack(fill=X)


employee_icon=PhotoImage(file='images/employee.png')
employee_button=Button(leftFrame,image=employee_icon,compound=LEFT,text='          کارمندان',font=('fonts/Persian-Yekan.ttf',15,'bold'),anchor='w', padx=10, command=employee_form)
employee_button.pack(fill=X)


supplier_icon=PhotoImage(file='images/supplier.png')
supplier_button=Button(leftFrame,image=supplier_icon,compound=LEFT,text='   تامین کنندگان',font=('fonts/Persian-Yekan.ttf',15,'bold'))
supplier_button.pack(fill=X)


category_icon=PhotoImage(file='images/category.png')
category_button=Button(leftFrame,image=category_icon,compound=LEFT,text='       دسته بندی ',font=('fonts/Persian-Yekan.ttf',15,'bold'))
category_button.pack(fill=X)

products_icon=PhotoImage(file='images/products.png')
products_button=Button(leftFrame,image=products_icon,compound=LEFT,text='         محصولات ',font=('fonts/Persian-Yekan.ttf',15,'bold'))
products_button.pack(fill=X)

sale_icon=PhotoImage(file='images/sale.png')
sale_button=Button(leftFrame,image=sale_icon,compound=LEFT,text='             فروش',font=('fonts/Persian-Yekan.ttf',15,'bold'))
sale_button.pack(fill=X)

exit_icon=PhotoImage(file='images/exit.png')
exit_button=Button(leftFrame,image=exit_icon,compound=LEFT,text='             خروج',font=('fonts/Persian-Yekan.ttf',15,'bold'))
exit_button.pack(fill=X)


emp_frame=Frame(window,bg='#00198f',bd=4,relief=RIDGE)
emp_frame.place(x=400,y=125,height=170,width=280)
totl_emp_icon=PhotoImage(file='images/total_employee.png')
totl_emp_icon_label=Label(emp_frame,image=totl_emp_icon,bg='#00198f')
totl_emp_icon_label.pack(pady=8)

totl_emp_label=Label(emp_frame,text='تعداد کارمندان',bg='#00198f',fg='#fef9fb',font=('fonts/Persian-Yekan.ttf',15,'bold'))
totl_emp_label.pack()

totl_emp_count=Label(emp_frame,text='0',bg='#00198f',fg='#fef9fb',font=('fonts/Persian-Yekan.ttf',25,'bold'))
totl_emp_count.pack()




sup_frame=Frame(window,bg='#00198f',bd=4,relief=RIDGE)
sup_frame.place(x=800,y=125,height=170,width=280)
totl_sup_icon=PhotoImage(file='images/total_sup.png')
totl_sup_icon_label=Label(sup_frame,image=totl_sup_icon,bg='#00198f')
totl_sup_icon_label.pack(pady=8)

totl_sup_label=Label(sup_frame,text=' تعداد تامین کنندگان  ',bg='#00198f',fg='#fef9fb',font=('fonts/Persian-Yekan.ttf',15,'bold'))
totl_sup_label.pack()

totl_sup_count=Label(sup_frame,text='0',bg='#00198f',fg='#fef9fb',font=('fonts/Persian-Yekan.ttf',25,'bold'))
totl_sup_count.pack()




category_frame=Frame(window,bg='#00198f',bd=4,relief=RIDGE)
category_frame.place(x=400,y=310,height=170,width=280)
totl_category_icon=PhotoImage(file='images/total_category.png')
totl_category_icon_label=Label(category_frame,image=totl_category_icon,bg='#00198f')
totl_category_icon_label.pack(pady=8)

totl_category_label=Label(category_frame,text=' تعداد دسته بندی ها  ',bg='#00198f',fg='#fef9fb',font=('fonts/Persian-Yekan.ttf',15,'bold'))
totl_category_label.pack()

totl_category_count=Label(category_frame,text='0',bg='#00198f',fg='#fef9fb',font=('fonts/Persian-Yekan.ttf',25,'bold'))
totl_category_count.pack()


product_frame=Frame(window,bg='#00198f',bd=4,relief=RIDGE)
product_frame.place(x=800,y=310,height=170,width=280)
totl_product_icon=PhotoImage(file='images/total_product.png')
totl_product_icon_label=Label(product_frame,image=totl_product_icon,bg='#00198f')
totl_product_icon_label.pack(pady=8)

totl_product_label=Label(product_frame,text='    تعداد محصولات     ',bg='#00198f',fg='#fef9fb',font=('fonts/Persian-Yekan.ttf',15,'bold'))
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

