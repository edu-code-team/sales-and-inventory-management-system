from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from employees import connect_database

from tkinter import filedialog
import csv
from tkinter import messagebox


# تابع برای ذخیره داده‌های تامین‌کنندگان در فایل CSV
def export_supplier_to_csv(treeview):
    items = treeview.get_children()
    if not items:
        messagebox.showwarning("هشدار", "داده‌ای برای خروجی وجود ندارد")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="ذخیره فایل CSV",
    )
    if not file_path:
        return

    with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["شناسه تامین کننده", "نام تامین‌کننده", "شماره تماس", "توضیحات"]
        )  # به دلخواه شما
        for item in items:
            writer.writerow(treeview.item(item)["values"])

    messagebox.showinfo("موفقیت", "خروجی CSV با موفقیت انجام شد")
    show_all_btn.focus_set()

    


# تابع برای وارد کردن داده‌ها از فایل CSV به دیتابیس تامین‌کنندگان
def import_supplier_from_csv(treeview):
    file_path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv")], title="انتخاب فایل CSV"
    )
    if not file_path:
        return

    # اتصال به پایگاه داده و وارد کردن داده‌ها
    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    cursor.execute("USE inventory_system")
    imported, skipped = 0, 0

    with open(file_path, "r", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        next(reader)  # برای رد کردن هدر

        for row in reader:
            if len(row) < 4:
                skipped += 1
                continue

            invoice = row[0]
            cursor.execute(
                "SELECT invoice FROM supplier_data WHERE invoice = %s", (invoice,)
            )
            if cursor.fetchone():
                skipped += 1
                continue

            cursor.execute(
                "INSERT INTO supplier_data (invoice, name, contact, description) VALUES (%s, %s, %s, %s)",
                tuple(row),
            )
            imported += 1

    connection.commit()
    cursor.close()
    connection.close()

    treeview_data(treeview)
    messagebox.showinfo("نتیجه", f"وارد شده: {imported}\nرد شده: {skipped}")


def fetch_supplier_search_values(invoice_cb, name_cb, contact_cb):
    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    cursor.execute("USE inventory_system")
    cursor.execute("SELECT invoice, name, contact FROM supplier_data")
    rows = cursor.fetchall()

    invoices = ["همه"]
    names = ["همه"]
    contacts = ["همه"]

    for inv, nm, ct in rows:
        if str(inv) not in invoices:
            invoices.append(str(inv))
        if nm not in names:
            names.append(nm)
        if ct not in contacts:
            contacts.append(ct)

    invoice_cb.config(values=invoices)
    name_cb.config(values=names)
    contact_cb.config(values=contacts)

    cursor.close()
    connection.close()


def search_supplier_multi(invoice, name, contact, treeview):
    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    query = "SELECT * FROM supplier_data WHERE 1=1"
    params = []

    if invoice and invoice != "همه":
        query += " AND invoice = %s"
        params.append(invoice)

    if name and name != "همه":
        query += " AND name LIKE %s"
        params.append(f"%{name}%")

    if contact and contact != "همه":
        query += " AND contact LIKE %s"
        params.append(f"%{contact}%")

    cursor.execute("USE inventory_system")
    cursor.execute(query, tuple(params))
    records = cursor.fetchall()

    treeview.delete(*treeview.get_children())
    for record in records:
        treeview.insert("", END, values=record)

    cursor.close()
    connection.close()


def delete_supplier(
    invoice, treeview, search_invoice_cb, search_name_cb, search_contact_cb
):
    index = treeview.selection()
    if not index:
        messagebox.showerror("خطا", "هیچ ردیفی انتخاب نشده است")
        return
    cursor, connection = connect_database()
    if not cursor or not connection:
        return
    try:
        cursor.execute("use inventory_system")
        cursor.execute(" DELETE FROM supplier_data WHERE invoice=%s", (invoice,))
        connection.commit()
        treeview_data(treeview)
        # به‌روزرسانی لیست‌های جستجو
        fetch_supplier_search_values(
            search_invoice_cb, search_name_cb, search_contact_cb
        )
        messagebox.showinfo("اطلاعات", "ردیف انتخاب شده حذف شد")
    except Exception as e:
        messagebox.showerror("خطا", f"خطا به دلیل {e}")
    finally:
        cursor.close()
        connection.close()


def clear(invoice_entry, name_entry, contact_entry, description_text, treeview):
    invoice_entry.delete(0, END)
    name_entry.delete(0, END)
    contact_entry.delete(0, END)
    description_text.delete(1.0, END)
    treeview.selection_remove(treeview.selection())


def search_supplier(search_value, treeview):
    if search_value == "":
        messagebox.showerror("خطا", "لطفا شناسه تامین کننده را وارد کنید")
    else:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
    try:
        cursor.execute("use inventory_system")
        cursor.execute(" SELECT * from supplier_data WHERE invoice=%s", (search_value,))
        record = cursor.fetchone()
        if not record:
            messagebox.showerror("خطا", "اطلاعاتی پیدا نشد!")
            return

        treeview.delete(*treeview.get_children())
        treeview.insert("", END, values=record)
    except Exception as e:
        messagebox.showerror("خطا", f"خطا به دلیل {e}")
    finally:
        cursor.close()
        connection.close()


def show_all(treeview, search_entry):
    treeview_data(treeview)
    search_entry.delete(0, END)


def update_supplier(
    invoice,
    name,
    contact,
    description,
    treeview,
    search_invoice_cb,
    search_name_cb,
    search_contact_cb,
):
    index = treeview.selection()
    if not index:
        messagebox.showerror("خطا", "هیچ ردیفی انتخاب نشده است")
        return
    # بررسی اینکه آیا شماره شناسه تامین کننده در ورودی خالی است یا خیر
    if not invoice:
        messagebox.showerror(
            "خطا",
            "شناسه تامین کننده قابل تغییر نیست. لطفاً برای ویرایش اطلاعات دیگر از این ردیف استفاده کنید.",
        )
        return

    try:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        cursor.execute("use inventory_system")

        # بررسی وجود شماره شناسه تامین کننده در دیتابیس
        cursor.execute(" SELECT * from supplier_data WHERE invoice=%s", (invoice,))
        current_data = cursor.fetchone()

        if not current_data:
            messagebox.showerror("خطا", "شناسه تامین کننده قابل تغییر نیست!")
            return

        current_data = current_data[1:]

        new_data = (name, contact, description)

        if current_data == new_data:
            messagebox.showinfo("اطلاعات", "تغییری در اطلاعات ایجاد نشده است")
            return

        cursor.execute(
            " UPDATE supplier_data SET name=%s,contact=%s,description=%s WHERE invoice=%s",
            (name, contact, description, invoice),
        )
        connection.commit()
        messagebox.showinfo("اطلاعات", "اطلاعات به روز رسانی شد")
        treeview_data(treeview)
        # به‌روزرسانی لیست‌های جستجو
        fetch_supplier_search_values(
            search_invoice_cb, search_name_cb, search_contact_cb
        )
    except Exception as e:
        messagebox.showerror("خطا", f"خطا به دلیل {e}")
    finally:
        cursor.close()
        connection.close()


def select_data(
    event, invoice_entry, name_entry, contact_entry, description_text, treeview
):
    index = treeview.selection()
    content = treeview.item(index)
    actual_content = content["values"]
    invoice_entry.delete(0, END)
    name_entry.delete(0, END)
    contact_entry.delete(0, END)
    description_text.delete(1.0, END)
    invoice_entry.insert(0, actual_content[0])
    name_entry.insert(0, actual_content[1])
    contact_entry.insert(0, actual_content[2])
    description_text.insert(1.0, actual_content[3])


def treeview_data(treeview):
    cursor, connection = connect_database()
    if not cursor or not connection:
        return
    try:
        cursor.execute("USE inventory_system")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS supplier_data (invoice INT PRIMARY KEY,name VARCHAR(100),"
            "contact VARCHAR(15), description TEXT)"
        )
        cursor.execute("Select * from supplier_data")
        records = cursor.fetchall()
        treeview.delete(*treeview.get_children())
        for record in records:
            treeview.insert("", END, values=record)
    except Exception as e:
        messagebox.showerror("خطا", f"خطا به دلیل {e}")
    finally:
        cursor.close()
        connection.close()


def add_supplier(
    invoice,
    name,
    contact,
    description,
    treeview,
    search_invoice_cb,
    search_name_cb,
    search_contact_cb,
):
    if invoice == "" or name == "" or contact == "" or description == "":
        messagebox.showerror("خطا", "پر کردن تمام فیلدها الزامیست")
    else:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        try:
            cursor.execute("Use inventory_system")

            cursor.execute("Select * from supplier_data where invoice=%s", (invoice,))
            if cursor.fetchone():
                messagebox.showerror("خطا", "شناسه تامین کننده تکراری است")
                return

            cursor.execute(
                "INSERT INTO supplier_data VALUES(%s,%s,%s,%s)",
                (invoice, name, contact, description),
            )
            connection.commit()
            messagebox.showinfo("اطلاعات", " با موفقیت وارد شد")
            treeview_data(treeview)
            # به‌روزرسانی لیست‌های جستجو
            fetch_supplier_search_values(
                search_invoice_cb, search_name_cb, search_contact_cb
            )
        except Exception as e:
            messagebox.showerror("خطا", f"خطا به دلیل {e}")
        finally:
            cursor.close()
            connection.close()


def supplier_form(window):
    global back_image

    supplier_frame = Frame(
        window,
        width=window.winfo_width() - 200,
        height=window.winfo_height(),
        bg="white",
    )
    supplier_frame.place(x=0, y=100)  # تنظیم موقعیت فرم در سمت چپ صفحه
    heading_label = Label(
        supplier_frame,
        text="مدیریت تامین کنندگان",
        font=("fonts/Persian-Yekan.ttf", 18, "bold"),
        bg="#00198f",
        fg="white",
    )
    heading_label.place(x=0, y=0, relwidth=1)

    back_image = PhotoImage(file="images/back_button.png")
    Button(
        supplier_frame,
        image=back_image,
        bd=0,
        cursor="hand2",
        bg="white",
        command=lambda: supplier_frame.place_forget(),
    ).place(x=10, y=45)

    # ==================== سرچ + جدول سمت چپ (قبلاً سمت راست) ====================
    left_frame = Frame(supplier_frame, bg="white")
    left_frame.place(x=60, y=105, width=600, height=480)

    # ---------- سرچ ----------
    search_frame = Frame(left_frame, bg="white", bd=1, relief=SOLID)
    search_frame.pack(fill=X, padx=5, pady=(5, 10))

    label_font = ("fonts/Persian-Yekan.ttf", 12, "bold")
    entry_font = ("fonts/Persian-Yekan.ttf", 14)

    Label(search_frame, text="شناسه تامین کننده", font=label_font, bg="white").grid(
        row=0, column=0, padx=10, sticky="w"
    )
    Label(search_frame, text="نام تأمین‌کننده", font=label_font, bg="white").grid(
        row=0, column=1, padx=10, sticky="w"
    )
    Label(search_frame, text="شماره تماس", font=label_font, bg="white").grid(
        row=0, column=2, padx=10, sticky="w"
    )
    cb_font = ("fonts/Persian-Yekan.ttf", 11)
    search_invoice = ttk.Combobox(
        search_frame, font=cb_font, width=11, state="readonly",takefocus=True
    )
    search_invoice.grid(row=1, column=0, padx=10, pady=5)
    search_invoice.set("همه")
    search_name = ttk.Combobox(search_frame, font=cb_font, width=11, state="readonly",takefocus=True)
    search_name.grid(row=1, column=1, padx=10, pady=5)
    search_name.set("همه")

    search_contact = ttk.Combobox(
        search_frame, font=cb_font, width=11, state="readonly",takefocus=True
    )
    search_contact.grid(row=1, column=2, padx=10, pady=5)
    search_contact.set("همه")

    search_btn = Button(
    search_frame,
    text="جستجو",
    font=("fonts/Persian-Yekan.ttf", 11),
    fg="white",
    bg="#00198f",
    width=8,
    takefocus=True,
    command=lambda: search_supplier_multi(
        search_invoice.get(), search_name.get(), search_contact.get(), treeview
    ),
)
    search_btn.grid(row=1, column=3, padx=10)

    show_all_btn = Button(
    search_frame,
    text="نمایش همه",
    font=("fonts/Persian-Yekan.ttf", 11),
    fg="white",
    bg="#7a7a7a",
    width=8,
    takefocus=True,
    command=lambda: treeview_data(treeview),
)
    show_all_btn.grid(row=1, column=4, padx=5)


    # ---------- جدول ----------
    table_frame = Frame(left_frame, bg="white")
    table_frame.pack(fill=BOTH, expand=1)

    scrolly = Scrollbar(table_frame, orient=VERTICAL)
    scrollx = Scrollbar(table_frame, orient=HORIZONTAL)

    treeview = ttk.Treeview(
        table_frame,
        columns=("invoice", "name", "contact", "description"),
        show="headings",
        yscrollcommand=scrolly.set,
        xscrollcommand=scrollx.set,
    )
    scrolly.pack(side=RIGHT, fill=Y)
    scrollx.pack(side=BOTTOM, fill=X)
    scrollx.config(command=treeview.xview)
    scrolly.config(command=treeview.yview)
    treeview.pack(fill=BOTH, expand=1)

    treeview.heading("invoice", text="شناسه تامین کننده")
    treeview.heading("name", text="نام تامین کننده")
    treeview.heading("contact", text="شماره تماس")
    treeview.heading("description", text="توضیحات")

    treeview_data(treeview)

    fetch_supplier_search_values(search_invoice, search_name, search_contact)

    # ==================== فرم سمت راست (قبلاً سمت چپ) ====================
    right_frame = Frame(supplier_frame, bg="white")
    right_frame.place(x=820, y=150)


    # برچسب‌ها در سمت راست و فیلدهای ورودی در سمت چپ
    Label(
        right_frame,
        text="شناسه تامین کننده",
        font=("fonts/Persian-Yekan.ttf", 14, "bold"),
        bg="white",
    ).grid(
        row=0, column=1, padx=(40, 20), sticky="e"
    )  # تغییر به ستون 1 و sticky="e"
    invoice_entry = Entry(
        right_frame, font=("fonts/Persian-Yekan.ttf", 16, "bold"), bg="lightblue"
    )
    invoice_entry.grid(row=0, column=0, padx=(20, 40))  # تغییر به ستون 0

    Label(
        right_frame,
        text="نام تامین کننده",
        font=("fonts/Persian-Yekan.ttf", 14, "bold"),
        bg="white",
    ).grid(
        row=1, column=1, padx=(40, 20), pady=25, sticky="e"
    )  # تغییر به ستون 1 و sticky="e"
    name_entry = Entry(
        right_frame, font=("fonts/Persian-Yekan.ttf", 16, "bold"), bg="lightblue"
    )
    name_entry.grid(row=1, column=0, padx=(20, 40))  # تغییر به ستون 0

    Label(
        right_frame,
        text="شماره تماس",
        font=("fonts/Persian-Yekan.ttf", 14, "bold"),
        bg="white",
    ).grid(
        row=2, column=1, padx=(40, 20), sticky="e"
    )  # تغییر به ستون 1 و sticky="e"
    contact_entry = Entry(
        right_frame, font=("fonts/Persian-Yekan.ttf", 16, "bold"), bg="lightblue"
    )
    contact_entry.grid(row=2, column=0, padx=(20, 40))  # تغییر به ستون 0

    Label(
        right_frame,
        text="توضیحات",
        font=("fonts/Persian-Yekan.ttf", 14, "bold"),
        bg="white",
    ).grid(
        row=3, column=1, padx=(40, 20), sticky="ne", pady=25
    )  # تغییر به ستون 1 و sticky="ne"
    description_text = Text(right_frame, width=30, height=6, bg="lightblue")
    description_text.grid(row=3, column=0, padx=(20, 40), pady=25)  # تغییر به ستون 0

    button_frame = Frame(right_frame, bg="white")
    button_frame.grid(row=4, column=0, columnspan=2, pady=20)
    right_frame.grid_columnconfigure(0, weight=1)
    right_frame.grid_columnconfigure(1, weight=1)


    Button(
        button_frame,
        text="افزودن",
        font=("fonts/Persian-Yekan.ttf", 12),
        width=8,
        fg="white",
        bg="#00198f",
        command=lambda: (
    add_supplier(
        invoice_entry.get(),
        name_entry.get(),
        contact_entry.get(),
        description_text.get(1.0, END).strip(),
        treeview,
        search_invoice,
        search_name,
        search_contact,
    ),
    clear(
        invoice_entry,
        name_entry,
        contact_entry,
        description_text,
        treeview,
    ),
)
    ).grid(row=0, column=0, padx=20)

    Button(
        button_frame,
        text="به روزرسانی",
        font=("fonts/Persian-Yekan.ttf", 12),
        width=8,
        fg="white",
        bg="#00198f",
        command=lambda: update_supplier(
            invoice_entry.get(),
            name_entry.get(),
            contact_entry.get(),
            description_text.get(1.0, END).strip(),
            treeview,
            search_invoice,
            search_name,
            search_contact,
        ),
    ).grid(row=0, column=1)

    Button(
        button_frame,
        text="حذف",
        font=("fonts/Persian-Yekan.ttf", 12),
        width=8,
        fg="white",
        bg="#00198f",
        command=lambda: (
    delete_supplier(
        invoice_entry.get(),
        treeview,
        search_invoice,
        search_name,
        search_contact,
    ),
    clear(
        invoice_entry,
        name_entry,
        contact_entry,
        description_text,
        treeview,
    ),
)
    ).grid(row=0, column=2, padx=20)

    Button(
        button_frame,
        text="پاک کردن",
        font=("fonts/Persian-Yekan.ttf", 12),
        width=8,
        fg="white",
        bg="#00198f",
        command=lambda: clear(
            invoice_entry, name_entry, contact_entry, description_text, treeview
        ),
    ).grid(row=0, column=3)

    # ===== رفع گیر کردن Tab در Text توضیحات =====

    def description_tab_to_button(event):
    # فوکوس بره روی اولین دکمه (افزودن)
        button_frame.children[list(button_frame.children)[0]].focus_set()
        return "break"

    description_text.bind("<Tab>", description_tab_to_button)


    import_export_frame = Frame(button_frame, bg="white")
    import_export_frame.grid(row=1, column=0, columnspan=4, pady=(10, 10), sticky="ew")
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)
    button_frame.grid_columnconfigure(2, weight=1)
    button_frame.grid_columnconfigure(3, weight=1)


    # دکمه اکسپورت
    export_button = Button(
        import_export_frame,
        text="📊 خروجی CSV",
        font=("fonts/Persian-Yekan.ttf", 11),
        width=18,
        fg="white",
        bg="#4b39e9",
        command=lambda: export_supplier_to_csv(treeview),
    )
    export_button.pack(side=LEFT, padx=14)

    # دکمه ایمپورت
    import_button = Button(
        import_export_frame,
        text="📥 وارد کردن CSV",
        font=("fonts/Persian-Yekan.ttf", 11),
        width=18,
        fg="white",
        bg="#4b39e9",
        command=lambda: import_supplier_from_csv(treeview),
    )
    import_button.pack(side=LEFT, padx=14)

    # اتصال رویداد انتخاب از جدول
    treeview.bind(
        "<ButtonRelease-1>",
        lambda e: select_data(
            e, invoice_entry, name_entry, contact_entry, description_text, treeview
        ),
    )
    # ========= Tab Order کل صفحه =========

# فوکوس اولیه
    invoice_entry.focus_set()

# بعد از آخرین دکمه فرم → سرچ
    button_frame.children[list(button_frame.children)[-1]].bind(
    "<Tab>",
    lambda e: (search_invoice.focus_set(), "break")
)

# بعد از نمایش همه → برگرد اول فرم
    show_all_btn.bind(
    "<Tab>",
    lambda e: (invoice_entry.focus_set(), "break")
)

    # ================== میانبرهای صفحه تامین‌کنندگان ==================

    def shortcut_add(event=None):
        add_supplier(
        invoice_entry.get(),
        name_entry.get(),
        contact_entry.get(),
        description_text.get(1.0, END).strip(),
        treeview,
        search_invoice,
        search_name,
        search_contact,
    )

    def shortcut_update(event=None):
        update_supplier(
        invoice_entry.get(),
        name_entry.get(),
        contact_entry.get(),
        description_text.get(1.0, END).strip(),
        treeview,
        search_invoice,
        search_name,
        search_contact,
    )

    def shortcut_delete(event=None):
        delete_supplier(
        invoice_entry.get(), treeview, search_invoice, search_name, search_contact
    )

    def shortcut_clear(event=None):
        clear(invoice_entry, name_entry, contact_entry, description_text, treeview)

    def shortcut_search(event=None):
        search_supplier_multi(
        search_invoice.get(), search_name.get(), search_contact.get(), treeview
    )
        
    def shortcut_import(event=None): 
        import_supplier_from_csv(treeview) 
     
    def shortcut_export(event=None): 
        export_supplier_to_csv(treeview) 
     
    window.bind("<Control-a>", shortcut_add)      # افزودن 
    window.bind("<Control-u>", shortcut_update)   # ویرایش 
    window.bind("<Control-d>", shortcut_delete)   # حذف 
    window.bind("<Control-c>", shortcut_clear)    # پاک کردن 
    window.bind("<Control-s>", shortcut_search)   # جستجو 
    window.bind("<Control-n>", lambda e: treeview_data(treeview))  # نمایش همه

    # میانبرهای اضافه شده از کد category.py 
    window.bind("<Control-i>", shortcut_import)   # وارد کردن CSV 
    window.bind("<Control-I>", shortcut_import)   # وارد کردن CSV 
    window.bind("<Control-e>", shortcut_export)   # خروجی CSV 
    window.bind("<Control-E>", shortcut_export)   # خروجی CSV 
     
    window.bind("<Escape>", lambda e: supplier_frame.place_forget())  # خروج فرم




