from tkinter import *
from tkinter import ttk, messagebox
from tkinter import filedialog
from database import connect_database
import csv


def move_focus(widget):
    widget.focus_set()
    return "break"


def export_to_csv(treeview):
    """تابع برای ذخیره داده‌های انواع کاربری در فایل CSV"""
    try:
        items = treeview.get_children()
        data = []

        for item in items:
            values = treeview.item(item)["values"]
            data.append(values)

        if not data:
            messagebox.showwarning("هشدار", "هیچ داده‌ای برای ذخیره‌سازی وجود ندارد")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="ذخیره فایل CSV",
        )

        if file_path:
            with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow([
                    "شناسه", "نام نوع", "کارمندان", "شیفت", "کاربری", 
                    "تامین‌کننده", "دسته‌بندی", "محصولات", "فروش", 
                    "فاکتور", "تاریخچه فاکتور", "ادمین"
                ])
                writer.writerows(data)

            messagebox.showinfo(
                "موفقیت", f"داده‌ها با موفقیت در\n{file_path}\nذخیره شدند"
            )

    except Exception as e:
        messagebox.showerror("خطا", f"خطا در ذخیره‌سازی: {str(e)}")


def import_from_csv(treeview):
    """تابع برای وارد کردن داده‌ها از فایل CSV به دیتابیس انواع کاربری"""
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
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            next(reader)  # رد کردن هدر
            
            for idx, row in enumerate(reader, start=2):  # start=2 چون سطر 1 هدر است
                if len(row) < 12:
                    skipped_count += 1
                    errors.append(f"سطر {idx}: تعداد ستون‌ها ناکافی است (نیاز به 12 ستون)")
                    continue
                    
                try:
                    # خواندن داده‌ها از ردیف CSV
                    type_name = row[1].strip()
                    
                    # چک کردن وجود نوع کاربری
                    cursor.execute("SELECT * FROM user_types WHERE type_name=%s", (type_name,))
                    if cursor.fetchone():
                        skipped_count += 1
                        errors.append(f"سطر {idx}: نوع کاربری '{type_name}' از قبل وجود دارد")
                        continue
                    
                    # تبدیل ✅/❌ به 1/0 برای دیتابیس
                    permissions = []
                    for i in range(2, 11):  # از ستون 2 تا 10 (دسترسی‌ها)
                        if row[i] == "✅":
                            permissions.append(1)
                        else:
                            permissions.append(0)
                    
                    # اضافه کردن نوع کاربری
                    cursor.execute(
                        """
                        INSERT INTO user_types 
                        (type_name, can_employees, can_shifts, can_user_types, 
                         can_suppliers, can_categories, can_products,
                         can_sales, can_invoices, can_invoice_history)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (type_name, *permissions)
                    )
                    imported_count += 1
                    
                except Exception as e:
                    skipped_count += 1
                    errors.append(f"سطر {idx}: خطای عمومی - {str(e)}")
        
        connection.commit()
        
        # نمایش نتایج
        result_message = f"عملیات وارد کردن تکمیل شد:\n\n"
        result_message += f"تعداد وارد شده: {imported_count}\n"
        result_message += f"تعداد رد شده: {skipped_count}\n"
        
        if errors and len(errors) <= 5:  # نمایش حداکثر 5 خطا
            result_message += "\nخطاها:\n"
            for error in errors[:5]:
                result_message += f"• {error}\n"
        elif errors:
            result_message += f"\n{len(errors)} خطا رخ داده است (اولین 5 خطا نمایش داده شد)"
        
        messagebox.showinfo("عملیات وارد کردن", result_message)
        
        # تازه‌سازی داده‌ها
        load_user_types(treeview)
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        messagebox.showerror("خطا", f"خطا در وارد کردن فایل: {str(e)}")


def create_user_types_table():
    """ایجاد جدول انواع کاربری"""
    cursor, connection = connect_database()
    if not cursor or not connection:
        return False

    try:
        cursor.execute("USE inventory_system")
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS user_types (
            id INT AUTO_INCREMENT PRIMARY KEY,
            type_name VARCHAR(100) UNIQUE NOT NULL,
            can_employees BOOLEAN DEFAULT 0,
            can_shifts BOOLEAN DEFAULT 0,
            can_user_types BOOLEAN DEFAULT 0,
            can_suppliers BOOLEAN DEFAULT 0,
            can_categories BOOLEAN DEFAULT 0,
            can_products BOOLEAN DEFAULT 0,
            can_sales BOOLEAN DEFAULT 0,
            can_invoices BOOLEAN DEFAULT 0,
            can_invoice_history BOOLEAN DEFAULT 0,
            is_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
        )

        # اضافه کردن نوع کاربری ادمین پیش‌فرض
        cursor.execute(
            """
            INSERT IGNORE INTO user_types 
            (type_name, can_employees, can_shifts, can_user_types, can_suppliers, 
             can_categories, can_products, can_sales, can_invoices, can_invoice_history, is_admin)
            VALUES ('ادمین', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
        """
        )

        connection.commit()
        return True
    except Exception as e:
        print(f"خطا در ایجاد جدول user_types: {e}")
        return False
    finally:
        cursor.close()
        connection.close()


def load_user_types(treeview):
    """بارگذاری انواع کاربری در جدول"""
    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute("USE inventory_system")
        cursor.execute(
            """
            SELECT id, type_name, 
                   can_employees, can_shifts, can_user_types,
                   can_suppliers, can_categories, can_products,
                   can_sales, can_invoices, can_invoice_history, is_admin
            FROM user_types 
            ORDER BY is_admin DESC, type_name
        """
        )
        records = cursor.fetchall()

        treeview.delete(*treeview.get_children())
        for record in records:
            # نمایش حالت فارسی برای دسترسی‌ها
            display_record = list(record[:2])  # id و type_name

            # تبدیل 0/1 به ❌/✅
            for i in range(2, len(record)):  # همه دسترسی‌ها شامل is_admin
                display_record.append("✅" if record[i] == 1 else "❌")

            treeview.insert("", END, values=display_record, tags=(record[0],))

    except Exception as e:
        messagebox.showerror("خطا", f"خطا در بارگذاری انواع کاربری: {e}")
    finally:
        cursor.close()
        connection.close()


def get_user_types_for_combobox():
    """دریافت لیست انواع کاربری برای کامبوباکس"""
    cursor, connection = connect_database()
    if not cursor or not connection:
        return []

    try:
        cursor.execute("USE inventory_system")
        cursor.execute("SELECT type_name FROM user_types ORDER BY type_name")
        types = cursor.fetchall()
        return [type[0] for type in types]
    except:
        return []
    finally:
        cursor.close()
        connection.close()


def add_user_type(type_name, permissions, treeview):
    """اضافه کردن نوع کاربری جدید"""
    if not type_name.strip():
        messagebox.showerror("خطا", "نام نوع کاربری را وارد کنید")
        return

    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute("USE inventory_system")

        # بررسی تکراری نبودن
        cursor.execute("SELECT * FROM user_types WHERE type_name = %s", (type_name,))
        if cursor.fetchone():
            messagebox.showerror("خطا", "این نوع کاربری قبلاً وجود دارد")
            return

        # اضافه کردن رکورد جدید
        cursor.execute(
            """
            INSERT INTO user_types 
            (type_name, can_employees, can_shifts, can_user_types, can_suppliers,
             can_categories, can_products, can_sales, can_invoices, can_invoice_history)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (type_name, *permissions),
        )

        connection.commit()
        messagebox.showinfo("موفقیت", "نوع کاربری با موفقیت اضافه شد")
        load_user_types(treeview)

    except Exception as e:
        messagebox.showerror("خطا", f"خطا در اضافه کردن نوع کاربری: {e}")
    finally:
        cursor.close()
        connection.close()


def update_user_type(selected_id, type_name, permissions, treeview):
    """ویرایش نوع کاربری"""
    if not selected_id:
        messagebox.showerror("خطا", "هیچ نوع کاربری انتخاب نشده است")
        return

    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute("USE inventory_system")

        # بررسی ادمین بودن (غیرقابل ویرایش)
        cursor.execute("SELECT is_admin FROM user_types WHERE id = %s", (selected_id,))
        result = cursor.fetchone()
        if result and result[0] == 1:
            messagebox.showerror("خطا", "نوع کاربری ادمین قابل ویرایش نیست")
            return

        # به‌روزرسانی
        cursor.execute(
            """
            UPDATE user_types 
            SET type_name = %s, 
                can_employees = %s, can_shifts = %s, can_user_types = %s,
                can_suppliers = %s, can_categories = %s, can_products = %s,
                can_sales = %s, can_invoices = %s, can_invoice_history = %s
            WHERE id = %s
        """,
            (type_name, *permissions, selected_id),
        )

        connection.commit()
        messagebox.showinfo("موفقیت", "نوع کاربری با موفقیت ویرایش شد")
        load_user_types(treeview)

    except Exception as e:
        messagebox.showerror("خطا", f"خطا در ویرایش نوع کاربری: {e}")
    finally:
        cursor.close()
        connection.close()


def delete_user_type(selected_id, treeview):
    """حذف نوع کاربری"""
    if not selected_id:
        messagebox.showerror("خطا", "هیچ نوع کاربری انتخاب نشده است")
        return

    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute("USE inventory_system")

        # بررسی ادمین بودن (غیرقابل حذف)
        cursor.execute("SELECT is_admin FROM user_types WHERE id = %s", (selected_id,))
        result = cursor.fetchone()
        if result and result[0] == 1:
            messagebox.showerror("خطا", "نوع کاربری ادمین قابل حذف نیست")
            return

        # بررسی اینکه آیا در کارمندان استفاده شده
        cursor.execute("SELECT type_name FROM user_types WHERE id = %s", (selected_id,))
        type_name = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COUNT(*) FROM employee_data WHERE usertype = %s", (type_name,)
        )
        employee_count = cursor.fetchone()[0]

        if employee_count > 0:
            messagebox.showerror(
                "خطا",
                f"این نوع کاربری در {employee_count} کارمند استفاده شده است. ابتدا نوع کاربری کارمندان را تغییر دهید.",
            )
            return

        # حذف
        cursor.execute("DELETE FROM user_types WHERE id = %s", (selected_id,))
        connection.commit()

        messagebox.showinfo("موفقیت", "نوع کاربری با موفقیت حذف شد")
        load_user_types(treeview)

    except Exception as e:
        messagebox.showerror("خطا", f"خطا در حذف نوع کاربری: {e}")
    finally:
        cursor.close()
        connection.close()


def select_data(event, treeview, type_name_entry, checkboxes):
    """انتخاب ردیف از جدول"""
    selected_items = treeview.selection()
    if not selected_items:
        return

    item = treeview.item(selected_items[0])
    tags = item["tags"]
    if not tags:
        return

    selected_id = tags[0]

    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute("USE inventory_system")
        cursor.execute(
            """
            SELECT type_name, 
                   can_employees, can_shifts, can_user_types,
                   can_suppliers, can_categories, can_products,
                   can_sales, can_invoices, can_invoice_history
            FROM user_types WHERE id = %s
        """,
            (selected_id,),
        )

        result = cursor.fetchone()
        if result:
            type_name_entry.delete(0, END)
            type_name_entry.insert(0, result[0])

            # تنظیم وضعیت چک‌باکس‌ها
            permissions = result[1:]
            for i, checkbox in enumerate(checkboxes):
                var = checkbox[1]  # IntVar
                var.set(1 if permissions[i] == 1 else 0)

            return selected_id

    except Exception as e:
        messagebox.showerror("خطا", f"خطا در بارگذاری اطلاعات: {e}")
    finally:
        cursor.close()
        connection.close()

    return None


def clear_fields(type_entry, vars_list, selected_var, tree):
    """پاک کردن فیلدها"""
    type_entry.delete(0, END)
    for var in vars_list:
        var.set(0)
    selected_var.set("")
    tree.selection_remove(tree.selection())
    type_entry.focus_set()


def user_type_form(window):
    """فرم مدیریت انواع کاربری"""
    create_user_types_table()  # اطمینان از ایجاد جدول

    user_type_frame = Frame(
        window,
        width=window.winfo_width() - 200,
        height=window.winfo_height(),
        bg="white",
    )
    user_type_frame.place(x=0, y=100)  # تنظیم موقعیت فرم در سمت چپ صفحه

    heading_label = Label(
        user_type_frame,
        text="تعریف انواع کاربری",
        font=("fonts/Persian-Yekan.ttf", 18, "bold"),
        bg="#00198f",
        fg="white",
    )
    heading_label.place(x=0, y=0, relwidth=1)

    # دکمه بازگشت
    try:
        back_image = PhotoImage(file="images/back_button.png")
        back_button = Button(
            user_type_frame,
            image=back_image,
            bd=0,
            cursor="hand2",
            bg="white",
            command=lambda: user_type_frame.place_forget(),
        )
        back_button.place(x=10, y=45)
    except:
        back_button = Button(
            user_type_frame,
            text="← بازگشت",
            font=("fonts/Persian-Yekan.ttf", 12),
            bg="#00198f",
            fg="white",
            bd=0,
            cursor="hand2",
            command=lambda: user_type_frame.place_forget(),
        )
        back_button.place(x=10, y=45)

    # ============ سمت چپ: فرم ورودی ============
    left_frame = Frame(user_type_frame, bg="white")
    left_frame.place(x=30, y=80, width=400, height=420)

    # فریم برای دکمه‌های ایمپورت/اکسپورت (در بالای فرم)
    import_export_frame = Frame(left_frame, bg="white")
    import_export_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="ew")

    # دکمه ایمپورت
    import_button = Button(
        import_export_frame,
        text="📥 وارد کردن CSV",
        font=("fonts/Persian-Yekan.ttf", 11),
        width=18,
        fg="white",
        bg="#4b39e9",
        command=lambda: import_from_csv(treeview),
    )
    import_button.pack(side=LEFT, padx=5)

    # دکمه اکسپورت
    export_button = Button(
        import_export_frame,
        text="📊 خروجی CSV",
        font=("fonts/Persian-Yekan.ttf", 11),
        width=18,
        fg="white",
        bg="#4b39e9",
        command=lambda: export_to_csv(treeview),
    )
    export_button.pack(side=LEFT, padx=5)

    # نام نوع کاربری
    Label(
        left_frame,
        text="نام نوع کاربری",
        font=("fonts/Persian-Yekan.ttf", 12, "bold"),
        bg="white",
    ).grid(row=1, column=0, padx=10, pady=10, sticky="w")

    type_name_entry = Entry(
        left_frame, font=("fonts/Persian-Yekan.ttf", 12), bg="lightblue", width=25
    )
    type_name_entry.grid(row=1, column=1, padx=10, pady=10)

    # دسترسی‌ها
    Label(
        left_frame,
        text="دسترسی‌ها",
        font=("fonts/Persian-Yekan.ttf", 12, "bold"),
        bg="white",
    ).grid(row=2, column=0, padx=10, pady=10, sticky="nw")

    permissions_frame = Frame(left_frame, bg="white")
    permissions_frame.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

    # لیست دسترسی‌ها در دو ستون
    permission_labels = [
        ("کارمندان", "can_employees"),
        ("تعریف شیفت", "can_shifts"),
        ("تعریف کاربری", "can_user_types"),
        ("تامین کنندگان", "can_suppliers"),
        ("دسته بندی", "can_categories"),
        ("محصولات", "can_products"),
        ("فروش", "can_sales"),
        ("صدور فاکتور", "can_invoices"),
        ("تاریخچه فاکتور", "can_invoice_history"),
    ]

    checkboxes = []
    permission_vars = []

    # ایجاد چک‌باکس‌ها در دو ستون
    for i, (label, _) in enumerate(permission_labels):
        var = IntVar(value=0)
        permission_vars.append(var)

        row = i % 5  # 5 ردیف در هر ستون
        col = i // 5  # ستون 0 یا 1

        cb = Checkbutton(
            permissions_frame,
            text=label,
            variable=var,
            font=("fonts/Persian-Yekan.ttf", 11),
            bg="white",
            anchor="w",
        )
        cb.grid(row=row, column=col, sticky="w", pady=3, padx=(10 if col == 1 else 0))
        checkboxes.append((cb, var))

    # تنظیمات گرید برای تراز کردن ستون‌ها
    permissions_frame.grid_columnconfigure(0, weight=1)
    permissions_frame.grid_columnconfigure(1, weight=1)

    # دکمه‌های عملیات
    button_frame = Frame(left_frame, bg="white")
    button_frame.grid(row=3, column=0, columnspan=2, pady=20)

    selected_id_var = StringVar()  # برای ذخیره ID انتخاب شده

    # ردیف اول - دو دکمه
    add_button = Button(
        button_frame,
        text="➕ افزودن",
        font=("fonts/Persian-Yekan.ttf", 11),
        bg="#00198f",
        fg="white",
        width=12,
        command=lambda: add_user_type(
            type_name_entry.get(), [var.get() for var in permission_vars], treeview
        ),
    )
    add_button.grid(row=0, column=0, padx=5, pady=5)

    update_button = Button(
        button_frame,
        text="✏️ ویرایش",
        font=("fonts/Persian-Yekan.ttf", 11),
        bg="#00198f",
        fg="white",
        width=12,
        command=lambda: update_user_type(
            selected_id_var.get(),
            type_name_entry.get(),
            [var.get() for var in permission_vars],
            treeview,
        ),
    )
    update_button.grid(row=0, column=1, padx=5, pady=5)

    # ردیف دوم - دو دکمه
    delete_button = Button(
        button_frame,
        text="🗑️ حذف",
        font=("fonts/Persian-Yekan.ttf", 11),
        bg="#00198f",
        fg="white",
        width=12,
        command=lambda: delete_user_type(selected_id_var.get(), treeview),
    )
    delete_button.grid(row=1, column=0, padx=5, pady=5)

    clear_button = Button(
        button_frame,
        text="🧹 پاک کردن",
        font=("fonts/Persian-Yekan.ttf", 11),
        bg="#00198f",
        fg="white",
        width=12,
        command=lambda: clear_fields(
            type_name_entry, permission_vars, selected_id_var, treeview
        ),
    )
    clear_button.grid(row=1, column=1, padx=5, pady=5)

    # ============ سمت راست: جدول ============
    right_frame = Frame(user_type_frame, bg="white")
    right_frame.place(x=480, y=80, width=650, height=420)

    # Treeview با 2 ستون اصلی
    tree_frame = Frame(right_frame, bg="white")
    tree_frame.pack(fill=BOTH, expand=True)

    scroll_y = Scrollbar(tree_frame, orient=VERTICAL)
    scroll_x = Scrollbar(tree_frame, orient=HORIZONTAL)

    # ستون‌های treeview
    treeview = ttk.Treeview(
        tree_frame,
        columns=(
            "id", "name", "emp", "shift", "user_type",
            "sup", "cat", "prod", "sale", 
            "inv", "inv_history", "admin"
        ),
        show="headings",
        yscrollcommand=scroll_y.set,
        xscrollcommand=scroll_x.set,
        height=15,
    )

    # تنظیم هدرها
    headers = [
        "شناسه", "نام نوع",
        "کارمندان", "شیفت", "کاربری",
        "تامین‌کننده", "دسته‌بندی", "محصولات",
        "فروش", "فاکتور", "تاریخچه فاکتور", "ادمین"
    ]

    column_widths = [
        60, 100,  # شناسه و نام
        80, 60, 70,  # کارمندان، شیفت، کاربری
        90, 80, 70,  # تامین‌کننده، دسته‌بندی، محصولات
        60, 70, 100,  # فروش، فاکتور، تاریخچه فاکتور
        60  # ادمین
    ]

    for i, (header, width) in enumerate(zip(headers, column_widths)):
        treeview.heading(f"#{i + 1}", text=header)
        treeview.column(f"#{i + 1}", width=width, anchor="center")

    scroll_y.config(command=treeview.yview)
    scroll_x.config(command=treeview.xview)

    treeview.grid(row=0, column=0, sticky="nsew")
    scroll_y.grid(row=0, column=1, sticky="ns")
    scroll_x.grid(row=1, column=0, sticky="ew", columnspan=2)

    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)

    # مدیریت انتخاب ردیف
    def on_select(event):
        selected_id = select_data(event, treeview, type_name_entry, checkboxes)
        if selected_id:
            selected_id_var.set(selected_id)

    treeview.bind("<<TreeviewSelect>>", on_select)

    # بارگذاری اولیه داده‌ها
    load_user_types(treeview)

    # تنظیم فوکوس
    type_name_entry.focus_set()

    # تنظیمات Tab Order
    type_name_entry.bind("<Tab>", lambda e: move_focus(checkboxes[0][0]))
    
    for i in range(len(checkboxes) - 1):
        checkboxes[i][0].bind("<Tab>", lambda e, idx=i: move_focus(checkboxes[idx + 1][0]))
    
    checkboxes[-1][0].bind("<Tab>", lambda e: move_focus(add_button))
    add_button.bind("<Tab>", lambda e: move_focus(update_button))
    update_button.bind("<Tab>", lambda e: move_focus(delete_button))
    delete_button.bind("<Tab>", lambda e: move_focus(clear_button))
    clear_button.bind("<Tab>", lambda e: move_focus(import_button))
    import_button.bind("<Tab>", lambda e: move_focus(export_button))
    export_button.bind("<Tab>", lambda e: move_focus(treeview))
    treeview.bind("<Tab>", lambda e: move_focus(type_name_entry))

    return user_type_frame