from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from warnings import catch_warnings

from tkcalendar import DateEntry
import pymysql


def connect_database():
    try:
        connection = pymysql.connect(host='localhost', user='root', passwd='')
        curser = connection.cursor()
    except:
        messagebox.showerror('خطا', ' اتصال به پایگاه داده ناموفق. لطفا mysql command line را باز کنید')
        return
    curser.execute('CREATE DATABASE IF NOT EXISTS inventory_system DEFAULT CHARACTER SET utf8')
    curser.execute('USE inventory_system')
    curser.execute('CREATE TABLE IF NOT EXISTS employee_data (empid INT PRIMARY KEY, name VARCHAR(100),'
                   'email VARCHAR(100), gender VARCHAR(50), dob VARCHAR(30), contact VARCHAR(30), employee_type VARCHAR(50),'
                   'work_shift VARCHAR(50), address VARCHAR(100), doj VARCHAR(30), salary VARCHAR(50), usertype VARCHAR(50),'
                   'password VARCHAR(50))')


connect_database()


def add_employee(empid, name, email, gender, dob, contact, employment_type):
    print(empid, name)


def employee_form(window):
    global back_image
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
        columns=('empid', 'empname', 'empnumber', 'gender', 'dob', 'work_shift', 'address', 'email'),
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
    employee_treeview.heading('empnumber', text='شماره تماس')
    employee_treeview.heading('gender', text='جنسیت')
    employee_treeview.heading('dob', text='تاریخ تولد')
    employee_treeview.heading('work_shift', text='شیفت کاری')
    employee_treeview.heading('address', text='آدرس')
    employee_treeview.heading('email', text='ایمیل')

    employee_treeview.column('empid', width=100)
    employee_treeview.column('empname', width=140)
    employee_treeview.column('empnumber', width=120)
    employee_treeview.column('gender', width=80)
    employee_treeview.column('email', width=180)
    employee_treeview.column('work_shift', width=200)
    employee_treeview.column('address', width=300)

    detail_frame = Frame(employee_frame, bg='white')
    detail_frame.place(x=30, y=280)

    empid_label = Label(detail_frame, text='شماره پرسنلی', font=('fonts/Persian-Yekan.ttf', 12), bg='white')
    empid_label.grid(row=0, column=0, padx=20, pady=10, sticky='w')
    empid_entry = Entry(detail_frame, font=('fonts/Persian-Yekan.ttf', 12), bg='lightblue')
    empid_entry.grid(row=0, column=1, padx=20, pady=10)

    empname_label = Label(detail_frame, text='نام و نام خانوادگی', font=('fonts/Persian-Yekan.ttf', 12), bg='white')
    empname_label.grid(row=0, column=2, padx=20, pady=10)
    empid_entry = Entry(detail_frame, font=('fonts/Persian-Yekan.ttf', 12), bg='lightblue')
    empid_entry.grid(row=0, column=3, padx=20, pady=10)

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

    button_frame = Frame(employee_frame)
    button_frame.place(x=200, y=470)

    add_button = Button(button_frame, text='افزودن',
                        font=('fonts/Persian-Yekan.ttf', 12), fg='white',bg='#00198f',
                        command=lambda: add_employee(empid_entry.get(), email_entry.get(), gender_combobox.get(),
                                                     dob_date_entry.get(), empnumber_entry.get(),
                                                     work_shift_combobox.get(), address_text.get(1.0, END)))
    add_button.grid(row=0, column=0, padx=20)

    update_button = Button(button_frame, text='به روزرسانی',
                           font=('fonts/Persian-Yekan.ttf', 12), fg='white', bg='#00198f')
    update_button.grid(row=0, column=1, padx=20)

    delete_button = Button(button_frame, text='حذف',
                           font=('fonts/Persian-Yekan.ttf', 12), fg='white', bg='#00198f')
    delete_button.grid(row=0, column=2, padx=20)

    clear_button = Button(button_frame, text='پاک کردن',
                          font=('fonts/Persian-Yekan.ttf', 12), fg='white', bg='#00198f')
    clear_button.grid(row=0, column=3, padx=20)
