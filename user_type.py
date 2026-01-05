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
                writer.writerow(
                    [
                        "شناسه",
                        "نام نوع",
                        "کارمندان",
                        "شیفت",
                        "کاربری",
                        "تامین‌کننده",
                        "دسته‌بندی",
                        "محصولات",
                        "فاکتور",
                        "تاریخچه فاکتور",
                    ]
                )
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
            title="انتخاب فایل CSV برای وارد کردن",
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

            for idx, row in enumerate(reader, start=2):  # start=2 چون سطر 1 هدر است
                if len(row) < 11:
                    skipped_count += 1
                    errors.append(
                        f"سطر {idx}: تعداد ستون‌ها ناکافی است (نیاز به 12 ستون)"
                    )
                    continue

                try:
                    # خواندن داده‌ها از ردیف CSV
                    type_name = row[1].strip()

                    # چک کردن وجود نوع کاربری
                    cursor.execute(
                        "SELECT * FROM user_types WHERE type_name=%s", (type_name,)
                    )
                    if cursor.fetchone():
                        skipped_count += 1
                        errors.append(
                            f"سطر {idx}: نوع کاربری '{type_name}' از قبل وجود دارد"
                        )
                        continue

                    # تبدیل ✅/❌ به 1/0 برای دیتابیس
                    permissions = []
                    for i in range(2, 11):  # از ستون 2 تا 10 (دسترسی‌ها)
                        if row[i] == "✅":
                            permissions.append(1)
                        else:
                            permissions.append(0)

                    # اضافه کردن نوع کاربری
                    # ✅ درست شده:
                    cursor.execute(
                        """
                        INSERT INTO user_types 
                        (type_name, can_employees, can_shifts, can_user_types, 
                         can_suppliers, can_categories, can_products,
                         can_invoices, can_invoice_history)  # 9 ستون
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)  # 9 پارامتر
                        """,
                        (type_name, *permissions),  # permissions باید 8 آیتم باشد
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
            result_message += (
                f"\n{len(errors)} خطا رخ داده است (اولین 5 خطا نمایش داده شد)"
            )

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
            can_invoices BOOLEAN DEFAULT 0,  # ✅ مستقیماً بعد از can_products
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
             can_categories, can_products, can_invoices, can_invoice_history, is_admin)  # ✅
            VALUES ('ادمین', 1, 1, 1, 1, 1, 1, 1, 1, 1)
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
                   can_invoices, can_invoice_history
            FROM user_types 
            ORDER BY id ASC
            """
        )
        records = cursor.fetchall()

        treeview.delete(*treeview.get_children())

        # شمارنده برای نمایش ردیف
        row_number = 1

        for record in records:
            # نمایش شماره ردیف به جای ID
            display_record = [row_number]  # شماره ردیف

            # اضافه کردن نام نوع
            display_record.append(record[1])  # type_name

            # تبدیل 0/1 به ❌/✅ (فقط 8 دسترسی، نه is_admin)
            for i in range(2, len(record)):  # فقط دسترسی‌ها (بدون is_admin)
                display_record.append("✅" if record[i] == 1 else "❌")

            # ذخیره ID واقعی در tags
            treeview.insert("", END, values=display_record, tags=(record[0],))
            row_number += 1

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
             can_categories, can_products, can_invoices, can_invoice_history)  # ✅
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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

        # دریافت اطلاعات فعلی
        cursor.execute(
            """
            SELECT type_name, 
                   can_employees, can_shifts, can_user_types,
                   can_suppliers, can_categories, can_products,
                   can_invoices, can_invoice_history  # ✅
            FROM user_types WHERE id = %s
            """,
            (selected_id,),
        )
        current_data = cursor.fetchone()

        if not current_data:
            messagebox.showerror("خطا", "نوع کاربری یافت نشد")
            return

        # بررسی تغییرات
        current_permissions = list(current_data[1:])
        permissions_list = list(permissions)

        # اگر هیچ تغییری ایجاد نشده باشد
        if current_data[0] == type_name and current_permissions == permissions_list:
            messagebox.showerror("خطا", "تغییراتی ایجاد نشده است")
            return

        # به‌روزرسانی
        cursor.execute(
            """
            UPDATE user_types 
            SET type_name = %s, 
                can_employees = %s, can_shifts = %s, can_user_types = %s,
                can_suppliers = %s, can_categories = %s, can_products = %s,
                can_invoices = %s, can_invoice_history = %s
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


def delete_user_type(
    selected_id,
    treeview,
    type_name_entry=None,
    permission_vars=None,
    selected_id_var=None,
):
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

        # بارگذاری مجدد داده‌ها
        load_user_types(treeview)

        # پاک کردن فیلدهای ورودی اگر پارامترها داده شده باشند
        if type_name_entry and permission_vars and selected_id_var:
            clear_fields(type_name_entry, permission_vars, selected_id_var, treeview)

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
                   can_invoices, can_invoice_history
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
    user_type_frame.place(x=0, y=100)

    # ایجاد اسکرول‌بار عمودی برای کل فرم
    canvas = Canvas(user_type_frame, bg="white", highlightthickness=0)
    scrollbar = Scrollbar(user_type_frame, orient="vertical", command=canvas.yview)

    # فریم اصلی که روی کانواس قرار می‌گیرد
    main_frame = Frame(canvas, bg="white")

    # تنظیم اسکرول‌بار
    main_frame.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # موقعیت‌دهی کانواس و اسکرول‌بار
    canvas.place(x=0, y=0, relwidth=1, relheight=1)
    scrollbar.place(x=window.winfo_width() - 200 - 17, y=0, relheight=1)

    # تنظیم اندازه کانواس هنگام تغییر اندازه پنجره
    def configure_canvas(event):
        canvas.itemconfig(canvas_window, width=event.width)

    canvas.bind("<Configure>", configure_canvas)

    heading_label = Label(
        main_frame,
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
            main_frame,
            image=back_image,
            bd=0,
            cursor="hand2",
            bg="white",
            command=lambda: user_type_frame.place_forget(),
        )
        back_button.place(x=10, y=45)
    except:
        back_button = Button(
            main_frame,
            text="← بازگشت",
            font=("fonts/Persian-Yekan.ttf", 12),
            bg="#00198f",
            fg="white",
            bd=0,
            cursor="hand2",
            command=lambda: user_type_frame.place_forget(),
        )
        back_button.place(x=10, y=45)

    # ============ سمت چپ: جدول ============
    table_frame = Frame(main_frame, bg="white", bd=1, relief=SOLID)
    table_frame.place(x=20, y=80, width=650, height=420)

    # عنوان برای جدول
    Label(
        table_frame,
        text="لیست انواع کاربری",
        font=("fonts/Persian-Yekan.ttf", 14, "bold"),
        bg="white",
        fg="#00198f",
    ).pack(pady=(10, 5))

    # Treeview با scrollbar
    tree_container = Frame(table_frame, bg="white")
    tree_container.pack(fill=BOTH, expand=True, padx=10, pady=5)

    scroll_y = Scrollbar(tree_container, orient=VERTICAL)
    scroll_x = Scrollbar(tree_container, orient=HORIZONTAL)

    # ستون‌های treeview
    treeview = ttk.Treeview(
        tree_container,
        columns=(
            "id",
            "name",
            "emp",
            "shift",
            "user_type",
            "sup",
            "cat",
            "prod",
            "inv",
            "inv_history",
        ),
        show="headings",
        yscrollcommand=scroll_y.set,
        xscrollcommand=scroll_x.set,
        height=10,
    )

    # تنظیم هدرها
    headers = [
        "شناسه",
        "نام نوع",
        "کارمندان",
        "شیفت",
        "کاربری",
        "تامین‌کننده",
        "دسته‌بندی",
        "محصولات",
        "فاکتور",
        "تاریخچه فاکتور",
    ]

    column_widths = [
        40,
        120,
        140,
        150,
        165,
        170,
        180,
        185,
        190,  # برای "فاکتور"
        195,  # برای "تاریخچه فاکتور"
    ]

    for i, (header, width) in enumerate(zip(headers, column_widths)):
        treeview.heading(f"#{i + 1}", text=header)
        treeview.column(f"#{i + 1}", width=width, anchor="center")

    scroll_y.config(command=treeview.yview)
    scroll_x.config(command=treeview.xview)

    treeview.grid(row=0, column=0, sticky="nsew")
    scroll_y.grid(row=0, column=1, sticky="ns")
    scroll_x.grid(row=1, column=0, sticky="ew", columnspan=2)

    tree_container.grid_rowconfigure(0, weight=1)
    tree_container.grid_columnconfigure(0, weight=1)

    # ============ سمت راست: فرم ورودی مطابق تصویر ============
    window_width = window.winfo_width()
    form_frame_width = window_width - 200 - 690

    form_frame = Frame(main_frame, bg="white", bd=1, relief=SOLID)
    form_frame.place(x=690, y=80, width=form_frame_width - 20, height=420)

    # عنوان برای فرم
    Label(
        form_frame,
        text="فرم مدیریت نوع کاربری",
        font=("fonts/Persian-Yekan.ttf", 14, "bold"),
        bg="white",
        fg="#00198f",
    ).pack(pady=(10, 5))

    # فریم داخلی برای المان‌های فرم
    inner_form = Frame(form_frame, bg="white")
    inner_form.pack(fill=BOTH, expand=True, padx=15, pady=10)

    # ============ ردیف 1: دکمه‌های CSV در بالای فرم با فاصله بیشتر ============
    csv_frame = Frame(inner_form, bg="white")
    csv_frame.pack(fill=X, pady=(0, 15))

    # فاصله‌دهنده در وسط برای ایجاد فاصله بیشتر بین دکمه‌ها
    spacer_frame = Frame(csv_frame, bg="white", width=30)
    spacer_frame.pack(side=LEFT, expand=True, fill=X)

    # دکمه اکسپورت CSV (سمت چپ)
    export_button = Button(
        csv_frame,
        text="📊 خروجی CSV",
        font=("fonts/Persian-Yekan.ttf", 11),
        width=12,  # عرض کمتر برای فاصله بیشتر
        height=1,
        fg="white",
        bg="#4b39e9",
        command=lambda: export_to_csv(treeview),
    )
    export_button.pack(side=LEFT, padx=(0, 5))

    # دکمه ایمپورت CSV (سمت راست)
    import_button = Button(
        csv_frame,
        text="📥 وارد کردن CSV",
        font=("fonts/Persian-Yekan.ttf", 11),
        width=12,  # عرض کمتر برای فاصله بیشتر
        height=1,
        fg="white",
        bg="#4b39e9",
        command=lambda: import_from_csv(treeview),
    )
    import_button.pack(side=LEFT, padx=(5, 0))

    # فاصله‌دهنده دیگر
    spacer_frame2 = Frame(csv_frame, bg="white", width=30)
    spacer_frame2.pack(side=LEFT, expand=True, fill=X)

    # ============ ردیف 2: نام نوع کاربری ============
    name_frame = Frame(inner_form, bg="white")
    name_frame.pack(fill=X, pady=(0, 15))

    # لیبل نام نوع کاربری (سمت راست)
    Label(
        name_frame,
        text="نام نوع کاربری",
        font=("fonts/Persian-Yekan.ttf", 11, "bold"),
        bg="white",
    ).pack(side=RIGHT, padx=(10, 0))

    # Entry نام نوع کاربری (سمت چپ)
    type_name_entry = Entry(
        name_frame,
        font=("fonts/Persian-Yekan.ttf", 11),
        bg="lightblue",
        width=25,
    )
    type_name_entry.pack(side=LEFT, fill=X, expand=True)

    # ============ ردیف 3: دسترسی‌ها ============
    # ایجاد فریم برای لیبل دسترسی‌ها و چک‌باکس‌ها
    permissions_main_frame = Frame(inner_form, bg="white")
    permissions_main_frame.pack(fill=BOTH, expand=True, pady=(0, 10))

    # لیبل "دسترسی‌ها" در سمت راست بالای چک‌باکس‌ها
    Label(
        permissions_main_frame,
        text="دسترسی‌ها",
        font=("fonts/Persian-Yekan.ttf", 11, "bold"),
        bg="white",
    ).pack(anchor=E, pady=(0, 5), padx=(0, 10))

    # فریم برای چک‌باکس‌های دسترسی‌ها در دو ستون
    permissions_frame = Frame(permissions_main_frame, bg="white", bd=1, relief=SOLID)
    permissions_frame.pack(fill=BOTH, expand=True)

    # لیست دسترسی‌ها
    permission_labels = [
        ("کارمندان", "can_employees"),
        ("تعریف شیفت", "can_shifts"),
        ("تعریف کاربری", "can_user_types"),
        ("تامین کنندگان", "can_suppliers"),
        ("دسته بندی", "can_categories"),
        ("محصولات", "can_products"),
        ("صدور فاکتور", "can_invoices"),
        ("تاریخچه فاکتور", "can_invoice_history"),
    ]

    checkboxes = []
    permission_vars = []

    # تقسیم لیست به دو قسمت برای نمایش در دو ستون
    middle_index = len(permission_labels) // 2
    if len(permission_labels) % 2:
        middle_index += 1

    left_labels = permission_labels[:middle_index]
    right_labels = permission_labels[middle_index:]

    # ایجاد فریم برای دو ستون
    left_column = Frame(permissions_frame, bg="white")
    left_column.pack(side=LEFT, fill=BOTH, expand=True, padx=(10, 5))

    right_column = Frame(permissions_frame, bg="white")
    right_column.pack(side=RIGHT, fill=BOTH, expand=True, padx=(5, 10))

    # ایجاد چک‌باکس‌ها در ستون سمت چپ
    for i, (label, _) in enumerate(left_labels):
        var = IntVar(value=0)
        permission_vars.append(var)

        # فریم برای هر چک‌باکس
        cb_frame = Frame(left_column, bg="white")
        cb_frame.pack(fill=X, pady=2)

        # چک‌باکس با متن راست‌چین
        cb = Checkbutton(
            cb_frame,
            text=label,
            variable=var,
            font=("fonts/Persian-Yekan.ttf", 10),
            bg="white",
            anchor="e",
            justify="right",
        )
        cb.pack(side=RIGHT, fill=X, expand=True)

        checkboxes.append((cb, var))

    # ایجاد چک‌باکس‌ها در ستون سمت راست
    for i, (label, _) in enumerate(right_labels):
        var = IntVar(value=0)
        permission_vars.append(var)

        # فریم برای هر چک‌باکس
        cb_frame = Frame(right_column, bg="white")
        cb_frame.pack(fill=X, pady=2)

        # چک‌باکس با متن راست‌چین
        cb = Checkbutton(
            cb_frame,
            text=label,
            variable=var,
            font=("fonts/Persian-Yekan.ttf", 10),
            bg="white",
            anchor="e",
            justify="right",
        )
        cb.pack(side=RIGHT, fill=X, expand=True)

        checkboxes.append((cb, var))

    # تنظیم ارتفاع فریم دسترسی‌ها
    permissions_frame.config(height=120)

    # ============ ردیف 4: دکمه‌های عملیات ============
    button_frame = Frame(inner_form, bg="white")
    button_frame.pack(fill=X, pady=(10, 0))

    # متغیر برای ذخیره ID انتخاب شده
    selected_id_var = StringVar()

    # ردیف اول دکمه‌ها
    row1_frame = Frame(button_frame, bg="white")
    row1_frame.pack(pady=(0, 5))

    # دکمه افزودن
    add_button = Button(
        row1_frame,
        text="افزودن",
        font=("fonts/Persian-Yekan.ttf", 11),
        bg="#00198f",
        fg="white",
        width=10,
        height=1,
        command=lambda: add_user_type(
            type_name_entry.get(), [var.get() for var in permission_vars], treeview
        ),
    )
    add_button.pack(side=LEFT, padx=3)

    # فاصله بین دکمه‌ها
    Label(row1_frame, text="", width=3, bg="white").pack(side=LEFT)

    # دکمه ویرایش
    update_button = Button(
        row1_frame,
        text="ویرایش",
        font=("fonts/Persian-Yekan.ttf", 11),
        bg="#00198f",
        fg="white",
        width=10,
        height=1,
        command=lambda: update_user_type(
            selected_id_var.get(),
            type_name_entry.get(),
            [var.get() for var in permission_vars],
            treeview,
        ),
    )
    update_button.pack(side=LEFT, padx=3)

    # ردیف دوم دکمه‌ها
    row2_frame = Frame(button_frame, bg="white")
    row2_frame.pack()

    # دکمه حذف
    delete_button = Button(
        row2_frame,
        text="حذف",
        font=("fonts/Persian-Yekan.ttf", 11),
        bg="#00198f",
        fg="white",
        width=10,
        height=1,
        command=lambda: delete_user_type(
            selected_id_var.get(),
            treeview,
            type_name_entry,
            permission_vars,
            selected_id_var,
        ),
    )
    delete_button.pack(side=LEFT, padx=3)

    # فاصله بین دکمه‌ها
    Label(row2_frame, text="", width=3, bg="white").pack(side=LEFT)

    # دکمه پاک کردن
    clear_button = Button(
        row2_frame,
        text="پاک کردن",
        font=("fonts/Persian-Yekan.ttf", 11),
        bg="#00198f",
        fg="white",
        width=10,
        height=1,
        command=lambda: clear_fields(
            type_name_entry, permission_vars, selected_id_var, treeview
        ),
    )
    clear_button.pack(side=LEFT, padx=3)

    # ================= میانبرهای صفحه انواع کاربری =================

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

    def focus_name_shortcut(event=None):
        type_name_entry.focus_set()

    def close_form(event=None):
        user_type_frame.place_forget()

        # ================= Bind کلیدهای میانبر =================

    window.bind("<Control-a>", add_shortcut)
    window.bind("<Control-u>", update_shortcut)
    window.bind("<Control-d>", delete_shortcut)
    window.bind("<Control-c>", clear_shortcut)

    window.bind("<Control-i>", import_shortcut)
    window.bind("<Control-e>", export_shortcut)

    window.bind("<Control-f>", focus_name_shortcut)
    window.bind("<Escape>", close_form)

    # تنظیم ارتفاع اصلی فرم برای امکان اسکرول
    main_frame.config(height=530)

    # ============ مدیریت انتخاب ردیف ============
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
    # مرتب کردن چک‌باکس‌ها بر اساس ترتیب ظاهری
    ordered_checkboxes = []
    for i in range(len(left_labels)):
        if i < len(left_labels):
            ordered_checkboxes.append(checkboxes[i])
        if i < len(right_labels):
            ordered_checkboxes.append(checkboxes[middle_index + i])

    if ordered_checkboxes:
        type_name_entry.bind("<Tab>", lambda e: move_focus(ordered_checkboxes[0][0]))

        for i in range(len(ordered_checkboxes) - 1):
            ordered_checkboxes[i][0].bind(
                "<Tab>", lambda e, idx=i: move_focus(ordered_checkboxes[idx + 1][0])
            )

        ordered_checkboxes[-1][0].bind("<Tab>", lambda e: move_focus(add_button))

    add_button.bind("<Tab>", lambda e: move_focus(update_button))
    update_button.bind("<Tab>", lambda e: move_focus(delete_button))
    delete_button.bind("<Tab>", lambda e: move_focus(clear_button))
    clear_button.bind("<Tab>", lambda e: move_focus(import_button))
    import_button.bind("<Tab>", lambda e: move_focus(export_button))
    export_button.bind("<Tab>", lambda e: move_focus(treeview))
    treeview.bind("<Tab>", lambda e: move_focus(type_name_entry))

    type_name_entry.focus_set()

    return user_type_frame
