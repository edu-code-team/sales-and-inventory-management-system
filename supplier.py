from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from employees import connect_database


def delete_supplier(invoice,treeview):
    index= treeview.selection()
    if not index:
         messagebox.showerror('خطا','هیچ ردیفی انتخاب نشده است')
         return
    cursor,connection=connect_database()
    if not cursor or not connection:
         return
    try:
       cursor.execute('use inventory_system')
       cursor.execute(' DELETE FROM supplier_data WHERE invoice=%s',invoice)
       connection.commit()
       treeview_data(treeview)
       messagebox.showinfo('اطلاعات','ردیف انتخاب شده حذف شد')
    except Exception as e:
        messagebox.showerror('خطا',f'خطا به دلیل {e}')
    finally:
        cursor.close()
        connection.close()
     

def clear(invoice_entry,name_entry,contact_entry,description_text,treeview):
    invoice_entry.delete(0,END)
    name_entry.delete(0,END)
    contact_entry.delete(0,END)
    description_text.delete(1.0,END)
    treeview.selection_remove(treeview.selection())



     


def update_supplier(invoice,name,contact,description,treeview):
    index=treeview.selection()
    if not index:
         messagebox.showerror('خطا','هیچ ردیفی انتخاب نشده است')
         return
    try:
     cursor,connection=connect_database()
     if not cursor or not connection:
         return
     cursor.execute('use inventory_system')
     cursor.execute(' SELECT * from supplier_data WHERE invoice=%s',invoice)
     current_data=cursor.fetchone()
     current_data=current_data[1:]
    
     new_data=(name,contact,description)
    

     if current_data==new_data:
        messagebox.showinfo('اطلاعات','ابتدا تغییرات را اعمال کنید')
        return

     cursor.execute(' UPDATE supplier_data SET name=%s,contact=%s,description=%s WHERE invoice=%s',(name,contact,description,invoice))
     connection.commit()
     messagebox.showinfo('اطلاعات','اطلاعات به روز رسانی شد')
     treeview_data(treeview)
    except Exception as e:
     messagebox.showerror('خطا',f'خطا به دلیل {e}')
    finally:
        cursor.close()
        connection.close()


def select_data(event,invoice_entry,name_entry,contact_entry,description_text,treeview):
    index=treeview.selection()
    content=treeview.item(index)
    actual_content=content['values']
    invoice_entry.delete(0,END)
    name_entry.delete(0,END)
    contact_entry.delete(0,END)
    description_text.delete(1.0,END)
    invoice_entry.insert(0,actual_content[0])
    name_entry.insert(0,actual_content[1])
    contact_entry.insert(0,actual_content[2])
    description_text.insert(1.0,actual_content[3])



def treeview_data(treeview):
    cursor,connection=connect_database()
    if not cursor or not connection:
        return
    try:
       cursor.execute('USE inventory_system')
       cursor.execute('Select * from supplier_data')
       records=cursor.fetchall()
       treeview.delete(*treeview.get_children())
       for record in records:
           treeview.insert('',END,values=record)
    except Exception as e:
               messagebox.showerror('خطا',f'خطا به دلیل {e}')
    finally:
        cursor.close()
        connection.close()

def add_supplier(invoice,name,contact,description,treeview):
    if invoice=='' or name=='' or contact=='' or description =='':
          messagebox.showerror('خطا','پر کردن تمام فیلدها الزامیست')
    else:
          cursor,connection=connect_database()
          if not cursor or not connection:
               return
          try:
             cursor.execute('Use inventory_system')
             cursor.execute('Select * from supplier_data where invoice=%s',invoice)
             if cursor.fetchone():
                 messagebox.showerror('خطا','شماره فاکتور تکراری است')
                 return
             cursor.execute('CREATE TABLE IF NOT EXISTS supplier_data (invoice INT PRIMARY KEY,name VARCHAR(100), contact VARCHAR(15), description TEXT)')

             cursor.execute('INSERT INTO supplier_data VALUES(%s,%s,%s,%s)', (invoice, name, contact, description))
             connection.commit()
             messagebox.showinfo('اطلاعات',' با موفقیت وارد شد')
             treeview_data(treeview)
          except Exception as e:
             messagebox.showerror('خطا',f'خطا به دلیل {e}')
          finally:
             cursor.close()
             connection.close()

def supplier_form(window):
     global back_image
     supplier_frame = Frame(window, width=1165, height=567, bg='white')
     supplier_frame.place(x=200, y=100)
     heading_label = Label(supplier_frame, text='مدیریت تامین کنندگان', font=('fonts/Persian-Yekan.ttf', 18, 'bold'),
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
                         bg='#00198f',
                         command=lambda: add_supplier(invoice_entry.get(),name_entry.get(),contact_entry.get(),
                                                      description_text.get(1.0, END).strip(),treeview))
     add_button.grid(row=0, column=0, padx=20)


     update_button = Button(button_frame, text='به روزرسانی', font=('fonts/Persian-Yekan.ttf', 12), width=8, fg='white',
                         bg='#00198f',
                         command=lambda :update_supplier(invoice_entry.get(),name_entry.get(),contact_entry.get(),
                                                        description_text.get(1.0, END).strip(),treeview))
     update_button.grid(row=0, column=1)

     delete_button = Button(button_frame, text='حذف', font=('fonts/Persian-Yekan.ttf', 12), width=8,fg='white',
                         bg='#00198f',
                         command=lambda :delete_supplier(invoice_entry.get(),treeview))
     delete_button.grid(row=0, column=2, padx=20)

     clear_button = Button(button_frame, text='پاک کردن', font=('fonts/Persian-Yekan.ttf', 12), width=8, fg='white',
                         bg='#00198f',command=lambda :clear(invoice_entry,name_entry,contact_entry,description_text,treeview))
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
                         bg='#00198f',command=lambda :search_supplier(search_entry.get(),treeview))
     search_button.grid(row=0, column=2,padx=15)

     show_button = Button(search_frame, text='نمایش همه', font=('fonts/Persian-Yekan.ttf', 12), width=8, fg='white',cursor='hand2',
                         bg='#00198f')
     show_button.grid(row=0, column=3)


     scrolly=Scrollbar(right_frame,orient=VERTICAL)
     scrollx=Scrollbar(right_frame,orient=HORIZONTAL)


     treeview = ttk.Treeview(right_frame,column=('invoice', 'name', 'contact', 'description'), show='headings',
                             yscrollcommand=scrolly.set,xscrollcommand=scrollx.set)
     scrolly.pack(side=RIGHT,fill=Y)
     scrollx.pack(side=BOTTOM,fill=X)
     scrollx.config(command=treeview.xview)
     scrolly.config(command=treeview.yview)
     treeview.pack(fill=BOTH,expand=1)
     treeview.heading('invoice',text='شماره فاکتور')
     treeview.heading('name',text='نام تامین کننده')
     treeview.heading('contact',text='شماره تماس')
     treeview.heading('description',text='توضیحات')

     treeview.column('invoice',width=80)
     treeview.column('name',width=160)
     treeview.column('contact',width=120)
     treeview.column('description',width=300)

     treeview_data(treeview)
     treeview.bind('<ButtonRelease-1>',lambda event:select_data(event,invoice_entry,name_entry,contact_entry,description_text,treeview))