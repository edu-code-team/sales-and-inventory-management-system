from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from employees import connect_database
from tkinter import filedialog
import csv


def move_focus(widget):
    widget.focus_force()
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
                writer.writerow(["شناسه", "دسته‌بندی", "تأمین‌کننده", "نام", "قیمت", "مقدار", "وضعیت"])
                writer.writerows(data)

            messagebox.showinfo(
                "موفقیت", f"داده‌ها با موفقیت در\n{file_path}\nذخیره شدند"
            )

    except Exception as e:
        messagebox.showerror("خطا", f"خطا در ذخیره‌سازی: {str(e)}")


def import_from_csv(treeview, category_combobox, supplier_combobox):
    """
    تابع برای وارد کردن داده‌ها از فایل CSV به دیتابیس
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
                if len(row) < 7:
                    skipped_count += 1
                    errors.append(f"سطر {idx}: تعداد ستون‌ها ناکافی است")
                    continue
                    
                try:
                    # چک کردن وجود دسته‌بندی
                    category = row[1].strip()
                    cursor.execute("SELECT name FROM category_data WHERE name=%s", (category,))
                    if not cursor.fetchone():
                        skipped_count += 1
                        errors.append(f"سطر {idx}: دسته‌بندی '{category}' وجود ندارد")
                        continue
                    
                    # چک کردن وجود تأمین‌کننده
                    supplier = row[2].strip()
                    cursor.execute("SELECT name FROM supplier_data WHERE name=%s", (supplier,))
                    if not cursor.fetchone():
                        skipped_count += 1
                        errors.append(f"سطر {idx}: تأمین‌کننده '{supplier}' وجود ندارد")
                        continue
                    
                    # چک کردن وجود محصول
                    product_name = row[3].strip()
                    cursor.execute(
                        "SELECT * FROM product_data WHERE name=%s AND category=%s AND supplier=%s",
                        (product_name, category, supplier)
                    )
                    
                    if cursor.fetchone():
                        skipped_count += 1
                        errors.append(f"سطر {idx}: محصول '{product_name}' از قبل وجود دارد")
                        continue
                        
                    # وارد کردن محصول جدید
                    cursor.execute(
                        "INSERT INTO product_data (category, supplier, name, price, quantity, status) VALUES (%s, %s, %s, %s, %s, %s)",
                        (category, supplier, product_name, float(row[4]), int(row[5]), row[6].strip())
                    )
                    imported_count += 1
                    
                except ValueError as ve:
                    skipped_count += 1
                    errors.append(f"سطر {idx}: خطا در فرمت داده‌ها - {str(ve)}")
                except Exception as e:
                    skipped_count += 1
                    errors.append(f"سطر {idx}: خطای عمومی - {str(e)}")
        
        connection.commit()
        
        # تازه‌سازی Comboboxها
        fetch_supplier_category(category_combobox, supplier_combobox)
        
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
        load_product_data(treeview)
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        messagebox.showerror("خطا", f"خطا در وارد کردن فایل: {str(e)}")


def filter_products(treeview, category, supplier, status):
    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    query = "SELECT * FROM product_data WHERE 1=1"
    params = []

    if category != "همه":
        query += " AND category=%s"
        params.append(category)

    if supplier != "همه":
        query += " AND supplier=%s"
        params.append(supplier)

    if status != "همه":
        query += " AND status=%s"
        params.append(status)

    cursor.execute("USE inventory_system")
    cursor.execute(query, tuple(params))
    records = cursor.fetchall()

    treeview.delete(*treeview.get_children())
    for record in records:
        treeview.insert("", END, values=record)

    cursor.close()
    connection.close()


def clear_fields(
    category_combobox,
    supplier_combobox,
    name_entry,
    price_entry,
    quantity_entry,
    status_combobox,
):
    category_combobox.set("انتخاب کنید")
    supplier_combobox.set("انتخاب کنید")
    name_entry.delete(0, END)
    price_entry.delete(0, END)
    quantity_entry.delete(0, END)
    status_combobox.set("یک مورد را انتخاب کنید")


def delete_product(
    treeview,
    category_combobox,
    supplier_combobox,
    name_entry,
    price_entry,
    quantity_entry,
    status_combobox,
):
    selected = treeview.selection()
    if not selected:
        messagebox.showerror("خطا", "هیچ ردیفی انتخاب نشده است")
        return

    item = treeview.item(selected[0])
    content = item["values"]
    id = content[0]

    ans = messagebox.askyesno("تاییدیه", "آیا از حذف ردیف منتخب اطمینان دارید؟")
    if ans:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        try:
            cursor.execute("use inventory_system")
            cursor.execute(" DELETE FROM product_data WHERE id=%s", (id,))
            connection.commit()
            load_product_data(treeview)
            messagebox.showinfo("اطلاعات", "ردیف انتخاب شده حذف شد")
            clear_fields(
                category_combobox,
                supplier_combobox,
                name_entry,
                price_entry,
                quantity_entry,
                status_combobox,
            )

            category_combobox.focus_set()

        except Exception as e:
            messagebox.showerror("خطا", f"خطا به دلیل {e}")
        finally:
            cursor.close()
            connection.close()


def update_product(category, supplier, name, price, quantity, status, treeview):
    selected = treeview.selection()
    item = treeview.item(selected[0])
    content = item["values"]
    id = content[0]
    if not selected:
        messagebox.showerror("خطا", "هیچ ردیفی انتخاب نشده است")
        return
    cursor, connection = connect_database()
    if not cursor or not connection:
        return
    cursor.execute("use inventory_system")
    cursor.execute(" SELECT * from product_data WHERE id=%s", (id,))
    current_data = cursor.fetchone()
    current_data = current_data[1:]
    current_data = list(current_data)
    current_data[3] = str(current_data[3])
    current_data = tuple(current_data)

    quantity = int(quantity)
    new_data = (category, supplier, name, price, quantity, status)

    if current_data == new_data:
        messagebox.showinfo("اطلاعات", " تغییرات را اعمال کنید")
        return

    cursor.execute(
        " UPDATE product_data SET category=%s, supplier=%s, name=%s, price=%s, quantity=%s, status=%s "
        "WHERE id=%s",
        (category, supplier, name, price, quantity, status, id),
    )
    connection.commit()
    messagebox.showinfo("اطلاعات", "اطلاعات به روز رسانی شد")
    load_product_data(treeview)
    clear_fields(
        category_combobox,
        supplier_combobox,
        name_entry,
        price_entry,
        quantity_entry,
        status_combobox,
    )


def select_data(
    event,
    treeview,
    category_combobox,
    supplier_combobox,
    name_entry,
    price_entry,
    quantity_entry,
    status_combobox,
):
    selected = treeview.selection()
    if not selected:
        return

    item = treeview.item(selected[0])
    content = item["values"]

    name_entry.delete(0, END)
    price_entry.delete(0, END)
    quantity_entry.delete(0, END)

    category_combobox.set(content[1])
    supplier_combobox.set(content[2])
    name_entry.insert(0, content[3])
    price_entry.insert(0, content[4])
    quantity_entry.insert(0, content[5])
    status_combobox.set(content[6])


def load_product_data(treeview):
    cursor, connection = connect_database()
    if not cursor or not connection:
        return
    try:
        cursor.execute("USE inventory_system")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS product_data (id INT AUTO_INCREMENT PRIMARY KEY, category VARCHAR(50), "
            "supplier VARCHAR(50), name VARCHAR(100), price DECIMAL(10,2),quantity INT,status VARCHAR(50))"
        )
        cursor.execute("Select * from product_data")
        records = cursor.fetchall()
        treeview.delete(*treeview.get_children())
        for record in records:
            treeview.insert("", END, values=record)
    except Exception as e:
        messagebox.showerror("خطا", f"خطا به دلیل {e}")
    finally:
        cursor.close()
        connection.close()


def fetch_supplier_category(category_combobox, supplier_combobox):
    category_option = []
    supplier_option = []
    cursor, connection = connect_database()
    if not cursor or not connection:
        return
    cursor.execute("USE inventory_system")
    cursor.execute("SELECT name FROM category_data")
    names = cursor.fetchall()
    if len(names) > 0:
        category_combobox.set("انتخاب کنید")
        for name in names:
            category_option.append(name[0])
        category_combobox.config(value=category_option)

    cursor.execute("SELECT name FROM supplier_data")
    names = cursor.fetchall()
    if len(names) > 0:
        supplier_combobox.set("انتخاب کنید")
        for name in names:
            supplier_option.append(name[0])
        supplier_combobox.config(value=supplier_option)


def add_product(category, supplier, name, price, quantity, status, treeview):
    if category == "خالی":
        messagebox.showerror("خطا", "لطفا دسته بندی را اضافه کنید")
    elif supplier == "خالی":
        messagebox.showerror("خطا", "لطفا تامین کننده را اضافه کنید")
    elif (
        category == "انتخاب کنید"
        or supplier == "انتخاب کنید"
        or name == ""
        or price == ""
        or quantity == ""
        or status == "یک مورد را انتخاب کنید"
    ):
        messagebox.showerror("خطا", "پر کردن تمامی فیلد ها الزامی است")
    else:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        cursor.execute("USE inventory_system")

        cursor.execute(
            "SELECT * FROM product_data WHERE category=%s AND supplier=%s AND name=%s",
            (category, supplier, name),
        )
        existing_product = cursor.fetchone()
        if existing_product:
            messagebox.showerror("خطا!", "محصول از قبل وجود دارد!")
            return

        cursor.execute(
            "INSERT INTO product_data (category, supplier, name, price, quantity, status) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (category, supplier, name, price, quantity, status),
        )
        connection.commit()
        messagebox.showinfo("عمل موفق", "محصول با موفقیت افزوده شد")
        load_product_data(treeview)
        clear_fields(
            category_combobox,
            supplier_combobox,
            name_entry,
            price_entry,
            quantity_entry,
            status_combobox,
        )


def product_form(window):
    global treeview
    global name_entry, price_entry, quantity_entry
    global category_combobox, supplier_combobox, status_combobox
    global back_image

    product_frame = Frame(
        window,
        width=window.winfo_width() - 200,
        height=window.winfo_height(),
        bg="white",
    )
    product_frame.place(x=0, y=100)  # تنظیم موقعیت فرم در سمت چپ صفحه

    back_image = PhotoImage(file="images/back_button.png")
    back_button = Button(
        product_frame,
        image=back_image,
        bd=0,
        cursor="hand2",
        bg="white",
        command=lambda: product_frame.place_forget(),
    )
    back_button.place(x=10, y=0)
    
    left_frame = Frame(product_frame, bg="white", bd=2, relief=RIDGE)
    left_frame.place(x=window.winfo_width() - 700, y=40,height=490)

    # تنظیم ستون‌ها برای RTL
    left_frame.grid_columnconfigure(0, minsize=200)
    left_frame.grid_columnconfigure(1, minsize=120)

    heading_label = Label(
        left_frame,
        text="مدیریت جزییات محصولات",
        font=("fonts/Persian-Yekan.ttf", 16, "bold"),
        bg="#00198f",
        fg="white",
    )
    heading_label.grid(row=0, column=0, columnspan=2, sticky="we", pady=(0, 10))

    # ---------- helper ----------
    def rtl_label(text, row):
        Label(
            left_frame,
            text=text,
            font=("fonts/Persian-Yekan.ttf", 14, "bold"),
            bg="white",
            anchor="e",
        ).grid(row=row, column=1, padx=15, sticky="e")

    def rtl_entry(widget, row):
        widget.grid(row=row, column=0, pady=12, sticky="e")

    # ---------- دسته‌بندی ----------
    category_combobox = ttk.Combobox(
        left_frame,
        font=("fonts/Persian-Yekan.ttf", 14),
        width=18,
        state="readonly",
        justify="right",
    )
    rtl_entry(category_combobox, 1)
    rtl_label("دسته‌بندی", 1)

    # ---------- تامین‌کننده ----------
    supplier_combobox = ttk.Combobox(
        left_frame,
        font=("fonts/Persian-Yekan.ttf", 14),
        width=18,
        state="readonly",
        justify="right",
    )
    rtl_entry(supplier_combobox, 2)
    rtl_label("تأمین‌کننده", 2)

    # ---------- نام ----------
    name_entry = Entry(
        left_frame,
        font=("fonts/Persian-Yekan.ttf", 16, "bold"),
        bg="lightblue",
        justify="right",
    )
    rtl_entry(name_entry, 3)
    rtl_label("نام", 3)

    # ---------- قیمت ----------
    price_entry = Entry(
        left_frame,
        font=("fonts/Persian-Yekan.ttf", 16, "bold"),
        bg="lightblue",
        justify="right",
    )
    rtl_entry(price_entry, 4)
    rtl_label("قیمت", 4)

    # ---------- مقدار ----------
    quantity_entry = Entry(
        left_frame,
        font=("fonts/Persian-Yekan.ttf", 16, "bold"),
        bg="lightblue",
        justify="right",
    )
    rtl_entry(quantity_entry, 5)
    rtl_label("مقدار", 5)

    # ---------- وضعیت ----------
    status_combobox = ttk.Combobox(
        left_frame,
        values=("فعال", "غیرفعال"),
        font=("fonts/Persian-Yekan.ttf", 14),
        width=18,
        state="readonly",
        justify="right",
    )
    rtl_entry(status_combobox, 6)
    rtl_label("وضعیت", 6)
    status_combobox.set("یک مورد را انتخاب کنید")

    # ===== کلیدهای اصلی (4 دکمه اول) =====
    button_frame = Frame(left_frame, bg="white")
    button_frame.grid(row=7, columnspan=2, pady=20)

    add_button = Button(
        button_frame,
        text="افزودن",
        font=("fonts/Persian-Yekan.ttf", 12),
        width=8,
        fg="white",
        bg="#00198f",
        command=lambda: add_product(
            category_combobox.get(),
            supplier_combobox.get(),
            name_entry.get(),
            price_entry.get(),
            quantity_entry.get(),
            status_combobox.get(),
            treeview,
        ),
    )
    add_button.grid(row=0, column=0, padx=10, sticky="e")

    update_button = Button(
        button_frame,
        text="بروزرسانی",
        font=("fonts/Persian-Yekan.ttf", 12),
        width=8,
        fg="white",
        bg="#00198f",
        command=lambda: update_product(
            category_combobox.get(),
            supplier_combobox.get(),
            name_entry.get(),
            price_entry.get(),
            quantity_entry.get(),
            status_combobox.get(),
            treeview,
        ),
    )
    update_button.grid(row=0, column=1, padx=10, sticky="e")

    delete_button = Button(
        button_frame,
        text="حذف",
        font=("fonts/Persian-Yekan.ttf", 12),
        width=8,
        fg="white",
        bg="#00198f",
        command=lambda: delete_product(
            treeview,
            category_combobox,
            supplier_combobox,
            name_entry,
            price_entry,
            quantity_entry,
            status_combobox,
        ),
    )
    delete_button.grid(row=0, column=2, padx=10, sticky="e")

    clear_button = Button(
        button_frame,
        text="پاک کردن",
        font=("fonts/Persian-Yekan.ttf", 12),
        width=8,
        fg="white",
        bg="#00198f",
        command=lambda: clear_fields(
            category_combobox,
            supplier_combobox,
            name_entry,
            price_entry,
            quantity_entry,
            status_combobox,
        ),
    )
    clear_button.grid(row=0, column=3, padx=10, sticky="e")

    # ===== کلیدهای ایمپورت/اکسپورت (در زیر کلیدهای اصلی) =====
    import_export_frame = Frame(left_frame, bg="white")
    import_export_frame.grid(row=8, columnspan=2, pady=(0, 10))

    # دکمه ایمپورت
    import_button = Button(
        import_export_frame,
        text="📥 وارد کردن CSV",
        font=("fonts/Persian-Yekan.ttf", 11),
        width=15,
        fg="white",
        bg="#4b39e9",
        takefocus=True,
        command=lambda: import_from_csv(treeview, category_combobox, supplier_combobox),
    )
    import_button.grid(row=0, column=0, padx=5)

    # دکمه اکسپورت
    export_button = Button(
        import_export_frame,
        text="📊 خروجی CSV",
        font=("fonts/Persian-Yekan.ttf", 11),
        width=15,
        fg="white",
        bg="#4b39e9",
        takefocus=True,
        command=lambda: export_to_excel(treeview),
    )
    export_button.grid(row=0, column=1, padx=5)



    # ================= KEYBOARD SHORTCUTS (PRODUCTS) =================

    def add_shortcut(event=None):
        add_button.invoke()

    def update_shortcut(event=None):
        update_button.invoke()

    def delete_shortcut(event=None):
        delete_button.invoke()

    def clear_shortcut(event=None):
        clear_button.invoke()

    def search_shortcut(event=None):
        search_button.invoke()

    def show_all_shortcut(event=None):
        show_all_button.invoke()

    def focus_category(event=None):
        category_combobox.focus_set()

    def import_shortcut(event=None):
        import_button.invoke()

    def export_shortcut(event=None):
        export_button.invoke()

    def close_form(event=None):
        product_frame.place_forget()

    def search_shortcut(event=None):
        search_button.invoke()

    def show_all_shortcut(event=None):
        show_all_button.invoke()

    def focus_filter_shortcut(event=None):
        filter_category.focus_force()


    # Bind shortcuts
    window.bind("<Control-a>", add_shortcut)
    window.bind("<Control-A>", add_shortcut)

    window.bind("<Control-u>", update_shortcut)
    window.bind("<Control-U>", update_shortcut)

    window.bind("<Control-d>", delete_shortcut)
    window.bind("<Control-D>", delete_shortcut)

    window.bind("<Control-c>", clear_shortcut)
    window.bind("<Control-C>", clear_shortcut)

    window.bind("<Control-s>", search_shortcut)
    window.bind("<Control-S>", search_shortcut)
    window.bind("<Control-Return>", search_shortcut)

    window.bind("<Control-r>", show_all_shortcut)
    window.bind("<Control-R>", show_all_shortcut)

    window.bind("<Control-f>", focus_category)
    window.bind("<Control-F>", focus_category)

    window.bind("<Control-i>", import_shortcut)
    window.bind("<Control-I>", import_shortcut)

    window.bind("<Control-e>", export_shortcut)
    window.bind("<Control-E>", export_shortcut)

    window.bind("<Escape>", close_form)

    window.bind("<Control-Return>", search_shortcut)

    window.bind("<Control-r>", show_all_shortcut)
    window.bind("<Control-R>", show_all_shortcut)

    window.bind("<Control-f>", focus_filter_shortcut)
    window.bind("<Control-F>", focus_filter_shortcut)


    product_frame.focus_set()

    # ------------------------ فیلتر ------------------------
    filter_frame = Frame(product_frame, bg="white", bd=1, relief=SOLID)
    filter_frame.place(x=80, y=40, width=570, height=50)  # دقیقاً هم‌عرض TreeView

    # فونت
    f_font = ("fonts/Persian-Yekan.ttf", 11)

    # دسته‌بندی
    Label(filter_frame, text="دسته‌بندی", bg="white", font=f_font).place(x=10, y=2)
    filter_category = ttk.Combobox(filter_frame, width=14, state="readonly")
    filter_category.place(x=10, y=22)
    filter_category.set("همه")

    # تامین‌کننده
    Label(filter_frame, text="تأمین‌کننده", bg="white", font=f_font).place(x=150, y=2)
    filter_supplier = ttk.Combobox(filter_frame, width=14, state="readonly")
    filter_supplier.place(x=150, y=22)
    filter_supplier.set("همه")

    # وضعیت
    Label(filter_frame, text="وضعیت", bg="white", font=f_font).place(x=290, y=2)

    # جلوگیری از فوکوس گرفتن Label های فیلتر بالا
    for widget in filter_frame.winfo_children():
        if isinstance(widget, Label):
            widget.configure(takefocus=0)

    filter_status = ttk.Combobox(
        filter_frame,
        values=("همه", "فعال", "غیرفعال"),
        width=12,
        state="readonly",
    )
    filter_status.place(x=290, y=22)
    filter_status.set("همه")

    # دکمه اعمال
    search_button = Button(
        filter_frame,
        text=" جستجو",
        bg="#00198f",
        fg="white",
        width=9,
        command=lambda: filter_products(
            treeview,
            filter_category.get(),
            filter_supplier.get(),
            filter_status.get(),
        ),
    )
    search_button.place(x=410, y=20)

    show_all_button = Button(
        filter_frame,
        text="نمایش همه",
        bg="#00198f",
        fg="white",
        width=9,
        command=lambda: load_product_data(treeview),
    )
    show_all_button.place(x=485, y=20)

    # ------------------------ TreeView ------------------------
    treeview_frame = Frame(product_frame)
    treeview_frame.place(x=80, y=100, width=570, height=430)

    scrolly = Scrollbar(treeview_frame, orient=VERTICAL)
    scrollx = Scrollbar(treeview_frame, orient=HORIZONTAL)

    treeview = ttk.Treeview(
        treeview_frame,
        columns=("id", "category", "supplier", "name", "price", "quantity", "state"),
        show="headings",
        yscrollcommand=scrolly.set,
        xscrollcommand=scrollx.set,
    )

    scrolly.pack(side=RIGHT, fill=Y)
    scrollx.pack(side=BOTTOM, fill=X)
    scrollx.config(command=treeview.xview)
    scrolly.config(command=treeview.yview)
    treeview.pack(fill=BOTH, expand=1)

    treeview.heading("id", text="شناسه", anchor="e")
    treeview.heading("category", text="دسته‌بندی", anchor="e")
    treeview.heading("supplier", text="تأمین‌کننده", anchor="e")
    treeview.heading("name", text="نام", anchor="e")
    treeview.heading("price", text="قیمت", anchor="e")
    treeview.heading("quantity", text="مقدار", anchor="e")
    treeview.heading("state", text="وضعیت", anchor="e")

    # ست کردن عرض ستون‌ها
    treeview.column("category", width=100, anchor="e")
    treeview.column("supplier", width=120, anchor="e")
    treeview.column("name", width=120, anchor="e")
    treeview.column("price", width=80, anchor="e")
    treeview.column("quantity", width=80, anchor="e")
    treeview.column("state", width=80, anchor="e")

    fetch_supplier_category(category_combobox, supplier_combobox)
    filter_category.config(values=["همه"] + list(category_combobox["values"]))
    filter_supplier.config(values=["همه"] + list(supplier_combobox["values"]))

    load_product_data(treeview)

    treeview.bind(
        "<ButtonRelease-1>",
        lambda event: select_data(
            event,
            treeview,
            category_combobox,
            supplier_combobox,
            name_entry,
            price_entry,
            quantity_entry,
            status_combobox,
        ),
    )

    # ================= TAB FIX (PRODUCTS) =================

    category_combobox.focus_set()

    category_combobox.bind("<Tab>", lambda e: move_focus(supplier_combobox))
    supplier_combobox.bind("<Tab>", lambda e: move_focus(name_entry))
    name_entry.bind("<Tab>", lambda e: move_focus(price_entry))
    price_entry.bind("<Tab>", lambda e: move_focus(quantity_entry))
    quantity_entry.bind("<Tab>", lambda e: move_focus(status_combobox))
    status_combobox.bind("<Tab>", lambda e: move_focus(add_button))

    add_button.bind("<Tab>", lambda e: move_focus(update_button))
    update_button.bind("<Tab>", lambda e: move_focus(delete_button))
    delete_button.bind("<Tab>", lambda e: move_focus(clear_button))

    clear_button.bind("<Tab>", lambda e: move_focus(import_button))
    import_button.bind("<Tab>", lambda e: move_focus(export_button))
    export_button.bind("<Tab>", lambda e: move_focus(filter_category))
    filter_category.bind("<Tab>", lambda e: move_focus(filter_supplier))
    filter_supplier.bind("<Tab>", lambda e: move_focus(filter_status))

# ---- جستجو / نمایش همه ----
    filter_status.bind("<Tab>", lambda e: move_focus(search_button))
    search_button.bind("<Tab>", lambda e: move_focus(show_all_button))

# ---- جدول ----
    show_all_button.bind("<Tab>", lambda e: move_focus(treeview))
    treeview.bind("<Tab>", lambda e: move_focus(category_combobox))