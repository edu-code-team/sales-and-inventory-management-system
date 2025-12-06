from tkinter import *
from tkinter import  ttk
def category_form(window):
    global back_image,logo
    category_frame = Frame(window, width=1165, height=567, bg='white')
    category_frame.place(x=200, y=100)

    heading_label = Label(category_frame, text='مدیریت دسته بندی محصولات', font=('fonts/Persian-Yekan.ttf', 18, 'bold'),
                          bg='#00198f', fg='white')
    heading_label.place(x=0, y=0, relwidth=1)

    back_image = PhotoImage(file='images/back_button.png')

    back_button = Button(category_frame, image=back_image, bd=0, cursor='hand2', bg='white',
                         command=lambda: category_frame.place_forget())
    back_button.place(x=10, y=45)

    logo=PhotoImage(file='images/category_product.png')
    label=Label(category_frame,image=logo,bg='white')
    label.place(x=30,y=100)

    details_frame=Frame(category_frame,bg='white')
    details_frame.place(x=620,y=70)

    id_label=Label(details_frame,text='شماره محصول',font=('fonts/Persian-Yekan.ttf', 14, 'bold'), bg='white')
    id_label.grid(row=0,column=0,padx=20,sticky='w')
    id_entry=Entry(details_frame,font=('fonts/Persian-Yekan.ttf', 16, 'bold'), bg='lightblue')
    id_entry.grid(row=0,column=1)

    
    category_name_label=Label(details_frame,text='نام محصول',font=('fonts/Persian-Yekan.ttf', 14, 'bold'), bg='white')
    category_name_label.grid(row=1,column=0,padx=20,sticky='w')
    category_name_label_entry=Entry(details_frame,font=('fonts/Persian-Yekan.ttf', 16, 'bold'), bg='lightblue')
    category_name_label_entry.grid(row=1,column=1, pady=20)

    description_label=Label(details_frame,text='توضیحات',font=('fonts/Persian-Yekan.ttf', 14, 'bold'), bg='white')
    description_label.grid(row=2,column=0,padx=20,sticky='nw')

    description_text=Text(details_frame,width=25,height=6,bd=2,bg='lightblue')
    description_text.grid(row=2,column=1)

    button_frame=Frame(category_frame,bg='white')
    button_frame.place(x=760,y=280)

    add_button = Button(button_frame, text='افزودن', font=('fonts/Persian-Yekan.ttf', 12), width=8, fg='white',
                         bg='#00198f')
    add_button.grid(row=0, column=0, padx=20)

    delete_button= Button(button_frame, text='حذف', font=('fonts/Persian-Yekan.ttf', 12), width=8, fg='white',
                         bg='#00198f')
    delete_button.grid(row=0, column=1, padx=20)

    treeview_frame=Frame(category_frame,bg='#00198f')
    treeview_frame.place(x=530,y=340,height=200, width=500)


    scrolly=Scrollbar(treeview_frame,orient=VERTICAL)
    scrollx=Scrollbar(treeview_frame,orient=HORIZONTAL)


    treeview = ttk.Treeview(treeview_frame,column=('id', 'name', 'description'), show='headings',
                             yscrollcommand=scrolly.set,xscrollcommand=scrollx.set)
    scrolly.pack(side=RIGHT,fill=Y)
    scrollx.pack(side=BOTTOM,fill=X)
    scrollx.config(command=treeview.xview)
    scrolly.config(command=treeview.yview)
    treeview.pack(fill=BOTH,expand=1)

    treeview.heading('id',text='شماره محصول')
    treeview.heading('name',text='نام محصول ')
    treeview.heading('description',text='توضیحات')

    treeview.column('id',width=80)
    treeview.column('name',width=140)
    treeview.column('description',width=300)

    