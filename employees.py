from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from warnings import catch_warnings

from tkcalendar import DateEntry
import pymysql


def treeview_data():
    cursor, connection = connect_database()
    if not cursor or not connection:
        return
    cursor.execute('USE inventory_system')
    try:
        cursor.execute('select * from employee_data')
        employee_records = cursor.fetchall()
        employee_treeview.delete(*employee_treeview.get_children())
        for records in employee_records:
            employee_treeview.insert('', END, values=records)
    except Exception as e:
        messagebox.showerror('خطا', f'{e} خطای')
    finally:
        cursor.close()
        connection.close()


def connect_database():
    try:
        connection = pymysql.connect(host='localhost', user='root', passwd='')
        cursor = connection.cursor()
    except:
        messagebox.showerror('خطا', ' اتصال به پایگاه داده ناموفق. لطفا mysql را باز کنید')
        return None, None

    return cursor, connection


def create_database_table():
    cursor, connection = connect_database()
    cursor.execute('CREATE DATABASE IF NOT EXISTS inventory_system DEFAULT CHARACTER SET utf8')
    cursor.execute('USE inventory_system')
    cursor.execute('CREATE TABLE IF NOT EXISTS employee_data (empid INT PRIMARY KEY, name VARCHAR(100),'
                   'email VARCHAR(100), gender VARCHAR(50),dob VARCHAR(30), contact VARCHAR(30),'
                   'work_shift VARCHAR(50), address VARCHAR(100), usertype VARCHAR(50), password VARCHAR(50))')


def select_data(event, empid_entry,
                empname_entry, email_entry,
                gender_combobox, dob_date_entry,
                empnumber_entry, work_shift_combobox,
                address_text, user_type_combobox,
                password_entry):
    index = employee_treeview.selection()
    content = employee_treeview.item(index)
    row = content['values']
    clear_fields(empid_entry, empname_entry, email_entry, gender_combobox, dob_date_entry, empnumber_entry,
                 work_shift_combobox, address_text, user_type_combobox, password_entry, False)
    empid_entry.insert(0, row[0])
    empname_entry.insert(0, row[1])
    email_entry.insert(0, row[2])
    gender_combobox.set(row[3])
    dob_date_entry.set_date(row[4])
    empnumber_entry.insert(0, row[5])
    work_shift_combobox.set(row[6])
    address_text.insert(1.0, row[7])
    user_type_combobox.set(row[8])
    password_entry.insert(0, row[9])


def add_employee(empid, name, email, gender, dob, contact, work_shift, address, usertype, password):
    if (empid == '' or name == '' or email == '' or gender == 'جنسیت را انتخاب کنید' or dob == '' or contact == ''
            or work_shift == 'ساعت کاری را انتخاب کنید' or address == '\n' or usertype == 'نوع کاربری را انتخاب کنید'):
        messagebox.showerror('خطا', 'هیچ فیلدی نباید خالی باشد')
    else:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        cursor.execute('USE inventory_system')
        try:
            cursor.execute('SELECT * FROM employee_data WHERE empid = %s', (empid,))
            if cursor.fetchone():
                messagebox.showerror('خطا', 'شماره پرسنلی از قبل موجود می باشد')
                return
            address = address.strip()  # removes \n at the end of the address
            cursor.execute('INSERT INTO employee_data VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                           (empid, name, email, gender,
                            dob, contact, work_shift, address, usertype, password))
            connection.commit()
            treeview_data()
            messagebox.showinfo('عملیات موفق', 'اطلاعات کارمند با موفقیت ثبت شد')
        except Exception as e:
            messagebox.showerror('خطا', f'{e} خطای')
        finally:
            cursor.close()
            connection.close()


def clear_fields(empid_entry, empname_entry, email_entry, gender_combobox, dob_date_entry,
                 empnumber_entry, work_shift_combobox, address_text, user_type_combobox,
                 password_entry, check):
    empid_entry.delete(0, END)
    empname_entry.delete(0, END)
    email_entry.delete(0, END)
    gender_combobox.set('جنسیت را انتخاب کنید')
    from datetime import date
    dob_date_entry.set_date(date.today())
    empnumber_entry.delete(0, END)
    work_shift_combobox.set('ساعت کاری را انتخاب کنید')
    address_text.delete(1.0, END)
    user_type_combobox.set('نوع کاربری را انتخاب کنید')
    password_entry.delete(0, END)
    if check:
        employee_treeview.selection_remove(employee_treeview.selection())


def update_employee(empid, name, email, gender, dob, contact, work_shift, address,
                    usertype, password):
    selected = employee_treeview.selection()
    if not selected:
        messagebox.showerror('خطا', 'هیچ ردیفی برای بروزرسانی انتخاب نشده')
    else:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        try:
            cursor.execute('USE inventory_system')
            cursor.execute('SELECT * FROM employee_data WHERE empid = %s', (empid,))
            current_data = cursor.fetchone()
            current_data = current_data[1:]
            address = address.strip()
            new_data = (name, email, gender, dob, contact, work_shift, address, usertype, password)

            if current_data == new_data:
                messagebox.showinfo('توجه', 'تغییری در اطلاعات کارمند ایجاد نشده است')
                return
            cursor.execute('UPDATE employee_data SET name = %s, email = %s, gender = %s, dob = %s, contact = %s,'
                           'work_shift = %s, address = %s, usertype = %s, password = %s WHERE empid = %s',
                           (name, email, gender, dob, contact, work_shift, address, usertype, password, empid,))
            connection.commit()
            treeview_data()
            messagebox.showinfo('عملیات موفق', 'اطلاعات کارمند مدنظر با موفقیت بروزرسانی شد')
        except Exception as e:
            messagebox.showerror('خطا', f'{e} خطای')
        finally:
            cursor.close()
            connection.close()


def delete_employee(empid):
    selected = employee_treeview.selection()
    if not selected:
        messagebox.showerror('خطا', 'هیچ ردیفی برای حذف انتخاب نشده')
    else:
        result = messagebox.askyesno('تایید', 'آیا از حذف ردیف مورد نظر خود مطمئن هستید؟')
        if result:
            cursor, connection = connect_database()
            if not cursor or not connection:
                return
            try:
                cursor.execute('USE inventory_system')
                cursor.execute('DELETE FROM employee_data WHERE empid = %s', (empid,))
                connection.commit()
                treeview_data()
                messagebox.showinfo('عملیات موفق', 'اطلاعات کارمند با موفقیت حذف شذ')
            except Exception as e:
                messagebox.showerror('خطا', f'{e} خطای')
            finally:
                cursor.close()
                connection.close()


def search_employee(search_option, value):
    if search_option == 'جستجو بر اساس':
        messagebox.showerror('خطا', 'هیچ گزینه ای انتخاب نشده است')
    elif value == '':
        messagebox.showerror('خطا', 'مقداری را برای جستجو وارد کنید')
    else:
        #------------map for search columns:------------
        column_mapping = {
            'شماره پرسنلی': 'empid',
            'نام و نام خانوادگی': 'name',
            'جنسیت': 'gender',
            'تاریخ تولد': 'dob',
            'شیفت کاری': 'work_shift',
            'نوع کاربری': 'usertype'
        }
        db_column = column_mapping.get(search_option)
        #-----------------------------------------------

        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        try:
            cursor.execute('USE inventory_system')
            #-------------db_column query--------------
            query = f'SELECT * FROM employee_data WHERE {db_column} LIKE %s'
            cursor.execute(query, (f'%{value}%',))
            #------------------------------------------
            recordes = cursor.fetchall()
            employee_treeview.delete(*employee_treeview.get_children())
            for recorde in recordes:
                employee_treeview.insert('', END, values=recorde)
        except Exception as e:
            messagebox.showerror('خطا', f'{e} خطای')
        finally:
            cursor.close()
            connection.close()



def show_all(search_entry_widget, search_combobox_widget):
    treeview_data()
    search_entry_widget.delete(0, END)
    search_combobox_widget.set('جستجو بر اساس')




def employee_form(window):
    global back_image, employee_treeview
    employee_frame = Frame(window, width=1070, height=567, bg='white')
    employee_frame.place(x=200, y=100)

    heading_label = Label(employee_frame, text='مدیریت کارمندان', font=('fonts/Persian-Yekan.ttf', 16, 'bold'),
                          bg='#00198f', fg='white')
    heading_label.place(x=0, y=0, relwidth=1)

    back_image = PhotoImage(file='images/back_button.png')

    top_Frame = Frame(employee_frame)
    top_Frame.place(x=0, y=40, relwidth=1, height=235)

    back_button = Button(top_Frame, image=back_image, bd=0, cursor='hand2', bg='white',
                         command=lambda: employee_frame.place_forget())
    back_button.place(x=10, y=0)

    search_frame = Frame(top_Frame)
    search_frame.pack()
    Search_combobox = ttk.Combobox(search_frame,
                                   values=('شماره پرسنلی', 'نام و نام خانوادگی', 'جنسیت', 'تاریخ تولد', 'شیفت کاری',
                                           'نوع کاربری'), font=('fonts/Persian-Yekan.ttf', 12), state='readonly',
                                   justify='center')
    Search_combobox.set('جستجو بر اساس')
    Search_combobox.grid(row=0, column=0, padx=20)

    search_entry = Entry(search_frame, font=('fonts/Persian-Yekan.ttf', 12), bg='lightblue')
    search_entry.grid(row=0, column=1)

    search_button = Button(search_frame, text='جستجو', font=('fonts/Persian-Yekan.ttf', 12), fg='white',
                           bg='#00198f', command=lambda: show_all(search_entry, Search_combobox))
    search_button.grid(row=0, column=2, padx=20)

    show_button = Button(search_frame, text='نمایش همه', font=('fonts/Persian-Yekan.ttf', 12), width=10, cursor='hand2',
                         fg='white', bg='#00198f', command=lambda : show_all(search_entry ,Search_combobox))
    show_button.grid(row=0, column=3)

    style = ttk.Style()
    style.configure("Treeview.Heading", font=('fonts/Persian-Yekan.ttf', 12, 'bold'),
                    background='#00198f', foreground='black')
    style.configure("Treeview", font=('fonts/Persian-Yekan.ttf', 11), rowheight=25)

    horizontal_scrollbar = Scrollbar(top_Frame, orient=HORIZONTAL)
    vertical_scrollbar = Scrollbar(top_Frame, orient=VERTICAL)

    employee_treeview = ttk.Treeview(
        top_Frame,
        columns=('empid', 'empname', 'email', 'gender', 'dob', 'empnumber', 'work_shift', 'address', 'user_type'),
        show='headings',
        yscrollcommand=vertical_scrollbar.set,
        xscrollcommand=horizontal_scrollbar.set
    )

    horizontal_scrollbar.config(command=employee_treeview.xview)
    vertical_scrollbar.config(command=employee_treeview.yview)

    horizontal_scrollbar.pack(side=BOTTOM, fill=X)
    vertical_scrollbar.pack(side=RIGHT, fill=Y)
    horizontal_scrollbar.config(command=employee_treeview.xview)
    employee_treeview.pack(fill=BOTH, expand=True)

    employee_treeview.heading('empid', text='شماره پرسنلی')
    employee_treeview.heading('empname', text='نام و نام خانوادگی')
    employee_treeview.heading('email', text='ایمیل')
    employee_treeview.heading('gender', text='جنسیت')
    employee_treeview.heading('dob', text='تاریخ تولد')
    employee_treeview.heading('empnumber', text='شماره تماس')
    employee_treeview.heading('work_shift', text='شیفت کاری')
    employee_treeview.heading('address', text='آدرس')
    employee_treeview.heading('user_type', text='نوع کاربری')

    employee_treeview.column('empid', width=100)
    employee_treeview.column('empname', width=150)
    employee_treeview.column('email', width=200)
    employee_treeview.column('gender', width=50)
    employee_treeview.column('dob', width=80)
    employee_treeview.column('empnumber', width=120)
    employee_treeview.column('work_shift', width=80)
    employee_treeview.column('address', width=270)
    employee_treeview.column('user_type', width=70)

    #------------this function was moved from the last line to here------------
    create_database_table()
    #-------------------------------------------------------------------------
    treeview_data()

    detail_frame = Frame(employee_frame, bg='white')
    detail_frame.place(x=30, y=280)

    empid_label = Label(detail_frame, text='شماره پرسنلی', font=('fonts/Persian-Yekan.ttf', 12), bg='white')
    empid_label.grid(row=0, column=0, padx=20, pady=10, sticky='w')
    empid_entry = Entry(detail_frame, font=('fonts/Persian-Yekan.ttf', 12), bg='lightblue')
    empid_entry.grid(row=0, column=1, padx=20, pady=10)

    empname_label = Label(detail_frame, text='نام و نام خانوادگی', font=('fonts/Persian-Yekan.ttf', 12), bg='white')
    empname_label.grid(row=0, column=2, padx=20, pady=10)
    empname_entry = Entry(detail_frame, font=('fonts/Persian-Yekan.ttf', 12), bg='lightblue')
    empname_entry.grid(row=0, column=3, padx=20, pady=10)

    empnumber_label = Label(detail_frame, text='شماره تماس', font=('fonts/Persian-Yekan.ttf', 12), bg='white')
    empnumber_label.grid(row=0, column=4, padx=20, pady=10)
    empnumber_entry = Entry(detail_frame, font=('fonts/Persian-Yekan.ttf', 12), bg='lightblue')
    empnumber_entry.grid(row=0, column=5, padx=20, pady=10)

    gender_label = Label(detail_frame, text='جنسیت', font=('fonts/Persian-Yekan.ttf', 12), bg='white')
    gender_label.grid(row=1, column=0, padx=20, pady=10)

    gender_combobox = ttk.Combobox(detail_frame, values=('زن', 'مرد'), font=('fonts/Persian-Yekan.ttf', 12), width=18,
                                   state='readonly')
    gender_combobox.set('جنسیت را انتخاب کنید')
    gender_combobox.grid(row=1, column=1)

    dob_date_label = Label(detail_frame, text='تاریخ تولد', font=('fonts/Persian-Yekan.ttf', 12), bg='white')
    dob_date_label.grid(row=1, column=2, padx=20, pady=10)

    dob_date_entry = DateEntry(detail_frame, width=18, font=('fonts/Persian-Yekan.ttf', 12), state='readonly',
                               data_pattern='dd/mm/yyyy')
    dob_date_entry.grid(row=1, column=3)

    work_shift_label = Label(detail_frame, text='شیفت کاری', font=('fonts/Persian-Yekan.ttf', 12), bg='white')
    work_shift_label.grid(row=1, column=4, padx=20, pady=10)

    work_shift_combobox = ttk.Combobox(detail_frame, values=('تمام وقت', 'پاره وقت'),
                                       font=('fonts/Persian-Yekan.ttf', 12), width=18, state='readonly')
    work_shift_combobox.set('ساعت کاری را انتخاب کنید')
    work_shift_combobox.grid(row=1, column=5)

    email_label = Label(detail_frame, text='ایمیل', font=('fonts/Persian-Yekan.ttf', 12), bg='white')
    email_label.grid(row=3, column=0, padx=20, pady=10)
    email_entry = Entry(detail_frame, font=('fonts/Persian-Yekan.ttf', 12), bg='lightblue')
    email_entry.grid(row=3, column=1, padx=20, pady=10)

    address_label = Label(detail_frame, text='آدرس', font=('fonts/Persian-Yekan.ttf', 12), bg='white')
    address_label.grid(row=3, column=2, padx=20, pady=10)
    address_text = Text(detail_frame, width=20, height=3, font=('fonts/Persian-Yekan.ttf', 12), bg='lightblue')
    address_text.grid(row=3, column=3)

    user_type_label = Label(detail_frame, text='نوع کاربری', font=('fonts/Persian-Yekan.ttf', 12), bg='white')
    user_type_label.grid(row=3, column=4, padx=20, pady=10, sticky='w')
    user_type_combobox = ttk.Combobox(detail_frame, values=('ادمین', 'کارمند'), font=('fonts/Persian-Yekan.ttf', 12),
                                      width=18, state='readonly')
    user_type_combobox.set('نوع کاربری را انتخاب کنید')
    user_type_combobox.grid(row=3, column=5)

    password_label = Label(detail_frame, text='رمزعبور', font=('fonts/Persian-Yekan.ttf', 12), bg='white')
    password_label.grid(row=4, column=0, padx=20, pady=10, sticky='w')
    password_entry = Entry(detail_frame, font=('fonts/Persian-Yekan.ttf', 12), bg='lightblue')
    password_entry.grid(row=4, column=1, padx=20, pady=10)

    button_frame = Frame(employee_frame)
    button_frame.place(x=200, y=500)

    add_button = Button(button_frame, text='افزودن',
                        font=('fonts/Persian-Yekan.ttf', 12), fg='white', bg='#00198f',
                        command=lambda: add_employee(empid_entry.get(), empname_entry.get(), email_entry.get(),
                                                     gender_combobox.get(), dob_date_entry.get(), empnumber_entry.get(),
                                                     work_shift_combobox.get(), address_text.get(1.0, END),
                                                     user_type_combobox.get(), password_entry.get()))
    add_button.grid(row=0, column=0, padx=20)

    update_button = Button(button_frame, text='به روزرسانی', font=('fonts/Persian-Yekan.ttf', 12), fg='white',
                           bg='#00198f', command=lambda: update_employee(empid_entry.get(), empname_entry.get(),
                                                                         email_entry.get(), gender_combobox.get(),
                                                                         dob_date_entry.get(), empnumber_entry.get(),
                                                                         work_shift_combobox.get(),
                                                                         address_text.get(1.0, END),
                                                                         user_type_combobox.get(),
                                                                         password_entry.get()))
    update_button.grid(row=0, column=1, padx=20)

    delete_button = Button(button_frame, text='حذف', font=('fonts/Persian-Yekan.ttf', 12), fg='white',
                           bg='#00198f', command=lambda: delete_employee(empid_entry.get()))
    delete_button.grid(row=0, column=2, padx=20)

    clear_button = Button(button_frame, text='پاک کردن',
                          font=('fonts/Persian-Yekan.ttf', 12), fg='white', bg='#00198f',
                          command=lambda: clear_fields(empid_entry,
                                                       empname_entry, email_entry,
                                                       gender_combobox, dob_date_entry,
                                                       empnumber_entry, work_shift_combobox,
                                                       address_text, user_type_combobox,
                                                       password_entry, True))
    clear_button.grid(row=0, column=3, padx=20)
    employee_treeview.bind('<ButtonRelease-1 >', lambda event: select_data(event, empid_entry, empname_entry,
                                                                           email_entry, gender_combobox, dob_date_entry,
                                                                           empnumber_entry, work_shift_combobox,
                                                                           address_text, user_type_combobox,
                                                                           password_entry))