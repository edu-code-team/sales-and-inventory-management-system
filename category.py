from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from employees import connect_database
from tkinter import filedialog
import csv


def move_focus(widget):
    widget.focus_set()
    return "break"


def export_to_excel(treeview):
    """
    تابع برای ذخیره داده‌های treeview در فایل CSV
    """
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
            title="ذخیره فایل",
        )

        if file_path:
            with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow(["شناسه", "نام دسته بندی", "توضیحات"])
                writer.writerows(data)

            messagebox.showinfo(
                "موفقیت", f"داده‌ها با موفقیت در\n{file_path}\nذخیره شدند"
            )

    except Exception as e:
        messagebox.showerror("خطا", f"خطا در ذخیره‌سازی: {str(e)}")


def import_from_csv(treeview):
    """
    تابع برای وارد کردن داده‌ها از فایل CSV به دیتابیس دسته‌بندی
    """
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
                if len(row) < 3:
                    skipped_count += 1
                    errors.append(f"سطر {idx}: تعداد ستون‌ها ناکافی است (نیاز به 3 ستون)")
                    continue
                    
                try:
                    id_val = row[0].strip()
                    name_val = row[1].strip()
                    description_val = row[2].strip()
                    
                    # چک کردن فیلدهای خالی
                    if not id_val or not name_val:
                        skipped_count += 1
                        errors.append(f"سطر {idx}: شناسه یا نام خالی است")
                        continue
                    
                    # چک کردن شناسه عددی
                    if not id_val.isdigit():
                        skipped_count += 1
                        errors.append(f"سطر {idx}: شناسه باید عددی باشد")
                        continue
                    
                    # چک کردن وجود دسته‌بندی
                    cursor.execute("SELECT * FROM category_data WHERE id=%s", (id_val,))
                    if cursor.fetchone():
                        skipped_count += 1
                        errors.append(f"سطر {idx}: شناسه {id_val} تکراری است")
                        continue
                        
                    # وارد کردن دسته‌بندی جدید
                    cursor.execute(
                        "INSERT INTO category_data (id, name, description) VALUES (%s, %s, %s)",
                        (int(id_val), name_val, description_val)
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
        
        if errors and len(errors) <= 10:  # نمایش حداکثر 10 خطا
            result_message += "\nخطاها:\n"
            for error in errors[:10]:
                result_message += f"• {error}\n"
        elif errors:
            result_message += f"\n{len(errors)} خطا رخ داده است (اولین 10 خطا نمایش داده شد)"
        
        messagebox.showinfo("عملیات وارد کردن", result_message)
        
        # تازه‌سازی داده‌ها
        treeview_data(treeview)
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        messagebox.showerror("خطا", f"خطا در وارد کردن فایل: {str(e)}")


def update_category(id_entry, name_entry, description_text, treeview, clear_func):
    id_val = id_entry.get()
    name_val = name_entry.get()
    description_val = description_text.get(1.0, END).strip()

    if id_val == "" or name_val == "" or description_val == "":
        messagebox.showerror("خطا", "پر کردن تمام فیلدها الزامیست")
        return

    selected = treeview.selection()
    if not selected:
        messagebox.showerror("خطا", "هیچ ردیفی برای بروزرسانی انتخاب نشده است")
        return

    item = treeview.item(selected[0])
    old_id = item["values"][0]
    old_name = item["values"][1]
    old_description = item["values"][2]

    if (
        id_val == str(old_id)
        and name_val == old_name
        and description_val == old_description
    ):
        messagebox.showinfo("اطلاع", "تغییری در داده‌ها ایجاد نشده است")
        clear_func()
        return

    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute("USE inventory_system")

        if id_val != str(old_id):
            cursor.execute("SELECT * FROM category_data WHERE id=%s", (id_val,))
            if cursor.fetchone():
                messagebox.showerror("خطا", "شناسه تکراری است")
                return

        cursor.execute(
            """
            UPDATE category_data 
            SET id=%s, name=%s, description=%s 
            WHERE id=%s
        """,
            (id_val, name_val, description_val, old_id),
        )

        connection.commit()
        messagebox.showinfo("عملیات موفق", "دسته‌بندی با موفقیت بروزرسانی شد")
        treeview_data(treeview)
        clear_func()

    except Exception as e:
        messagebox.showerror("خطا", f"خطا در بروزرسانی: {e}")
    finally:
        cursor.close()
        connection.close()


def delete_category(treeview, clear_func, id_entry, first_entry=None):
    index = treeview.selection()
    command = lambda: delete_category(treeview, clear_func, id_entry)
    first_entry.focus_set()

    if not index:
        messagebox.showerror("خطا", "هیچ ردیفی انتخاب نشده است")
        return

    content = treeview.item(index)
    row = content["values"]
    id_val = row[0]

    confirm = messagebox.askyesno("تایید حذف", "آیا از حذف این ردیف مطمئن هستید؟")
    if not confirm:
        return

    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute("USE inventory_system")
        cursor.execute("DELETE FROM category_data WHERE id=%s", (id_val,))
        connection.commit()
        treeview_data(treeview)
        messagebox.showinfo("اطلاعات", "ردیف انتخاب شده حذف شد")
        clear_func()
        id_entry.focus_set()

    except Exception as e:
        messagebox.showerror("خطا", f"خطا به دلیل {e}")

    finally:
        cursor.close()
        connection.close()


def clear_fields(id_entry, category_name_entry, description_text):
    id_entry.delete(0, END)
    category_name_entry.delete(0, END)
    description_text.delete(1.0, END)


def treeview_data(treeview):
    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute("USE inventory_system")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS category_data (id INT PRIMARY KEY, name VARCHAR(100), description TEXT)"
        )
        cursor.execute("SELECT * FROM category_data")
        records = cursor.fetchall()
        treeview.delete(*treeview.get_children())
        for record in records:
            treeview.insert("", END, values=record)

    except Exception as e:
        messagebox.showerror("خطا", f"خطا به دلیل {e}")

    finally:
        cursor.close()
        connection.close()


def select_data(event, treeview, id_entry, name_entry, description_text):
    selected = treeview.selection()
    if not selected:
        return

    item = treeview.item(selected[0])
    content = item["values"]

    id_entry.delete(0, END)
    name_entry.delete(0, END)
    description_text.delete(1.0, END)

    id_entry.insert(0, content[0])
    name_entry.insert(0, content[1])
    description_text.insert(1.0, content[2])


def add_category(id_val, name_val, description_val, treeview, clear_func):
    if id_val == "" or name_val == "" or description_val == "":
        messagebox.showerror("خطا", "پر کردن تمام فیلدها الزامیست")
        return

    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute("USE inventory_system")
        cursor.execute("SELECT * FROM category_data WHERE id=%s", (id_val,))
        if cursor.fetchone():
            messagebox.showerror("خطا", "شناسه محصول تکراری است")
            return

        cursor.execute(
            "INSERT INTO category_data VALUES(%s, %s, %s)",
            (id_val, name_val, description_val),
        )
        connection.commit()
        messagebox.showinfo("اطلاعات", "با موفقیت وارد شد")
        treeview_data(treeview)
        clear_func()

    except Exception as e:
        messagebox.showerror("خطا", f"خطا به دلیل {e}")

    finally:
        cursor.close()
        connection.close()


def category_form(window):
    global back_image, logo
    category_frame = Frame(
        window,
        width=window.winfo_width() - 200,
        height=window.winfo_height(),
        bg="white",
    )
    category_frame.place(x=0, y=100)  # تنظیم موقعیت فرم در سمت چپ صفحه

    heading_label = Label(
        category_frame,
        text="مدیریت دسته بندی محصولات",
        font=("fonts/Persian-Yekan.ttf", 18, "bold"),
        bg="#00198f",
        fg="white",
    )
    heading_label.place(x=0, y=0, relwidth=1)

    back_image = PhotoImage(file="images/back_button.png")
    back_button = Button(
        category_frame,
        image=back_image,
        bd=0,
        cursor="hand2",
        bg="white",
        command=lambda: category_frame.place_forget(),
    )
    back_button.place(x=10, y=45)

    logo = PhotoImage(file="images/category_product.png")
    label = Label(category_frame, image=logo, bg="white")
    label.place(x=30, y=130)

    # ============ فریم برای دکمه‌های ایمپورت/اکسپورت ============
    import_export_frame = Frame(category_frame, bg="white")
    import_export_frame.place(x=30, y=80, width=300)

    # دکمه ایمپورت
    import_button = Button(
        import_export_frame,
        text="📥 وارد کردن CSV",
        font=("fonts/Persian-Yekan.ttf", 11),
        width=15,
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
        width=15,
        fg="white",
        bg="#4b39e9",
        command=lambda: export_to_excel(treeview),
    )
    export_button.pack(side=LEFT, padx=5)

    # ============ قسمت فرم ورودی ============
    details_frame = Frame(category_frame, bg="white")
    details_frame.place(x=630, y=70, width=500, height=200)

    # labelها سمت راست با راست‌چین کامل
    id_label = Label(
        details_frame,
        text="شناسه",
        font=("fonts/Persian-Yekan.ttf", 14, "bold"),
        bg="white",
        anchor="e",
        width=15,
    )  # anchor='e' برای راست‌چین
    id_label.grid(
        row=0, column=1, padx=(0, 20), pady=10, sticky="e"
    )  # padx=(0, 20): فاصله از راست

    id_entry = Entry(
        details_frame,
        font=("fonts/Persian-Yekan.ttf", 12),
        bg="lightblue",
        width=25,
        justify=RIGHT,
    )
    id_entry.grid(row=0, column=0, padx=(20, 10), pady=10, sticky="ew")

    category_name_label = Label(
        details_frame,
        text="نام دسته بندی",
        font=("fonts/Persian-Yekan.ttf", 14, "bold"),
        bg="white",
        anchor="e",
        width=15,
    )
    category_name_label.grid(row=1, column=1, padx=(0, 20), pady=10, sticky="e")

    category_name_entry = Entry(
        details_frame,
        font=("fonts/Persian-Yekan.ttf", 12),
        bg="lightblue",
        width=25,
        justify=RIGHT,
    )
    category_name_entry.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="ew")

    description_label = Label(
        details_frame,
        text="توضیحات",
        font=("fonts/Persian-Yekan.ttf", 14, "bold"),
        bg="white",
        anchor="ne",
        width=15,
    )  # anchor='ne' برای بالا-راست
    description_label.grid(row=2, column=1, padx=(0, 20), pady=10, sticky="ne")

    description_text = Text(
        details_frame,
        width=25,
        height=4,
        bd=2,
        bg="lightblue",
        font=("fonts/Persian-Yekan.ttf", 12),
    )
    description_text.grid(row=2, column=0, padx=(20, 10), pady=10, sticky="nsew")
    # غیرفعال کردن Tab پیش‌فرض Text
    description_text.unbind_class("Text", "<Tab>")
    description_text.unbind_class("Text", "<Shift-Tab>")

    details_frame.grid_rowconfigure(2, weight=1)
    details_frame.grid_columnconfigure(0, weight=1)
    details_frame.grid_columnconfigure(1, minsize=120)

    # ============ قسمت دکمه‌ها ============
    button_frame = Frame(category_frame, bg="white")
    button_frame.place(x=630, y=280, width=500, height=50)

    clear_func = lambda: clear_fields(id_entry, category_name_entry, description_text)

    clear_func()
    id_entry.focus_set()

    add_button = Button(
        button_frame,
        text="افزودن",
        font=("fonts/Persian-Yekan.ttf", 12),
        width=12,
        fg="white",
        bg="#00198f",
        command=lambda: add_category(
            id_entry.get(),
            category_name_entry.get(),
            description_text.get(1.0, END).strip(),
            treeview,
            clear_func,
        ),
    )
    add_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    delete_button = Button(
        button_frame,
        text="حذف",
        font=("fonts/Persian-Yekan.ttf", 12),
        width=12,
        fg="white",
        bg="#00198f",
        command=lambda: delete_category(treeview, clear_func,id_entry,category_name_entry),
    )
    delete_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    update_button = Button(
        button_frame,
        text="ویرایش",
        font=("fonts/Persian-Yekan.ttf", 12),
        width=12,
        fg="white",
        bg="#00198f",
        command=lambda: update_category(id_entry,category_name_entry,description_text,treeview,clear_func),
    )
    update_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    clear_button = Button(
        button_frame,
        text="پاک کردن",
        font=("fonts/Persian-Yekan.ttf", 12),
        width=12,
        fg="white",
        bg="#00198f",
        command=clear_func,
    )
    clear_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

    # ================= KEYBOARD SHORTCUTS (CATEGORY) =================

    def add_shortcut(event=None):
        add_button.invoke()

    def update_shortcut(event=None):
        update_button.invoke()

    def delete_shortcut(event=None):
        delete_button.invoke()

    def clear_shortcut(event=None):
        clear_button.invoke()

    def focus_id(event=None):
        id_entry.focus_set()

    def import_shortcut(event=None):
        import_button.invoke()

    def export_shortcut(event=None):
        export_button.invoke()

    def close_form(event=None):
        category_frame.place_forget()

    # Bind shortcuts
    window.bind("<Control-a>", add_shortcut)
    window.bind("<Control-A>", add_shortcut)

    window.bind("<Control-u>", update_shortcut)
    window.bind("<Control-U>", update_shortcut)

    window.bind("<Control-d>", delete_shortcut)
    window.bind("<Control-D>", delete_shortcut)

    window.bind("<Control-c>", clear_shortcut)
    window.bind("<Control-C>", clear_shortcut)

    window.bind("<Control-f>", focus_id)
    window.bind("<Control-F>", focus_id)

    window.bind("<Control-i>", import_shortcut)
    window.bind("<Control-I>", import_shortcut)

    window.bind("<Control-e>", export_shortcut)
    window.bind("<Control-E>", export_shortcut)

    window.bind("<Escape>", close_form)
    window.bind("<Return>", add_shortcut)

    category_frame.focus_set()

    # ---------- TAB ORDER (CATEGORY FORM) ----------

    id_entry.focus_set()

    id_entry.bind("<Tab>", lambda e: move_focus(category_name_entry))
    category_name_entry.bind("<Tab>", lambda e: move_focus(description_text))

    description_text.bind("<Tab>", lambda e: move_focus(add_button))
    description_text.bind("<Shift-Tab>", lambda e: move_focus(category_name_entry))

    add_button.bind("<Tab>", lambda e: move_focus(delete_button))
    delete_button.bind("<Tab>", lambda e: move_focus(update_button))
    update_button.bind("<Tab>", lambda e: move_focus(clear_button))
    clear_button.bind("<Tab>", lambda e: move_focus(import_button))
    import_button.bind("<Tab>", lambda e: move_focus(export_button))
    


    for i in range(4):
        button_frame.grid_columnconfigure(i, weight=1)

    # ============ قسمت treeview ============
    treeview_frame = Frame(category_frame, bg="white")
    treeview_frame.place(x=630, y=340, width=500, height=200)

    scrolly = Scrollbar(treeview_frame, orient=VERTICAL)
    scrollx = Scrollbar(treeview_frame, orient=HORIZONTAL)

    treeview = ttk.Treeview(
        treeview_frame,
        columns=("id", "name", "desc"),
        show="headings",
        yscrollcommand=scrolly.set,
        xscrollcommand=scrollx.set,
        height=8,
    )

    scrolly.pack(side=RIGHT, fill=Y)
    scrollx.pack(side=BOTTOM, fill=X)
    treeview.pack(side=LEFT, fill=BOTH, expand=True)

    scrollx.config(command=treeview.xview)
    scrolly.config(command=treeview.yview)

    treeview.heading("id", text="شناسه")
    treeview.heading("name", text="نام دسته بندی")
    treeview.heading("desc", text="توضیحات")

    treeview.column("id", width=120, anchor="center")
    treeview.column("name", width=200, anchor="center")
    treeview.column("desc", width=300, anchor="center")

    treeview_data(treeview)
    # ---------- TAB FIX AFTER TREEVIEW CREATED ----------

    export_button.bind("<Tab>", lambda e: move_focus(treeview))
    treeview.bind("<Tab>", lambda e: move_focus(id_entry))


    treeview.bind(
        "<<TreeviewSelect>>",
        lambda event: select_data(
            event, treeview, id_entry, category_name_entry, description_text
        ),
    )