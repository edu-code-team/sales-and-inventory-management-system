# employees.py
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
import pymysql
from database import connect_database, get_shifts_from_db
from user_type import get_user_types_for_combobox
from tkinter import filedialog
import csv

# ================= تابع فیلتر چند ملاکه جدید =================
def multi_filter_employees(treeview, empid_filter, name_filter, gender_filter, usertype_filter, shift_filter):
    cursor, connection = connect_database()
    if not cursor or not connection:
        return
    
    try:
        cursor.execute("USE inventory_system")
        
        # ساخت شرط‌های پویا
        conditions = []
        params = []
        
        if empid_filter and empid_filter != "همه":
            conditions.append("empid = %s")
            params.append(empid_filter)
        
        if name_filter and name_filter != "همه":
            conditions.append("name = %s")
            params.append(name_filter)
        
        if gender_filter != "همه":
            conditions.append("gender = %s")
            params.append(gender_filter)
        
        if usertype_filter != "همه":
            conditions.append("usertype = %s")
            params.append(usertype_filter)
        
        if shift_filter != "همه":
            conditions.append("work_shift = %s")
            params.append(shift_filter)
        
        # ساختن کوئری نهایی
        if conditions:
            query = "SELECT * FROM employee_data WHERE " + " AND ".join(conditions)
        else:
            query = "SELECT * FROM employee_data"
        
        cursor.execute(query, tuple(params))
        records = cursor.fetchall()
        
        treeview.delete(*treeview.get_children())
        
        if not records:
            messagebox.showinfo("نتیجه", "هیچ رکوردی با این فیلترها یافت نشد")
            return
            
        for record in records:
            treeview.insert("", END, values=record)
            
    except Exception as e:
        messagebox.showerror("خطا", f"خطا در فیلتر کردن: {str(e)}")
    finally:
        cursor.close()
        connection.close()

# ================= تابع برای دریافت نام‌های کارمندان از دیتابیس =================
def get_employee_names_from_db():
    cursor, connection = connect_database()
    if not cursor or not connection:
        return ["همه"]
    
    try:
        cursor.execute("USE inventory_system")
        cursor.execute("SELECT DISTINCT name FROM employee_data ORDER BY name")
        names = cursor.fetchall()
        name_list = ["همه"]
        for name in names:
            if name[0]:  # اطمینان از خالی نبودن
                name_list.append(name[0])
        return name_list
    except Exception as e:
        print(f"خطا در دریافت نام‌ها: {e}")
        return ["همه"]
    finally:
        cursor.close()
        connection.close()

# ================= تابع برای دریافت شماره‌های پرسنلی از دیتابیس =================
def get_employee_ids_from_db():
    cursor, connection = connect_database()
    if not cursor or not connection:
        return ["همه"]
    
    try:
        cursor.execute("USE inventory_system")
        cursor.execute("SELECT DISTINCT empid FROM employee_data ORDER BY empid")
        ids = cursor.fetchall()
        id_list = ["همه"]
        for id in ids:
            if id[0]:  # اطمینان از خالی نبودن
                id_list.append(str(id[0]))
        return id_list
    except Exception as e:
        print(f"خطا در دریافت شماره پرسنلی‌ها: {e}")
        return ["همه"]
    finally:
        cursor.close()
        connection.close()

# ================= تابع برای دریافت انواع کاربری از دیتابیس =================
def get_all_user_types_from_db():
    cursor, connection = connect_database()
    if not cursor or not connection:
        return ["همه", "ادمین", "کاربر"]
    
    try:
        cursor.execute("USE inventory_system")
        cursor.execute("SELECT DISTINCT usertype FROM employee_data ORDER BY usertype")
        usertypes = cursor.fetchall()
        usertype_list = ["همه"]
        for usertype in usertypes:
            if usertype[0]:  # اطمینان از خالی نبودن
                usertype_list.append(usertype[0])
        return usertype_list
    except Exception as e:
        print(f"خطا در دریافت انواع کاربری: {e}")
        return ["همه", "ادمین", "کاربر"]
    finally:
        cursor.close()
        connection.close()

# ================= تابع صادر کردن CSV =================
def export_employee_to_csv(treeview):
    items = treeview.get_children()
    if not items:
        messagebox.showwarning("هشدار", "داده‌ای برای خروجی وجود ندارد")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        title="ذخیره فایل CSV"
    )
    if not file_path:
        return

    try:
        with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow([
                "شماره پرسنلی", "نام", "ایمیل", "جنسیت", "تاریخ تولد",
                "شماره تماس", "شیفت کاری", "آدرس", "نوع کاربری", "رمز عبور"
            ])
            for item in items:
                writer.writerow(treeview.item(item)["values"])

        messagebox.showinfo("موفقیت", f"داده‌ها با موفقیت در\n{file_path}\nذخیره شدند")
    except Exception as e:
        messagebox.showerror("خطا", f"خطا در ذخیره‌سازی: {str(e)}")

# ================= تابع وارد کردن CSV =================
def import_employee_from_csv(treeview):
    try:
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="انتخاب فایل CSV برای وارد کردن"
        )
        if not file_path:
            return

        cursor, connection = connect_database()
        if not cursor or not connection:
            return

        cursor.execute("USE inventory_system")
        
        imported_count = 0
        skipped_count = 0
        errors = []
        
        with open(file_path, "r", encoding="utf-8-sig") as file:
            reader = csv.reader(file)
            next(reader)  # رد کردن هدر
            
            for idx, row in enumerate(reader, start=2):
                if len(row) < 10:
                    skipped_count += 1
                    errors.append(f"سطر {idx}: تعداد ستون‌ها ناکافی است")
                    continue
                    
                try:
                    empid = row[0].strip()
                    
                    # چک کردن وجود شماره پرسنلی
                    cursor.execute("SELECT empid FROM employee_data WHERE empid=%s", (empid,))
                    if cursor.fetchone():
                        skipped_count += 1
                        errors.append(f"سطر {idx}: شماره پرسنلی '{empid}' از قبل وجود دارد")
                        continue
                    
                    # وارد کردن کارمند جدید
                    cursor.execute(
                        "INSERT INTO employee_data VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        tuple(row)
                    )
                    imported_count += 1
                    
                except ValueError as ve:
                    skipped_count += 1
                    errors.append(f"سطر {idx}: خطا در فرمت داده‌ها - {str(ve)}")
                except Exception as e:
                    skipped_count += 1
                    errors.append(f"سطر {idx}: خطای عمومی - {str(e)}")
        
        connection.commit()
        
        # نمایش نتایج
        result_message = f"عملیات وارد کردن تکمیل شد:\n\n"
        result_message += f"تعداد وارد شده: {imported_count}\n"
        result_message += f"تعداد رد شده: {skipped_count}\n"
        
        if errors and len(errors) <= 10:
            result_message += "\nخطاها:\n"
            for error in errors[:10]:
                result_message += f"• {error}\n"
        elif errors:
            result_message += f"\n{len(errors)} خطا رخ داده است (اولین 10 خطا نمایش داده شد)"
        
        messagebox.showinfo("عملیات وارد کردن", result_message)
        
        # تازه‌سازی داده‌ها
        treeview_data()
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        messagebox.showerror("خطا", f"خطا در وارد کردن فایل: {str(e)}")

# ================= توابع اصلی =================
def treeview_data():
    cursor, connection = connect_database()
    if not cursor or not connection:
        return
    cursor.execute("USE inventory_system")
    try:
        cursor.execute("select * from employee_data")
        employee_records = cursor.fetchall()
        employee_treeview.delete(*employee_treeview.get_children())
        for records in employee_records:
            employee_treeview.insert("", END, values=records)
    except Exception as e:
        messagebox.showerror("خطا", f"{e} خطای")
    finally:
        cursor.close()
        connection.close()


def create_database_table():
    cursor, connection = connect_database()
    cursor.execute(
        "CREATE DATABASE IF NOT EXISTS inventory_system DEFAULT CHARACTER SET utf8"
    )
    cursor.execute("USE inventory_system")
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS employee_data (
            empid INT PRIMARY KEY, 
            name VARCHAR(100),
            email VARCHAR(100), 
            gender VARCHAR(50),
            dob VARCHAR(30), 
            contact VARCHAR(30),
            work_shift VARCHAR(50), 
            address VARCHAR(100), 
            usertype VARCHAR(50), 
            password VARCHAR(50)
        )"""
    )
    connection.commit()
    cursor.close()
    connection.close()


def select_data(
    event,
    empid_entry,
    empname_entry,
    email_entry,
    gender_combobox,
    dob_date_entry,
    empnumber_entry,
    work_shift_combobox,
    address_text,
    user_type_combobox,
    password_entry,
):
    index = employee_treeview.selection()
    content = employee_treeview.item(index)
    row = content["values"]
    clear_fields(
        empid_entry,
        empname_entry,
        email_entry,
        gender_combobox,
        dob_date_entry,
        empnumber_entry,
        work_shift_combobox,
        address_text,
        user_type_combobox,
        password_entry,
        False,
    )
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


def add_employee(
    empid, name, email, gender, dob, contact, work_shift, address, usertype, password
):
    if (
        empid == ""
        or name == ""
        or email == ""
        or gender == "جنسیت را انتخاب کنید"
        or dob == ""
        or contact == ""
        or work_shift == "شیفت کاری را انتخاب کنید"
        or address == "\n"
        or usertype == "نوع کاربری را انتخاب کنید"
    ):
        messagebox.showerror("خطا", "هیچ فیلدی نباید خالی باشد")
    else:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        cursor.execute("USE inventory_system")
        try:
            cursor.execute("SELECT * FROM employee_data WHERE empid = %s", (empid,))
            if cursor.fetchone():
                messagebox.showerror("خطا", "شماره پرسنلی از قبل موجود می باشد")
                return
            address = address.strip()
            cursor.execute(
                "INSERT INTO employee_data VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    empid,
                    name,
                    email,
                    gender,
                    dob,
                    contact,
                    work_shift,
                    address,
                    usertype,
                    password,
                ),
            )
            connection.commit()
            treeview_data()
            messagebox.showinfo("عملیات موفق", "اطلاعات کارمند با موفقیت ثبت شد")
        except Exception as e:
            messagebox.showerror("خطا", f"{e} خطای")
        finally:
            cursor.close()
            connection.close()


def clear_fields(
    empid_entry,
    empname_entry,
    email_entry,
    gender_combobox,
    dob_date_entry,
    empnumber_entry,
    work_shift_combobox,
    address_text,
    user_type_combobox,
    password_entry,
    check,
):
    empid_entry.delete(0, END)
    empname_entry.delete(0, END)
    email_entry.delete(0, END)
    gender_combobox.set("جنسیت را انتخاب کنید")
    from datetime import date

    dob_date_entry.set_date(date.today())
    empnumber_entry.delete(0, END)
    work_shift_combobox.set("شیفت کاری را انتخاب کنید")
    address_text.delete(1.0, END)
    user_type_combobox.set("نوع کاربری را انتخاب کنید")
    password_entry.delete(0, END)
    if check:
        employee_treeview.selection_remove(employee_treeview.selection())


def update_employee(
    empid, name, email, gender, dob, contact, work_shift, address, usertype, password
):
    selected = employee_treeview.selection()
    if not selected:
        messagebox.showerror("خطا", "هیچ ردیفی برای بروزرسانی انتخاب نشده")
    else:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        try:
            cursor.execute("USE inventory_system")
            cursor.execute("SELECT * FROM employee_data WHERE empid = %s", (empid,))
            current_data = cursor.fetchone()
            current_data = current_data[1:]
            address = address.strip()
            new_data = (
                name,
                email,
                gender,
                dob,
                contact,
                work_shift,
                address,
                usertype,
                password,
            )

            if current_data == new_data:
                messagebox.showinfo("توجه", "تغییری در اطلاعات کارمند ایجاد نشده است")
                return
            cursor.execute(
                "UPDATE employee_data SET name = %s, email = %s, gender = %s, dob = %s, contact = %s,"
                "work_shift = %s, address = %s, usertype = %s, password = %s WHERE empid = %s",
                (
                    name,
                    email,
                    gender,
                    dob,
                    contact,
                    work_shift,
                    address,
                    usertype,
                    password,
                    empid,
                ),
            )
            connection.commit()
            treeview_data()
            messagebox.showinfo(
                "عملیات موفق", "اطلاعات کارمند مدنظر با موفقیت بروزرسانی شد"
            )
        except Exception as e:
            messagebox.showerror("خطا", f"{e} خطای")
        finally:
            cursor.close()
            connection.close()


def delete_employee(empid):
    selected = employee_treeview.selection()
    if not selected:
        messagebox.showerror("خطا", "هیچ ردیفی برای حذف انتخاب نشده")
    else:
        result = messagebox.askyesno(
            "تایید", "آیا از حذف ردیف مورد نظر خود مطمئن هستید؟"
        )
        if result:
            cursor, connection = connect_database()
            if not cursor or not connection:
                return
            try:
                cursor.execute("USE inventory_system")
                cursor.execute("DELETE FROM employee_data WHERE empid = %s", (empid,))
                connection.commit()
                treeview_data()
                messagebox.showinfo("عملیات موفق", "اطلاعات کارمند با موفقیت حذف شد")
            except Exception as e:
                messagebox.showerror("خطا", f"{e} خطای")
            finally:
                cursor.close()
                connection.close()

# ================= تابع move_focus برای Tab =================
def move_focus(widget):
    widget.focus_set()
    return "break"

# ================= تابع فرم کارمندان =================
def employee_form(window):

    global back_image, employee_treeview
    employee_frame = Frame(
        window,
        width=window.winfo_width() - 200,
        height=window.winfo_height(),
        bg="white",
    )
    employee_frame.place(x=0, y=100)
    
    # ================= هدر =================
    heading_label = Label(
        employee_frame,
        text="مدیریت کارمندان",
        font=("fonts/Persian-Yekan.ttf", 16, "bold"),
        bg="#00198f",
        fg="white",
    )
    heading_label.place(x=0, y=0, relwidth=1)

    back_image = PhotoImage(file="images/back_button.png")

    # ================= فریم فیلتر - بین هدر و TreeView =================
    # ارتفاع هدر 40 پیکسل است، پس فیلتر از y=40 شروع می‌شود
    # عرض فیلتر هم اندازه هدر (relwidth=1) به جز 30 پیکسل برای دکمه back
    filter_frame = Frame(employee_frame, bg="white", bd=1, relief=SOLID)
    filter_frame.place(x=30, y=40, relwidth=1, height=50)  # عرض فیکس شده با هدر
    
    # فونت فیلتر
    f_font = ("fonts/Persian-Yekan.ttf", 10)
    
    # دریافت داده‌ها از دیتابیس برای Comboboxها
    empid_list = get_employee_ids_from_db()
    name_list = get_employee_names_from_db()
    
    # شماره پرسنلی (Combobox)
    Label(filter_frame, text="شماره پرسنلی", bg="white", font=f_font).place(x=10, y=2)
    empid_filter = ttk.Combobox(
        filter_frame,
        values=empid_list,
        width=10,
        state="readonly",
        font=f_font
    )
    empid_filter.place(x=10, y=22)
    empid_filter.set("همه")
    
    # نام و نام خانوادگی (Combobox)
    Label(filter_frame, text="نام و نام خانوادگی", bg="white", font=f_font).place(x=100, y=2)
    name_filter = ttk.Combobox(
        filter_frame,
        values=name_list,
        width=12,
        state="readonly",
        font=f_font
    )
    name_filter.place(x=100, y=22)
    name_filter.set("همه")
    
    # جنسیت
    Label(filter_frame, text="جنسیت", bg="white", font=f_font).place(x=210, y=2)
    gender_filter = ttk.Combobox(
        filter_frame,
        values=["همه", "زن", "مرد"],
        width=8,
        state="readonly",
        font=f_font
    )
    gender_filter.place(x=210, y=22)
    gender_filter.set("همه")
    
    # نوع کاربری - دریافت همه انواع کاربری از دیتابیس
    Label(filter_frame, text="نوع کاربری", bg="white", font=f_font).place(x=290, y=2)
    
    # دریافت لیست انواع کاربری برای فیلتر
    usertypes_list = get_all_user_types_from_db()
    
    usertype_filter = ttk.Combobox(
        filter_frame,
        values=usertypes_list,
        width=10,
        state="readonly",
        font=f_font
    )
    usertype_filter.place(x=290, y=22)
    usertype_filter.set("همه")
    
    # شیفت کاری
    Label(filter_frame, text="شیفت کاری", bg="white", font=f_font).place(x=380, y=2)
    
    # دریافت لیست شیفت‌ها برای فیلتر
    shifts_list = get_shifts_from_db()
    shift_filter_values = ["همه"]
    if shifts_list:
        shift_filter_values.extend(shifts_list)
    
    shift_filter = ttk.Combobox(
        filter_frame,
        values=shift_filter_values,
        width=10,
        state="readonly",
        font=f_font
    )
    shift_filter.place(x=380, y=22)
    shift_filter.set("همه")
    
    # دکمه جستجو
    search_btn = Button(
        filter_frame,
        text="جستجو",
        bg="#00198f",
        fg="white",
        width=8,
        font=("fonts/Persian-Yekan.ttf", 10),
        command=lambda: multi_filter_employees(
            employee_treeview,
            empid_filter.get(),
            name_filter.get(),
            gender_filter.get(),
            usertype_filter.get(),
            shift_filter.get()
        )
    )
    search_btn.place(x=480, y=20)
    
    # دکمه نمایش همه
    show_all_btn = Button(
        filter_frame,
        text="نمایش همه",
        bg="#4b39e9",
        fg="white",
        width=8,
        font=("fonts/Persian-Yekan.ttf", 10),
        command=lambda: treeview_data()
    )
    show_all_btn.place(x=560, y=20)

    # ================= TreeView - زیر فیلتر =================
    # فریم TreeView از y=90 شروع می‌شود (40 پیکسل هدر + 50 پیکسل فیلتر)
    top_Frame = Frame(employee_frame, bg="white")
    top_Frame.place(x=0, y=90, relwidth=1, height=185)  # ارتفاع کاهش یافته

    back_button = Button(
        top_Frame,
        image=back_image,
        bd=0,
        cursor="hand2",
        bg="white",
        command=lambda: employee_frame.place_forget(),
    )
    back_button.place(x=10, y=0)

    style = ttk.Style()
    style.configure(
        "Treeview.Heading",
        font=("fonts/Persian-Yekan.ttf", 12, "bold"),
        background="#00198f",
        foreground="black",
    )
    style.configure("Treeview", font=("fonts/Persian-Yekan.ttf", 11), rowheight=25)
    horizontal_scrollbar = Scrollbar(top_Frame, orient=HORIZONTAL)
    vertical_scrollbar = Scrollbar(top_Frame, orient=VERTICAL)

    employee_treeview = ttk.Treeview(
        top_Frame,
        columns=(
            "empid",
            "empname",
            "email",
            "gender",
            "dob",
            "empnumber",
            "work_shift",
            "address",
            "user_type",
        ),
        show="headings",
        yscrollcommand=vertical_scrollbar.set,
        xscrollcommand=horizontal_scrollbar.set,
    )

    horizontal_scrollbar.config(command=employee_treeview.xview)
    vertical_scrollbar.config(command=employee_treeview.yview)

    horizontal_scrollbar.pack(side=BOTTOM, fill=X)
    vertical_scrollbar.pack(side=RIGHT, fill=Y)
    employee_treeview.pack(fill=BOTH, expand=True)

    employee_treeview.heading("empid", text="شماره پرسنلی")
    employee_treeview.heading("empname", text="نام و نام خانوادگی")
    employee_treeview.heading("email", text="ایمیل")
    employee_treeview.heading("gender", text="جنسیت")
    employee_treeview.heading("dob", text="تاریخ تولد")
    employee_treeview.heading("empnumber", text="شماره تماس")
    employee_treeview.heading("work_shift", text="شیفت کاری")
    employee_treeview.heading("address", text="آدرس")
    employee_treeview.heading("user_type", text="نوع کاربری")

    employee_treeview.column("empid", width=100)
    employee_treeview.column("empname", width=150)
    employee_treeview.column("email", width=200)
    employee_treeview.column("gender", width=50)
    employee_treeview.column("dob", width=80)
    employee_treeview.column("empnumber", width=120)
    employee_treeview.column("work_shift", width=80)
    employee_treeview.column("address", width=270)
    employee_treeview.column("user_type", width=70)

    create_database_table()
    treeview_data()

    # ================= فریم جزئیات کارمند - زیر TreeView =================
    # TreeView ارتفاع 185 پیکسل دارد و از y=90 شروع می‌شود، پس از y=275 شروع می‌کنیم
    detail_frame = Frame(employee_frame, bg="white")
    detail_frame.place(x=30, y=280)

    # تنظیم ستون‌ها برای گرید
    for i in range(7):
        detail_frame.grid_columnconfigure(i, minsize=140)

    # ================= فیلدهای ورودی =================
    empid_label = Label(
        detail_frame,
        text="شماره پرسنلی",
        font=("fonts/Persian-Yekan.ttf", 12, "bold"),
        bg="white",
    )
    empid_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
    empid_entry = Entry(
        detail_frame, font=("fonts/Persian-Yekan.ttf", 12), bg="lightblue"
    )
    empid_entry.grid(row=0, column=1, padx=20, pady=10)

    empname_label = Label(
        detail_frame,
        text="نام و نام خانوادگی",
        font=("fonts/Persian-Yekan.ttf", 12, "bold"),
        bg="white",
    )
    empname_label.grid(row=0, column=2, padx=20, pady=10)
    empname_entry = Entry(
        detail_frame, font=("fonts/Persian-Yekan.ttf", 12), bg="lightblue"
    )
    empname_entry.grid(row=0, column=3, padx=20, pady=10)

    empnumber_label = Label(
        detail_frame,
        text="شماره تماس",
        font=("fonts/Persian-Yekan.ttf", 12, "bold"),
        bg="white",
    )
    empnumber_label.grid(row=0, column=4, padx=20, pady=10,sticky="w")
    empnumber_entry = Entry(
        detail_frame, font=("fonts/Persian-Yekan.ttf", 12), bg="lightblue"
    )
    empnumber_entry.grid(row=0, column=5, padx=20, pady=10)

    gender_label = Label(
        detail_frame, text="جنسیت", font=("fonts/Persian-Yekan.ttf", 12, "bold"), bg="white"
    )
    gender_label.grid(row=1, column=0, padx=20, pady=10)

    gender_combobox = ttk.Combobox(
        detail_frame,
        values=("زن", "مرد"),
        font=("fonts/Persian-Yekan.ttf", 12),
        width=18,
        state="readonly",
    )
    gender_combobox.set("جنسیت را انتخاب کنید")
    gender_combobox.grid(row=1, column=1)

    dob_date_label = Label(
        detail_frame,
        text="تاریخ تولد",
        font=("fonts/Persian-Yekan.ttf", 12, "bold"),
        bg="white",
    )
    dob_date_label.grid(row=1, column=2, padx=20, pady=10)

    dob_date_entry = DateEntry(
        detail_frame,
        width=18,
        font=("fonts/Persian-Yekan.ttf", 12),
        state="readonly",
        data_pattern="dd/mm/yyyy",
    )
    dob_date_entry.grid(row=1, column=3)

    work_shift_label = Label(
        detail_frame,
        text="شیفت کاری",
        font=("fonts/Persian-Yekan.ttf", 12, "bold"),
        bg="white",
    )
    work_shift_label.grid(row=1, column=4, padx=20, pady=10, sticky="w")

    # دریافت لیست شیفت‌ها از database.py
    shifts_list = get_shifts_from_db()

    work_shift_combobox = ttk.Combobox(
        detail_frame, font=("fonts/Persian-Yekan.ttf", 12), width=18, state="readonly"
    )

    if shifts_list:
        work_shift_combobox["values"] = shifts_list
        work_shift_combobox.set("شیفت کاری را انتخاب کنید")
    else:
        work_shift_combobox["values"] = ["اول شیفت تعریف کنید"]
        work_shift_combobox.set("اول شیفت تعریف کنید")

    work_shift_combobox.grid(row=1, column=5, padx=20, pady=10)

    email_label = Label(
        detail_frame, text="ایمیل", font=("fonts/Persian-Yekan.ttf", 12,"bold"), bg="white"
    )
    email_label.grid(row=3, column=0, padx=20, pady=10)
    email_entry = Entry(
        detail_frame, font=("fonts/Persian-Yekan.ttf", 12), bg="lightblue"
    )
    email_entry.grid(row=3, column=1, padx=20, pady=10)

    address_label = Label(
        detail_frame, text="آدرس", font=("fonts/Persian-Yekan.ttf", 12,"bold"), bg="white"
    )
    address_label.grid(row=3, column=2, padx=20, pady=10)
    address_text = Text(
        detail_frame,
        width=20,
        height=3,
        font=("fonts/Persian-Yekan.ttf", 12),
        bg="lightblue",
    )
    address_text.grid(row=3, column=3)

    user_type_label = Label(
        detail_frame,
        text="نوع کاربری",
        font=("fonts/Persian-Yekan.ttf", 12,"bold"),
        bg="white",
    )
    user_type_label.grid(row=3, column=4, padx=20, pady=10, sticky="w")

    # دریافت لیست انواع کاربری از دیتابیس (همه انواع کاربری موجود)
    all_user_types = get_all_user_types_from_db()
    # حذف "همه" از لیست برای انتخاب نوع کاربری
    user_types_list_for_selection = [ut for ut in all_user_types if ut != "همه"]
    
    user_type_combobox = ttk.Combobox(
        detail_frame,
        values=user_types_list_for_selection,
        font=("fonts/Persian-Yekan.ttf", 12),
        width=18,
        state="readonly",
    )

    if user_types_list_for_selection:
        user_type_combobox.set("نوع کاربری را انتخاب کنید")
    else:
        user_type_combobox.set("ادمین")

    user_type_combobox.grid(row=3, column=5)

    password_label = Label(
        detail_frame, text="رمزعبور", font=("fonts/Persian-Yekan.ttf", 12,"bold"), bg="white"
    )
    password_label.grid(row=4, column=0, padx=20, pady=10, sticky="w")
    password_entry = Entry(
        detail_frame, font=("fonts/Persian-Yekan.ttf", 12), bg="lightblue"
    )
    password_entry.grid(row=4, column=1, padx=20, pady=10)

    # ================= دکمه‌های CRUD + CSV =================
    button_container = Frame(employee_frame, bg="white")
    button_container.place(relx=0.5, y=520, anchor="n")

    button_frame = Frame(button_container, bg="white")
    button_frame.pack()

    add_button = Button(
        button_frame,
        text="افزودن",
        font=("fonts/Persian-Yekan.ttf", 12),
        fg="white",
        bg="#00198f",
        width=8,
        command=lambda: add_employee(
            empid_entry.get(),
            empname_entry.get(),
            email_entry.get(),
            gender_combobox.get(),
            dob_date_entry.get(),
            empnumber_entry.get(),
            work_shift_combobox.get(),
            address_text.get(1.0, END),
            user_type_combobox.get(),
            password_entry.get(),
        ),
    )
    add_button.grid(row=0, column=0, padx=5)

    update_button = Button(
        button_frame,
        text="به روزرسانی",
        font=("fonts/Persian-Yekan.ttf", 12),
        fg="white",
        bg="#00198f",
        width=8,
        command=lambda: update_employee(
            empid_entry.get(),
            empname_entry.get(),
            email_entry.get(),
            gender_combobox.get(),
            dob_date_entry.get(),
            empnumber_entry.get(),
            work_shift_combobox.get(),
            address_text.get(1.0, END),
            user_type_combobox.get(),
            password_entry.get(),
        ),
    )
    update_button.grid(row=0, column=1, padx=5)

    delete_button = Button(
        button_frame,
        text="حذف",
        font=("fonts/Persian-Yekan.ttf", 12),
        fg="white",
        bg="#00198f",
        width=8,
        command=lambda: delete_employee(empid_entry.get()),
    )
    delete_button.grid(row=0, column=2, padx=5)

    clear_button = Button(
        button_frame,
        text="پاک کردن",
        font=("fonts/Persian-Yekan.ttf", 12),
        fg="white",
        bg="#00198f",
        width=8,
        command=lambda: clear_fields(
            empid_entry,
            empname_entry,
            email_entry,
            gender_combobox,
            dob_date_entry,
            empnumber_entry,
            work_shift_combobox,
            address_text,
            user_type_combobox,
            password_entry,
            True,
        ),
    )
    clear_button.grid(row=0, column=3, padx=5)

    # ======= دکمه‌های CSV کنار دکمه‌های اصلی =======
    import_button = Button(
        button_frame,
        text="📥 وارد کردن CSV",
        font=("fonts/Persian-Yekan.ttf", 11),
        fg="white",
        bg="#4b39e9",
        width=12,
        command=lambda: import_employee_from_csv(employee_treeview),
    )
    import_button.grid(row=0, column=4, padx=5)

    export_button = Button(
        button_frame,
        text="📤 خروجی CSV",
        font=("fonts/Persian-Yekan.ttf", 11),
        fg="white",
        bg="#4b39e9",
        width=12,
        command=lambda: export_employee_to_csv(employee_treeview),
    )
    export_button.grid(row=0, column=5, padx=5)

    # ================= اتصال رویدادها =================
    employee_treeview.bind(
        "<ButtonRelease-1>",
        lambda event: select_data(
            event,
            empid_entry,
            empname_entry,
            email_entry,
            gender_combobox,
            dob_date_entry,
            empnumber_entry,
            work_shift_combobox,
            address_text,
            user_type_combobox,
            password_entry,
        ),
    )

    # ================= میانبرهای صفحه کلید =================
    def add_shortcut(event=None):
        add_button.invoke()

    def update_shortcut(event=None):
        update_button.invoke()

    def delete_shortcut(event=None):
        delete_button.invoke()

    def clear_shortcut(event=None):
        clear_button.invoke()

    def import_shortcut(event=None):
        import_button.invoke()

    def export_shortcut(event=None):
        export_button.invoke()

    def filter_shortcut(event=None):
        empid_filter.focus_set()

    def close_form(event=None):
        employee_frame.place_forget()

    # Bind shortcuts
    window.bind("<a>", add_shortcut)
    window.bind("<A>", add_shortcut)
    window.bind("<u>", update_shortcut)
    window.bind("<U>", update_shortcut)
    window.bind("<d>", delete_shortcut)
    window.bind("<D>", delete_shortcut)
    window.bind("<c>", clear_shortcut)
    window.bind("<C>", clear_shortcut)
    window.bind("<i>", import_shortcut)
    window.bind("<I>", import_shortcut)
    window.bind("<e>", export_shortcut)
    window.bind("<E>", export_shortcut)
    window.bind("<f>", filter_shortcut)
    window.bind("<F>", filter_shortcut)
    window.bind("<Escape>", close_form)

    # ================= تنظیم فوکوس Tab =================
    # تنظیم ترتیب Tab برای فیلدهای ورودی
    empid_entry.bind("<Tab>", lambda e: move_focus(empname_entry))
    empname_entry.bind("<Tab>", lambda e: move_focus(email_entry))
    email_entry.bind("<Tab>", lambda e: move_focus(gender_combobox))
    gender_combobox.bind("<Tab>", lambda e: move_focus(dob_date_entry))
    dob_date_entry.bind("<Tab>", lambda e: move_focus(empnumber_entry))
    empnumber_entry.bind("<Tab>", lambda e: move_focus(work_shift_combobox))
    work_shift_combobox.bind("<Tab>", lambda e: move_focus(address_text))
    address_text.bind("<Tab>", lambda e: move_focus(user_type_combobox))
    user_type_combobox.bind("<Tab>", lambda e: move_focus(password_entry))
    password_entry.bind("<Tab>", lambda e: move_focus(add_button))
    
    # تنظیم ترتیب Tab برای دکمه‌ها
    add_button.bind("<Tab>", lambda e: move_focus(update_button))
    update_button.bind("<Tab>", lambda e: move_focus(delete_button))
    delete_button.bind("<Tab>", lambda e: move_focus(clear_button))
    clear_button.bind("<Tab>", lambda e: move_focus(import_button))
    import_button.bind("<Tab>", lambda e: move_focus(export_button))
    export_button.bind("<Tab>", lambda e: move_focus(empid_filter))
    
    # تنظیم ترتیب Tab برای فیلترها
    empid_filter.bind("<Tab>", lambda e: move_focus(name_filter))
    name_filter.bind("<Tab>", lambda e: move_focus(gender_filter))
    gender_filter.bind("<Tab>", lambda e: move_focus(usertype_filter))
    usertype_filter.bind("<Tab>", lambda e: move_focus(shift_filter))
    shift_filter.bind("<Tab>", lambda e: move_focus(search_btn))
    search_btn.bind("<Tab>", lambda e: move_focus(show_all_btn))
    show_all_btn.bind("<Tab>", lambda e: move_focus(employee_treeview))
    employee_treeview.bind("<Tab>", lambda e: move_focus(empid_entry))

    # تنظیم فوکوس اولیه
    empid_entry.focus_set()