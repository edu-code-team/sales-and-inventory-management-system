from tkinter import *
from tkinter import ttk
from tkinter import messagebox

def add_product(category,supplier,name,price,quantity,status):
    if category=='خالی':
         messagebox.showerror('خطا','لطفا دسته بندی را اضافه کنید')
    elif supplier=='خالی': 
         messagebox.showerror('خطا','لطفا تامین کننده را اضافه کنید')
         
def product_form(window):
    global back_image

    product_frame = Frame(window, width=1165, height=567, bg='white')
    product_frame.place(x=200, y=100)

    back_image = PhotoImage(file='images/back_button.png')
    back_button = Button(product_frame, image=back_image, bd=0, cursor='hand2', bg='white',
                         command=lambda: product_frame.place_forget())
    back_button.place(x=10, y=0)

    left_frame = Frame(product_frame, bg='white', bd=2, relief=RIDGE)
    left_frame.place(x=20, y=40)

    heading_label = Label(left_frame, text='مدیریت جزییات محصولات',
                          font=('fonts/Persian-Yekan.ttf', 16, 'bold'),
                          bg='#00198f', fg='white')
    heading_label.grid(row=0, columnspan=2, sticky='we')

    # ----- دسته‌بندی -----
    Label(left_frame, text='دسته‌بندی:', font=('fonts/Persian-Yekan.ttf', 14, 'bold'), bg='white')\
        .grid(row=1, column=0, padx=20, sticky='w')
    category_combobox = ttk.Combobox(left_frame, font=('fonts/Persian-Yekan.ttf', 14),
                                     width=18, state='readonly')
    category_combobox.grid(row=1, column=1, pady=15)
    category_combobox.set('خالی')

    # ----- تأمین‌کننده -----
    Label(left_frame, text='تأمین‌کننده:', font=('fonts/Persian-Yekan.ttf', 14, 'bold'), bg='white')\
        .grid(row=2, column=0, padx=20, sticky='w')
    supplier_combobox = ttk.Combobox(left_frame, font=('fonts/Persian-Yekan.ttf', 14),
                                     width=18, state='readonly')
    supplier_combobox.grid(row=2, column=1, pady=15)
    supplier_combobox.set('خالی')

    # ----- نام -----
    Label(left_frame, text='نام:', font=('fonts/Persian-Yekan.ttf', 14, 'bold'), bg='white')\
        .grid(row=3, column=0, padx=20, sticky='w')
    name_entry = Entry(left_frame, font=('fonts/Persian-Yekan.ttf', 16, 'bold'), bg='lightblue')
    name_entry.grid(row=3, column=1, pady=15)

    # ----- قیمت -----
    Label(left_frame, text='قیمت:', font=('fonts/Persian-Yekan.ttf', 14, 'bold'), bg='white')\
        .grid(row=4, column=0, padx=20, sticky='w')
    price_entry = Entry(left_frame, font=('fonts/Persian-Yekan.ttf', 16, 'bold'), bg='lightblue')
    price_entry.grid(row=4, column=1, pady=15)

    # ----- مقدار -----
    Label(left_frame, text='مقدار:', font=('fonts/Persian-Yekan.ttf', 14, 'bold'), bg='white')\
        .grid(row=5, column=0, padx=20, sticky='w')
    quantity_entry = Entry(left_frame, font=('fonts/Persian-Yekan.ttf', 16, 'bold'), bg='lightblue')
    quantity_entry.grid(row=5, column=1, pady=15)

    # ----- وضعیت -----
    Label(left_frame, text='وضعیت:', font=('fonts/Persian-Yekan.ttf', 14, 'bold'), bg='white')\
        .grid(row=6, column=0, padx=20, sticky='w')
    status_combobox = ttk.Combobox(left_frame, values=('فعال', 'غیرفعال'),
                                   font=('fonts/Persian-Yekan.ttf', 14),
                                   width=18, state='readonly')
    status_combobox.grid(row=6, column=1, pady=15)
    status_combobox.set('یک مورد را انتخاب کنید')

    # ===== کلیدها =====
    button_frame = Frame(left_frame, bg='white')
    button_frame.grid(row=7, columnspan=2, pady=20)

    add_button = Button(button_frame, text='افزودن', font=('fonts/Persian-Yekan.ttf', 12), width=8,
                        fg='white', bg='#00198f',
                        command=lambda: add_product(
                            category_combobox.get(),
                            supplier_combobox.get(),
                            name_entry.get(),
                            price_entry.get(),
                            quantity_entry.get(),
                            status_combobox.get()
                        ))
    add_button.grid(row=0, column=0, padx=10)

    update_button = Button(button_frame, text='بروزرسانی', font=('fonts/Persian-Yekan.ttf', 12),
                           width=8, fg='white', bg='#00198f')
    update_button.grid(row=0, column=1, padx=10)

    delete_button = Button(button_frame, text='حذف', font=('fonts/Persian-Yekan.ttf', 12),
                           width=8, fg='white', bg='#00198f')
    delete_button.grid(row=0, column=2, padx=10)

    clear_button = Button(button_frame, text='پاک کردن', font=('fonts/Persian-Yekan.ttf', 12),
                           width=8, fg='white', bg='#00198f')
    clear_button.grid(row=0, column=3, padx=10)

    # ------------------------ جستجو ------------------------
    search_frame = LabelFrame(product_frame, text='جستجو بر اساس',
                              font=('fonts/Persian-Yekan.ttf', 12), bg='white')
    search_frame.place(x=480, y=40)

    search_combobox = ttk.Combobox(search_frame,
                                   values=('دسته‌بندی', 'تأمین‌کننده', 'نام', 'وضعیت'),
                                   state='readonly', width=16,
                                   font=('fonts/Persian-Yekan.ttf', 12))
    search_combobox.grid(row=0, column=0, padx=10)
    search_combobox.set('جستجو بر اساس')

    search_entry = Entry(search_frame, font=('fonts/Persian-Yekan.ttf', 16, 'bold'),
                         bg='lightblue', width=16)
    search_entry.grid(row=0, column=1)

    Button(search_frame, text='جستجو', font=('fonts/Persian-Yekan.ttf', 12),
           width=8, fg='white', bg='#00198f').grid(row=0, column=2, padx=(10, 0), pady=10)

    Button(search_frame, text='نمایش همه', font=('fonts/Persian-Yekan.ttf', 12),
           width=8, fg='white', bg='#00198f').grid(row=0, column=3, padx=10)

    # ------------------------ TreeView ------------------------
    treeview_frame = Frame(product_frame)
    treeview_frame.place(x=480, y=125, width=570, height=430)

    scrolly = Scrollbar(treeview_frame, orient=VERTICAL)
    scrollx = Scrollbar(treeview_frame, orient=HORIZONTAL)

    treeview = ttk.Treeview(
        treeview_frame,
        columns=('category', 'supplier', 'name', 'price', 'quantity', 'state'),
        show='headings',
        yscrollcommand=scrolly.set,
        xscrollcommand=scrollx.set
    )

    scrolly.pack(side=RIGHT, fill=Y)
    scrollx.pack(side=BOTTOM, fill=X)
    scrollx.config(command=treeview.xview)
    scrolly.config(command=treeview.yview)
    treeview.pack(fill=BOTH, expand=1)

    treeview.heading('category', text='دسته‌بندی')
    treeview.heading('supplier', text='تأمین‌کننده')
    treeview.heading('name', text='نام')
    treeview.heading('price', text='قیمت')
    treeview.heading('quantity', text='مقدار')
    treeview.heading('state', text='وضعیت')

    # ست کردن عرض ستون‌ها
    treeview.column('category', width=100)
    treeview.column('supplier', width=120)
    treeview.column('name', width=120)
    treeview.column('price', width=80)
    treeview.column('quantity', width=80)
    treeview.column('state', width=80)

    # ------------------------ حرکت با Enter ------------------------
    def focus_next(event, widget):
        widget.focus()

    category_combobox.bind("<Return>", lambda e: focus_next(e, supplier_combobox))
    supplier_combobox.bind("<Return>", lambda e: focus_next(e, name_entry))
    name_entry.bind("<Return>", lambda e: focus_next(e, price_entry))
    price_entry.bind("<Return>", lambda e: focus_next(e, quantity_entry))
    quantity_entry.bind("<Return>", lambda e: focus_next(e, status_combobox))
    status_combobox.bind("<Return>", lambda e: focus_next(e, add_button))

    add_button.bind("<Return>", lambda e: add_button.invoke())
