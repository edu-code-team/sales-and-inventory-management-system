from tkinter import * 
from tkinter import ttk

def supplier_form(window):
     global back_image
     supplier_frame = Frame(window, width=1165, height=567, bg='white') 
     supplier_frame.place(x=200, y=100)
     heading_label = Label(supplier_frame, text='مدیریت تامین کنندگان', font=('fonts/Persian-Yekan.ttf', 16, 'bold'),
                          bg='#00198f', fg='white')
     heading_label.place(x=0, y=0, relwidth=1)
     back_image = PhotoImage(file='images/back_button.png')

     back_button = Button(supplier_frame, image=back_image, bd=0, cursor='hand2', bg='white',
                         command=lambda: supplier_frame.place_forget())
     back_button.place(x=10, y=30)

     left_frame=Frame(supplier_frame)
     left_frame.place(x=10,y=100)

     invoice_lable=Label(left_frame,text='شماره فاکتور',font=('fonts/Persian-Yekan.ttf', 14, 'bold'), bg='white')
     invoice_lable.grid(row=0,column=0,padx=(20,40),sticky='w')
     invoice_entry=Entry(left_frame,font=('fonts/Persian-Yekan.ttf', 16, 'bold'), bg='lightblue')
     invoice_entry.grid(row=0,column=1)

     name_lable=Label(left_frame,text='نام تامین کننده',font=('fonts/Persian-Yekan.ttf', 14, 'bold') , bg='white')
     name_lable.grid(row=1,column=0,padx=(20,40),pady=25,sticky='w')
     name_entry=Entry(left_frame,font=('fonts/Persian-Yekan.ttf', 16, 'bold'), bg='lightblue')
     name_entry.grid(row=1,column=1)

     contact_lable=Label(left_frame,text='شماره تماس',font=('fonts/Persian-Yekan.ttf', 14, 'bold') , bg='white')
     contact_lable.grid(row=2,column=0,padx=(20,40),sticky='w')
     contact_entry=Entry(left_frame,font=('fonts/Persian-Yekan.ttf', 16, 'bold'), bg='lightblue')
     contact_entry.grid(row=2,column=1)

     description_lable=Label(left_frame,text='توضیحات',font=('fonts/Persian-Yekan.ttf', 14, 'bold') , bg='white')
     description_lable.grid(row=3,column=0,padx=(20,40),sticky='nw',pady=25)
     description_text=Text(left_frame,width=20,height=6,bd=2,bg='lightblue')
     description_text.grid(row=3,column=1,pady=25)

     button_frame=Frame(left_frame)
     button_frame.grid(row=4,columnspan=2,pady=20)

     add_button = Button(button_frame, text='افزودن', font=('fonts/Persian-Yekan.ttf', 12), width=8, fg='white',
                           bg='#00198f')
     add_button.grid(row=0, column=0, padx=20)


     update_button = Button(button_frame, text='به روزرسانی', font=('fonts/Persian-Yekan.ttf', 12), width=8, fg='white',
                           bg='#00198f')
     update_button.grid(row=0, column=1)

     delete_button = Button(button_frame, text='حذف', font=('fonts/Persian-Yekan.ttf', 12), width=8, fg='white',
                           bg='#00198f')
     delete_button.grid(row=0, column=2, padx=20)

     clear_button = Button(button_frame, text='پاک کردن', font=('fonts/Persian-Yekan.ttf', 12), width=8, fg='white',
                           bg='#00198f')
     clear_button.grid(row=0, column=3)

     right_frame=Frame(supplier_frame)
     right_frame.place(x=565,y=115)

     search_frame=Frame(right_frame,bg='white')
     search_frame.pack()

     num_lable=Label(search_frame,text='شماره فاکتور',font=('fonts/Persian-Yekan.ttf', 14, 'bold'), bg='white')
     num_lable.grid(row=0,column=0,padx=10,sticky='w')
     search_entry=Entry(search_frame,font=('fonts/Persian-Yekan.ttf', 16, 'bold'), bg='lightblue',width=12)
     search_entry.grid(row=0,column=1)

     right_frame=Frame(supplier_frame,bg='white')
     right_frame.place(x=520,y=95,width=500,height=350)

     search_frame=Frame(right_frame,bg='white')
     search_frame.pack(pady=(0,10))

     num_lable=Label(search_frame,text='شماره فاکتور',font=('fonts/Persian-Yekan.ttf', 14, 'bold'), bg='white')
     num_lable.grid(row=0,column=0,padx=(0,15),sticky='w')

     search_entry=Entry(search_frame,font=('fonts/Persian-Yekan.ttf', 16, 'bold'), bg='lightblue',width=12)
     search_entry.grid(row=0,column=1)

     search_button = Button(search_frame, text='جستجو', font=('fonts/Persian-Yekan.ttf', 12), width=8, fg='white',cursor='hand2',
                           bg='#00198f')
     search_button.grid(row=0, column=2,padx=15)

     show_button = Button(search_frame, text='نمایش همه', font=('fonts/Persian-Yekan.ttf', 12), width=8, fg='white',cursor='hand2',
                           bg='#00198f')
     show_button.grid(row=0, column=3)

     scrolly=Scrollbar(right_frame,orient=VERTICAL)
     scrollx=Scrollbar(right_frame,orient=HORIZONTAL)
     treeview=ttk.Treeview(right_frame,column=('Invoice','name','contact','description'),show='headings',
                           yscrollcommand=scrolly.set,xscrollcommand=scrollx.set)
     scrolly.pack(side=RIGHT,fill=Y)
     scrollx.pack(side=BOTTOM,fill=X)
     scrollx.config(command=treeview.xview)
     scrolly.config(command=treeview.yview)
     treeview.pack(fill=BOTH,expand=1)
     treeview.heading('Invoice',text='شماره فاکتور')
     treeview.heading('name',text='نام تامین کننده')
     treeview.heading('contact',text='شماره تماس')
     treeview.heading('description',text='توضیحات')

     treeview.column('invoice',width=80)
     treeview.column('name',width=160)
     treeview.column('contact',width=120)
     treeview.column('description',width=300)
