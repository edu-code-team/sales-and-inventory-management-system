from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from employees import connect_database


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

    if invoice != "" and invoice != "همه":
        query += " AND invoice=%s"
    params.append(invoice)

    if name != "" and name != "همه":
        query += " AND name LIKE %s"
    params.append(f"%{name}%")

    if contact != "" and contact != "همه":
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


def delete_supplier(invoice, treeview):
    index = treeview.selection()
    if not index:
        messagebox.showerror("خطا", "هیچ ردیفی انتخاب نشده است")
        return
    cursor, connection = connect_database()
    if not cursor or not connection:
        return
    try:
        cursor.execute("use inventory_system")
        cursor.execute(" DELETE FROM supplier_data WHERE invoice=%s", invoice)
        connection.commit()
        treeview_data(treeview)
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
        messagebox.showerror("خطا", "لطفا شماره فاکتور را وارد کنید")
    else:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
    try:
        cursor.execute("use inventory_system")
        cursor.execute(" SELECT * from supplier_data WHERE invoice=%s", search_value)
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


def update_supplier(invoice, name, contact, description, treeview):
    index = treeview.selection()
    if not index:
        messagebox.showerror("خطا", "هیچ ردیفی انتخاب نشده است")
        return
    try:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        cursor.execute("use inventory_system")
        cursor.execute(" SELECT * from supplier_data WHERE invoice=%s", invoice)
        current_data = cursor.fetchone()
        current_data = current_data[1:]

        new_data = (name, contact, description)

        if current_data == new_data:
            messagebox.showinfo("اطلاعات", " تغییرات را اعمال کنید")
            return

        cursor.execute(
            " UPDATE supplier_data SET name=%s,contact=%s,description=%s WHERE invoice=%s",
            (name, contact, description, invoice),
        )
        connection.commit()
        messagebox.showinfo("اطلاعات", "اطلاعات به روز رسانی شد")
        treeview_data(treeview)
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


def add_supplier(invoice, name, contact, description, treeview):
    if invoice == "" or name == "" or contact == "" or description == "":
        messagebox.showerror("خطا", "پر کردن تمام فیلدها الزامیست")
    else:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        try:
            cursor.execute("Use inventory_system")

            cursor.execute("Select * from supplier_data where invoice=%s", invoice)
            if cursor.fetchone():
                messagebox.showerror("خطا", "شماره فاکتور تکراری است")
                return

            cursor.execute(
                "INSERT INTO supplier_data VALUES(%s,%s,%s,%s)",
                (invoice, name, contact, description),
            )
            connection.commit()
            messagebox.showinfo("اطلاعات", " با موفقیت وارد شد")
            treeview_data(treeview)
        except Exception as e:
            messagebox.showerror("خطا", f"خطا به دلیل {e}")
        finally:
            cursor.close()
            connection.close()


def supplier_form(window):
    global back_image

    supplier_frame = Frame(window, width=1165, height=567, bg="white")
    supplier_frame.place(x=200, y=100)

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

    # ==================== فرم سمت چپ ====================
    left_frame = Frame(supplier_frame, bg="white")
    left_frame.place(x=10, y=100)

    Label(
        left_frame,
        text="شماره فاکتور",
        font=("fonts/Persian-Yekan.ttf", 14, "bold"),
        bg="white",
    ).grid(row=0, column=0, padx=(20, 40), sticky="w")
    invoice_entry = Entry(
        left_frame, font=("fonts/Persian-Yekan.ttf", 16, "bold"), bg="lightblue"
    )
    invoice_entry.grid(row=0, column=1)

    Label(
        left_frame,
        text="نام تامین کننده",
        font=("fonts/Persian-Yekan.ttf", 14, "bold"),
        bg="white",
    ).grid(row=1, column=0, padx=(20, 40), pady=25, sticky="w")
    name_entry = Entry(
        left_frame, font=("fonts/Persian-Yekan.ttf", 16, "bold"), bg="lightblue"
    )
    name_entry.grid(row=1, column=1)

    Label(
        left_frame,
        text="شماره تماس",
        font=("fonts/Persian-Yekan.ttf", 14, "bold"),
        bg="white",
    ).grid(row=2, column=0, padx=(20, 40), sticky="w")
    contact_entry = Entry(
        left_frame, font=("fonts/Persian-Yekan.ttf", 16, "bold"), bg="lightblue"
    )
    contact_entry.grid(row=2, column=1)

    Label(
        left_frame,
        text="توضیحات",
        font=("fonts/Persian-Yekan.ttf", 14, "bold"),
        bg="white",
    ).grid(row=3, column=0, padx=(20, 40), sticky="nw", pady=25)
    description_text = Text(left_frame, width=30, height=6, bg="lightblue")
    description_text.grid(row=3, column=1, pady=25)

    button_frame = Frame(left_frame, bg="white")
    button_frame.grid(row=4, columnspan=2, pady=20)

    Button(
        button_frame,
        text="افزودن",
        font=("fonts/Persian-Yekan.ttf", 12),
        width=8,
        fg="white",
        bg="#00198f",
        command=lambda: add_supplier(
            invoice_entry.get(),
            name_entry.get(),
            contact_entry.get(),
            description_text.get(1.0, END).strip(),
            treeview,
        ),
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
        ),
    ).grid(row=0, column=1)

    Button(
        button_frame,
        text="حذف",
        font=("fonts/Persian-Yekan.ttf", 12),
        width=8,
        fg="white",
        bg="#00198f",
        command=lambda: delete_supplier(invoice_entry.get(), treeview),
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

    # ==================== سرچ + جدول سمت راست ====================
    right_frame = Frame(supplier_frame, bg="white")
    right_frame.place(x=520, y=100, width=600, height=430)

    # ---------- سرچ ----------
    search_frame = Frame(right_frame, bg="white", bd=1, relief=SOLID)
    search_frame.pack(fill=X, padx=5, pady=(5, 10))

    label_font = ("fonts/Persian-Yekan.ttf", 12, "bold")
    entry_font = ("fonts/Persian-Yekan.ttf", 14)

    Label(search_frame, text="شماره فاکتور", font=label_font, bg="white").grid(
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
        search_frame, font=cb_font, width=11, state="readonly"
    )
    search_invoice.grid(row=1, column=0, padx=10, pady=5)
    search_invoice.set("همه")
    search_name = ttk.Combobox(search_frame, font=cb_font, width=11, state="readonly")
    search_name.grid(row=1, column=1, padx=10, pady=5)
    search_name.set("همه")

    search_contact = ttk.Combobox(
        search_frame, font=cb_font, width=11, state="readonly"
    )
    search_contact.grid(row=1, column=2, padx=10, pady=5)
    search_contact.set("همه")

    Button(
        search_frame,
        text="جستجو",
        font=("fonts/Persian-Yekan.ttf", 11),
        fg="white",
        bg="#00198f",
        width=8,
        command=lambda: search_supplier_multi(
            search_invoice.get(), search_name.get(), search_contact.get(), treeview
        ),
    ).grid(row=1, column=3, padx=10)

    Button(
        search_frame,
        text="نمایش همه",
        font=("fonts/Persian-Yekan.ttf", 11),
        fg="white",
        bg="#7a7a7a",
        width=8,
        command=lambda: treeview_data(treeview),
    ).grid(row=1, column=4, padx=5)

    fetch_supplier_search_values(search_invoice, search_name, search_contact)

    # ---------- جدول ----------
    table_frame = Frame(right_frame, bg="white")
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

    treeview.heading("invoice", text="شماره فاکتور")
    treeview.heading("name", text="نام تامین کننده")
    treeview.heading("contact", text="شماره تماس")
    treeview.heading("description", text="توضیحات")

    treeview_data(treeview)
    treeview.bind(
        "<ButtonRelease-1>",
        lambda e: select_data(
            e, invoice_entry, name_entry, contact_entry, description_text, treeview
        ),
    )
