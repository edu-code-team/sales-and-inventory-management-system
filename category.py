from tkinter import *
from tkinter import  ttk
from tkinter import messagebox
from employees import connect_database

def clear(id_entry,category_name_entry,description_text): 
    id_entry.delete(0,END)
    category_name_entry.delete(0,END)
    description_text.delete(1.0,END)






def treeview_data(treeview):
    cursor,connection=connect_database()
    if not cursor or not connection:
        return
    try:
       cursor.execute('USE inventory_system')
       cursor.execute('Select * from category_data')
       records=cursor.fetchall()
       treeview.delete(*treeview.get_children())
       for record in records:
           treeview.insert('',END,values=record)
    except Exception as e:
               messagebox.showerror('خطا',f'خطا به دلیل {e}')
    finally:
        cursor.close()
        connection.close()



def add_category(id,name,description,treeview):
    if id=='' or name=='' or description=='':
        messagebox.showerror('خطا','پر کردن تمام فیلدها الزامیست')
    else:
          cursor,connection=connect_database()
          if not cursor or not connection:
            return
          try:
             cursor.execute('Use inventory_system')
             cursor.execute('CREATE TABLE IF NOT EXISTS category_data (id INT PRIMARY KEY,name VARCHAR(100), description TEXT)')

             cursor.execute('Select * from category_data WHERE id=%s',id)
             if cursor.fetchone():
                 messagebox.showerror('خطا','شماره محصول تکراری است')
                 return
             cursor.execute('INSERT INTO category_data VALUES(%s,%s,%s)', (id, name, description))
             connection.commit()
             messagebox.showinfo('اطلاعات',' با موفقیت وارد شد')
             treeview_data(treeview)

          except Exception as e:
             messagebox.showerror('خطا',f'خطا به دلیل {e}')
    
          finally:
              cursor.close()
              connection.close()   
 


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
    details_frame.place(x=670,y=70)

    id_label=Label(details_frame,text='شماره ',font=('fonts/Persian-Yekan.ttf', 14, 'bold'), bg='white')
    id_label.grid(row=0,column=0,padx=20,sticky='w')
    id_entry=Entry(details_frame,font=('fonts/Persian-Yekan.ttf', 16, 'bold'), bg='lightblue')
    id_entry.grid(row=0,column=1)

    
    category_name_label=Label(details_frame,text='نام دسته بندی',font=('fonts/Persian-Yekan.ttf', 14, 'bold'), bg='white')
    category_name_label.grid(row=1,column=0,padx=20,sticky='w')
    category_name_entry=Entry(details_frame,font=('fonts/Persian-Yekan.ttf', 16, 'bold'), bg='lightblue')
    category_name_entry.grid(row=1,column=1, pady=20)

    description_label=Label(details_frame,text='توضیحات',font=('fonts/Persian-Yekan.ttf', 14, 'bold'), bg='white')
    description_label.grid(row=2,column=0,padx=20,sticky='nw')

    description_text=Text(details_frame,width=25,height=6,bd=2,bg='lightblue')
    description_text.grid(row=2,column=1)

    button_frame=Frame(category_frame,bg='white')
    button_frame.place(x=690,y=280)

    add_button = Button(button_frame, text='افزودن', font=('fonts/Persian-Yekan.ttf', 12), width=8, fg='white',
                         bg='#00198f',command=lambda :add_category(id_entry.get(),category_name_entry.get(),description_text.get(1.0,END).strip(),treeview))
    add_button.grid(row=0, column=0, padx=20)

    delete_button= Button(button_frame, text='حذف', font=('fonts/Persian-Yekan.ttf', 12), width=8, fg='white',
                         bg='#00198f')
    delete_button.grid(row=0, column=1, padx=20)

    clear_button= Button(button_frame, text='پاک کردن', font=('fonts/Persian-Yekan.ttf', 12), width=8, fg='white',
                         bg='#00198f',command=lambda :clear(id_entry,category_name_entry,description_text))
    clear_button.grid(row=0, column=2, padx=20)

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

    treeview.heading('id',text='شماره ')
    treeview.heading('name',text='نام دسته بندی ')
    treeview.heading('description',text='توضیحات')

    treeview.column('id',width=80)
    treeview.column('name',width=140)
    treeview.column('description',width=300)
    treeview_data(treeview)

    