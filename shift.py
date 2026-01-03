from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pymysql
from database import connect_database
from tkinter import filedialog
import csv

def export_shift_to_csv(treeview):
    items = treeview.get_children()
    if not items:
        messagebox.showwarning("هشدار", "داده‌ای برای خروجی وجود ندارد")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="ذخیره فایل CSV"
    )
    if not file_path:
        return

    with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["شناسه", "نام شیفت", "ساعت شروع", "ساعت پایان"])
        for item in items:
            writer.writerow(treeview.item(item)["values"])

    messagebox.showinfo("موفقیت", "خروجی CSV با موفقیت انجام شد")

def import_shift_from_csv(treeview):
    file_path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv")],
        title="انتخاب فایل CSV"
    )
    if not file_path:
        return

    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    cursor.execute("USE inventory_system")

    imported = 0
    skipped = 0

    with open(file_path, "r", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        next(reader)  # رد کردن هدر

        for row in reader:
            if len(row) < 4:
                skipped += 1
                continue

            shift_name, start_time, end_time = row[1], row[2], row[3]

            cursor.execute(
                "SELECT shift_id FROM shift_data WHERE shift_name=%s",
                (shift_name,)
            )
            if cursor.fetchone():
                skipped += 1
                continue

            cursor.execute(
                "INSERT INTO shift_data (shift_name, start_time, end_time) VALUES (%s, %s, %s)",
                (shift_name, start_time, end_time)
            )
            imported += 1

    connection.commit()
    cursor.close()
    connection.close()

    treeview_data(treeview)

    messagebox.showinfo(
        "نتیجه",
        f"وارد شده: {imported}\nرد شده: {skipped}"
    )


def treeview_data(shift_treeview):
    """بارگذاری داده‌های شیفت در جدول"""
    cursor, connection = connect_database()
    if not cursor or not connection:
        return
    try:
        cursor.execute("USE inventory_system")
        cursor.execute(
            "SELECT shift_id, shift_name, start_time, end_time FROM shift_data ORDER BY shift_id"
        )
        shift_records = cursor.fetchall()
        shift_treeview.delete(*shift_treeview.get_children())
        for records in shift_records:
            shift_treeview.insert("", END, values=records)
    except Exception as e:
        messagebox.showerror("خطا", f"خطا در بارگذاری داده‌ها: {e}")
    finally:
        cursor.close()
        connection.close()


def connect_database():
    """اتصال به پایگاه داده"""
    try:
        connection = pymysql.connect(
            host="localhost", user="root", passwd="", charset="utf8mb4"
        )
        cursor = connection.cursor()
        return cursor, connection
    except Exception as e:
        messagebox.showerror("خطا", f"اتصال به پایگاه داده ناموفق: {e}")
        return None, None


def create_shift_table():
    """ایجاد جدول شیفت در پایگاه داده"""
    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS inventory_system DEFAULT CHARACTER SET utf8"
        )
        cursor.execute("USE inventory_system")

        # ایجاد جدول شیفت
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS shift_data (
            shift_id INT PRIMARY KEY AUTO_INCREMENT,
            shift_name VARCHAR(100) NOT NULL UNIQUE,
            start_time VARCHAR(10) NOT NULL,
            end_time VARCHAR(10) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
        )

        connection.commit()
        print("✅ جدول shift_data ایجاد شد")

    except Exception as e:
        print(f"خطا در ایجاد جدول شیفت: {e}")
    finally:
        cursor.close()
        connection.close()


def validate_time_format(time_str):
    """اعتبارسنجی فرمت زمان"""
    try:
        if len(time_str) != 5:
            return False
        hours, minutes = time_str.split(":")
        if not hours.isdigit() or not minutes.isdigit():
            return False
        if int(hours) < 0 or int(hours) > 23:
            return False
        if int(minutes) < 0 or int(minutes) > 59:
            return False
        return True
    except:
        return False


def get_shifts_for_combobox():
    """دریافت لیست شیفت‌ها برای کامبوباکس"""
    cursor, connection = connect_database()
    if not cursor or not connection:
        return []

    try:
        cursor.execute("USE inventory_system")
        cursor.execute("SELECT shift_name FROM shift_data ORDER BY shift_name")
        shifts = cursor.fetchall()
        return [shift[0] for shift in shifts]
    except:
        return []
    finally:
        cursor.close()
        connection.close()

def move_focus(widget):
    widget.focus_set()
    return "break"

def shift_form(window):
    """فرم تعریف شیفت"""

    def select_data(event):
        """انتخاب ردیف از جدول"""
        index = shift_treeview.selection()
        if not index:
            return

        content = shift_treeview.item(index)
        row = content["values"]

        # پاک کردن فیلدها
        shift_name_entry.delete(0, END)
        start_time_entry.delete(0, END)
        end_time_entry.delete(0, END)

        # پر کردن فیلدها با داده‌های انتخاب شده
        shift_name_entry.insert(0, row[1])  # shift_name
        start_time_entry.insert(0, row[2])  # start_time
        end_time_entry.insert(0, row[3])  # end_time

    def add_shift():
        """اضافه کردن شیفت جدید"""
        shift_name = shift_name_entry.get().strip()
        start_time = start_time_entry.get().strip()
        end_time = end_time_entry.get().strip()

        if not shift_name:
            messagebox.showerror("خطا", "نام شیفت را وارد کنید")
            return

        if not start_time or not end_time:
            messagebox.showerror("خطا", "ساعت شروع و پایان را وارد کنید")
            return

        # اعتبارسنجی فرمت زمان
        if not validate_time_format(start_time) or not validate_time_format(end_time):
            messagebox.showerror("خطا", "فرمت زمان باید HH:MM باشد (مثال: 08:30)")
            return

        cursor, connection = connect_database()
        if not cursor or not connection:
            return

        try:
            cursor.execute("USE inventory_system")

            # بررسی تکراری نبودن نام شیفت
            cursor.execute(
                "SELECT * FROM shift_data WHERE shift_name = %s", (shift_name,)
            )
            if cursor.fetchone():
                messagebox.showerror("خطا", "این نام شیفت قبلاً ثبت شده است")
                return

            # اضافه کردن شیفت جدید
            cursor.execute(
                "INSERT INTO shift_data (shift_name, start_time, end_time) VALUES (%s, %s, %s)",
                (shift_name, start_time, end_time),
            )
            connection.commit()

            treeview_data(shift_treeview)
            messagebox.showinfo("موفقیت", "شیفت جدید با موفقیت اضافه شد")

            # پاک کردن فیلدها بعد از اضافه کردن
            clear_fields()

        except Exception as e:
            messagebox.showerror("خطا", f"خطا در اضافه کردن شیفت: {e}")
        finally:
            cursor.close()
            connection.close()

    def update_shift():
        """به‌روزرسانی شیفت"""
        selected_item = shift_treeview.selection()
        if not selected_item:
            messagebox.showerror("خطا", "لطفاً یک شیفت را برای ویرایش انتخاب کنید")
            return

        # دریافت داده‌های انتخاب شده
        item = shift_treeview.item(selected_item[0])
        shift_id = item["values"][0]
        old_shift_name = item["values"][1]
        old_start_time = item["values"][2]
        old_end_time = item["values"][3]

        # دریافت داده‌های جدید از فیلدها
        new_shift_name = shift_name_entry.get().strip()
        new_start_time = start_time_entry.get().strip()
        new_end_time = end_time_entry.get().strip()

        if not new_shift_name or not new_start_time or not new_end_time:
            messagebox.showerror("خطا", "تمامی فیلدها باید پر شوند")
            return

        # اعتبارسنجی فرمت زمان
        if not validate_time_format(new_start_time) or not validate_time_format(
            new_end_time
        ):
            messagebox.showerror("خطا", "فرمت زمان باید HH:MM باشد (مثال: 08:30)")
            return

        # ============ رفع مشکل 1: بررسی تغییرات ============
        # چک کردن اگر هیچ تغییری ایجاد نشده باشد
        if (
            new_shift_name == old_shift_name
            and new_start_time == old_start_time
            and new_end_time == old_end_time
        ):
            messagebox.showinfo("توجه", "هیچ تغییری در اطلاعات شیفت ایجاد نشده است")
            return

        cursor, connection = connect_database()
        if not cursor or not connection:
            return

        try:
            cursor.execute("USE inventory_system")

            # بررسی تکراری نبودن نام شیفت (به جز خودش)
            if new_shift_name != old_shift_name:
                cursor.execute(
                    "SELECT * FROM shift_data WHERE shift_name = %s AND shift_id != %s",
                    (new_shift_name, shift_id),
                )
                if cursor.fetchone():
                    messagebox.showerror("خطا", "این نام شیفت قبلاً ثبت شده است")
                    return

            # به‌روزرسانی شیفت
            cursor.execute(
                "UPDATE shift_data SET shift_name = %s, start_time = %s, end_time = %s WHERE shift_id = %s",
                (new_shift_name, new_start_time, new_end_time, shift_id),
            )
            connection.commit()

            treeview_data(shift_treeview)
            messagebox.showinfo("موفقیت", "شیفت با موفقیت ویرایش شد")

            # پاک کردن فیلدها
            clear_fields()

        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ویرایش شیفت: {e}")
        finally:
            cursor.close()
            connection.close()

    def delete_shift():
        """حذف شیفت"""
        selected_item = shift_treeview.selection()
        if not selected_item:
            messagebox.showerror("خطا", "لطفاً یک شیفت را برای حذف انتخاب کنید")
            return

        # دریافت نام شیفت انتخاب شده
        item = shift_treeview.item(selected_item[0])
        shift_id = item["values"][0]
        shift_name = item["values"][1]

        # تأیید حذف
        confirm = messagebox.askyesno(
            "تأیید حذف", f'آیا از حذف شیفت "{shift_name}" مطمئن هستید؟'
        )
        if not confirm:
            return

        cursor, connection = connect_database()
        if not cursor or not connection:
            return

        try:
            cursor.execute("USE inventory_system")

            # بررسی اینکه آیا این شیفت در جدول کارمندان استفاده شده
            cursor.execute(
                "SELECT COUNT(*) FROM employee_data WHERE work_shift = %s",
                (shift_name,),
            )
            employee_count = cursor.fetchone()[0]

            if employee_count > 0:
                messagebox.showwarning(
                    "اخطار",
                    f"این شیفت در {employee_count} کارمند استفاده شده است. ابتدا شیفت کارمندان را تغییر دهید.",
                )
                return

            # ============ رفع مشکل 2: بازنشانی شناسه‌ها بعد از حذف ============
            # 1. ابتدا شیفت را حذف می‌کنیم
            cursor.execute("DELETE FROM shift_data WHERE shift_id = %s", (shift_id,))
            connection.commit()

            # 2. بازنشانی شناسه‌های خودکار (AUTO_INCREMENT)
            cursor.execute("ALTER TABLE shift_data AUTO_INCREMENT = 1")

            # 3. دریافت همه شیفت‌ها و بازسازی شناسه‌ها
            cursor.execute(
                "SELECT shift_id, shift_name, start_time, end_time FROM shift_data ORDER BY shift_id"
            )
            all_shifts = cursor.fetchall()

            # 4. حذف همه رکوردها و دوباره اضافه کردن با شناسه‌های جدید
            cursor.execute("DELETE FROM shift_data")

            # 5. اضافه کردن مجدد با شناسه‌های پشت سر هم
            for index, shift in enumerate(all_shifts, start=1):
                cursor.execute(
                    "INSERT INTO shift_data (shift_id, shift_name, start_time, end_time) VALUES (%s, %s, %s, %s)",
                    (index, shift[1], shift[2], shift[3]),
                )

            connection.commit()

            treeview_data(shift_treeview)
            messagebox.showinfo(
                "موفقیت", "شیفت با موفقیت حذف شد و شناسه‌ها بازنشانی شدند"
            )

            # پاک کردن فیلدها
            clear_fields()

        except Exception as e:
            messagebox.showerror("خطا", f"خطا در حذف شیفت: {e}")
        finally:
            cursor.close()
            connection.close()

    def clear_fields():
        """پاک کردن فیلدهای ورودی"""
        shift_name_entry.delete(0, END)
        start_time_entry.delete(0, END)
        end_time_entry.delete(0, END)
        shift_treeview.selection_remove(shift_treeview.selection())

    # --- ایجاد رابط کاربری ---

    shift_frame = Frame(
        window,
        width=window.winfo_width() - 200,
        height=window.winfo_height(),
        bg="white",
    )
    shift_frame.place(x=0, y=100)  # تنظیم موقعیت فرم در سمت چپ صفحه

    heading_label = Label(
        shift_frame,
        text="تعریف شیفت",
        font=("fonts/Persian-Yekan.ttf", 16, "bold"),
        bg="#00198f",
        fg="white",
    )
    heading_label.place(x=0, y=0, relwidth=1)

    # اگر back_button.png ندارید، از این استفاده کنید یا کامنت کنید
    try:
        back_image = PhotoImage(file="images/back_button.png")
        back_button = Button(
            shift_frame,
            image=back_image,
            bd=0,
            cursor="hand2",
            bg="white",
            command=lambda: shift_frame.place_forget(),
        )
        back_button.place(x=10, y=10)
    except:
        # اگر آیکون وجود ندارد، دکمه متنی ایجاد کنید
        back_button = Button(
            shift_frame,
            text="← بازگشت",
            font=("fonts/Persian-Yekan.ttf", 12),
            bg="#00198f",
            fg="white",
            bd=0,
            cursor="hand2",
            command=lambda: shift_frame.place_forget(),
        )
        back_button.place(x=10, y=10)

    top_frame = Frame(shift_frame, bg="white")
    top_frame.place(x=20, y=50, width=1125, height=235)

    # ایجاد Treeview به صورت مستقیم و ساده
    tree_frame = Frame(top_frame, bg="white")
    tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    horizontal_scrollbar = Scrollbar(tree_frame, orient=HORIZONTAL)
    vertical_scrollbar = Scrollbar(tree_frame, orient=VERTICAL)

    shift_treeview = ttk.Treeview(
        tree_frame,
        columns=("id", "name", "start", "end"),
        show="headings",
        yscrollcommand=vertical_scrollbar.set,
        xscrollcommand=horizontal_scrollbar.set,
        height=8,
    )

    shift_treeview.heading("id", text="شناسه")
    shift_treeview.heading("name", text="نام شیفت")
    shift_treeview.heading("start", text="ساعت شروع")
    shift_treeview.heading("end", text="ساعت پایان")

    shift_treeview.column("id", width=80, anchor="center", minwidth=50)
    shift_treeview.column("name", width=250, anchor="center", minwidth=150)
    shift_treeview.column("start", width=150, anchor="center", minwidth=100)
    shift_treeview.column("end", width=150, anchor="center", minwidth=100)

    horizontal_scrollbar.config(command=shift_treeview.xview)
    vertical_scrollbar.config(command=shift_treeview.yview)

    shift_treeview.grid(row=0, column=0, sticky="nsew")
    vertical_scrollbar.grid(row=0, column=1, sticky="ns")
    horizontal_scrollbar.grid(row=1, column=0, sticky="ew", columnspan=2)

    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)

    # ایجاد فرم ورود اطلاعات
    detail_frame = Frame(shift_frame, bg="white")
    detail_frame.place(x=30, y=300)

    shift_name_label = Label(
        detail_frame,
        text="نام شیفت *",
        font=("fonts/Persian-Yekan.ttf", 12, "bold"),
        bg="white",
    )
    shift_name_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
    shift_name_entry = Entry(
        detail_frame, font=("fonts/Persian-Yekan.ttf", 12), bg="lightblue", width=25
    )
    shift_name_entry.grid(row=0, column=1, padx=20, pady=10)

    start_time_label = Label(
        detail_frame,
        text="ساعت شروع *",
        font=("fonts/Persian-Yekan.ttf", 12, "bold"),
        bg="white",
    )
    start_time_label.grid(row=0, column=2, padx=20, pady=10, sticky="w")
    start_time_entry = Entry(
        detail_frame, font=("fonts/Persian-Yekan.ttf", 12), bg="lightblue", width=15
    )
    start_time_entry.insert(0, "08:00")
    start_time_entry.grid(row=0, column=3, padx=20, pady=10)
    Label(
        detail_frame,
        text="(فرمت: HH:MM)",
        font=("fonts/Persian-Yekan.ttf", 10, "bold"),
        bg="white",
        fg="gray",
    ).grid(row=1, column=3, sticky="w", padx=20)

    end_time_label = Label(
        detail_frame,
        text="ساعت پایان *",
        font=("fonts/Persian-Yekan.ttf", 12, "bold"),
        bg="white",
    )
    end_time_label.grid(row=0, column=4, padx=20, pady=10, sticky="w")
    end_time_entry = Entry(
        detail_frame, font=("fonts/Persian-Yekan.ttf", 12), bg="lightblue", width=15
    )
    end_time_entry.insert(0, "16:00")
    end_time_entry.grid(row=0, column=5, padx=20, pady=10)
    Label(
        detail_frame,
        text="(فرمت: HH:MM)",
        font=("fonts/Persian-Yekan.ttf", 10),
        bg="white",
        fg="gray",
    ).grid(row=1, column=5, sticky="w", padx=20)

    button_frame = Frame(shift_frame, bg="white")
    button_frame.place(x=350, y=450)

    add_button = Button(
        button_frame,
        text="➕ افزودن شیفت",
        font=("fonts/Persian-Yekan.ttf", 12),
        fg="white",
        bg="#00198f",
        width=15,
        command=add_shift,
    )
    add_button.grid(row=0, column=0, padx=10)

    update_button = Button(
        button_frame,
        text="✏️ ویرایش شیفت",
        font=("fonts/Persian-Yekan.ttf", 12),
        fg="white",
        bg="#00198f",
        width=15,
        command=update_shift,
    )
    update_button.grid(row=0, column=1, padx=10)

    delete_button = Button(
        button_frame,
        text="🗑️ حذف شیفت",
        font=("fonts/Persian-Yekan.ttf", 12),
        fg="white",
        bg="#00198f",
        width=15,
        command=delete_shift,
    )
    delete_button.grid(row=0, column=2, padx=10)

    clear_button = Button(
        button_frame,
        text="🧹 پاک کردن فیلدها",
        font=("fonts/Persian-Yekan.ttf", 12),
        fg="white",
        bg="#00198f",
        width=15,
        command=clear_fields,
    )
    clear_button.grid(row=0, column=3, padx=10)
# ===== دکمه‌های CSV (مثل صفحه محصولات) =====
    csv_frame = Frame(shift_frame, bg="white")
    csv_frame.place(x=350, y=510)

    # ===== دکمه‌های CSV (وسط ۴ دکمه بالا) =====

    import_button = Button(
    button_frame,
    text="📥 وارد کردن CSV",
    font=("fonts/Persian-Yekan.ttf", 11),
    width=15,
    fg="white",
    bg="#4b39e9",
    command=lambda: import_shift_from_csv(shift_treeview),
)

    export_button = Button(
    button_frame,
    text="📤 خروجی CSV",
    font=("fonts/Persian-Yekan.ttf", 11),
    width=15,
    fg="white",
    bg="#4b39e9",
    command=lambda: export_shift_to_csv(shift_treeview),
)
    # نام شیفت → ساعت شروع → ساعت پایان
    shift_name_entry.bind("<Tab>", lambda e: move_focus(start_time_entry))
    start_time_entry.bind("<Tab>", lambda e: move_focus(end_time_entry))
    end_time_entry.bind("<Tab>", lambda e: move_focus(add_button))
    add_button.bind("<Tab>", lambda e: move_focus(update_button))
    update_button.bind("<Tab>", lambda e: move_focus(delete_button))
    delete_button.bind("<Tab>", lambda e: move_focus(clear_button))
    clear_button.bind("<Tab>", lambda e: move_focus(import_button))
    import_button.bind("<Tab>", lambda e: move_focus(export_button))
    export_button.bind("<Tab>", lambda e: move_focus(shift_treeview))
    shift_treeview.bind("<Tab>", lambda e: move_focus(shift_name_entry))




# ⬇️ ستون 1 و 2 یعنی وسط ۴ دکمه
    import_button.grid(row=1, column=1, padx=10, pady=10)
    export_button.grid(row=1, column=2, padx=10, pady=10)

    # ================= میانبرهای صفحه شیفت =================

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
        shift_name_entry.focus_set()

    def close_form(event=None):
        shift_frame.place_forget()

        # ================= Bind کلیدهای میانبر =================

    window.bind("<Control-a>", add_shortcut)   # افزودن
    window.bind("<Control-u>", update_shortcut)  # ویرایش
    window.bind("<Control-d>", delete_shortcut)  # حذف
    window.bind("<Control-c>", clear_shortcut)   # پاک کردن

    window.bind("<Control-i>", import_shortcut)  # Import CSV
    window.bind("<Control-e>", export_shortcut)  # Export CSV

    window.bind("<Control-f>", focus_name_shortcut)  # فوکوس نام شیفت
    window.bind("<Escape>", close_form)  # بستن فرم




    shift_treeview.bind("<ButtonRelease-1>", lambda event: select_data(event))

    create_shift_table()
    treeview_data(shift_treeview)
    shift_name_entry.focus_set()


    return shift_frame
