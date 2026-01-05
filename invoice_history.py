from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime
import jdatetime
from database import connect_database
from tkinter import filedialog
import csv


def move_focus(widget):
    widget.focus_set()
    return "break"

def validate_phone_input(value):
    # اجازه پاک کردن کامل
    if value == "":
        return True

    # فقط عدد
    if not value.isdigit():
        messagebox.showerror(
            "خطای ورودی",
            "❌ شماره تماس باید فقط شامل عدد باشد"
        )
        return False

    # بیشتر از 11 رقم نشود
    if len(value) > 11:
        messagebox.showerror(
            "خطای ورودی",
            "❌ شماره تماس باید دقیقاً ۱۱ رقم باشد"
        )
        return False

    return True

def load_invoice_history(
    treeview, date_filter=None, invoice_filter=None, customer_filter=None
):
    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute("USE inventory_system")

        query = """
            SELECT invoice_number, customer_name, customer_phone, 
                   total_amount, invoice_date, items_count,
                   DATE_FORMAT(created_at, '%%H:%%i:%%s') as invoice_time
            FROM invoice_history
            WHERE 1=1
        """
        params = []

        if date_filter and date_filter != "همه":
            query += " AND invoice_date = %s"
            params.append(date_filter)

        if invoice_filter and invoice_filter != "همه":
            query += " AND invoice_number = %s"
            params.append(invoice_filter)

        if customer_filter and customer_filter != "همه":
            query += " AND customer_name LIKE %s"
            params.append(f"%{customer_filter}%")

        query += " ORDER BY invoice_number DESC"

        cursor.execute(query, tuple(params))
        invoices = cursor.fetchall()

        treeview.delete(*treeview.get_children())

        for invoice in invoices:
            treeview.insert(
                "",
                END,
                values=(
                    invoice[0],  # شماره فاکتور
                    invoice[1],  # نام مشتری
                    invoice[2],  # شماره تماس
                    f"{invoice[3]:,.0f}",  # مبلغ کل
                    invoice[4],  # تاریخ
                    invoice[5],  # تعداد آیتم‌ها
                    invoice[6],  # زمان
                ),
            )

    except Exception as e:
        messagebox.showerror("خطا", f"خطا در بارگذاری تاریخچه: {str(e)}")
    finally:
        cursor.close()
        connection.close()


def load_filters(date_filter_cb, invoice_filter_cb, customer_filter_cb):
    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute("USE inventory_system")

        # بارگذاری تاریخ‌ها
        cursor.execute(
            "SELECT DISTINCT invoice_date FROM invoice_history ORDER BY invoice_date DESC"
        )
        dates = ["همه"] + [date[0] for date in cursor.fetchall()]
        date_filter_cb["values"] = dates[:20]  # فقط 20 تاریخ آخر
        date_filter_cb.set("همه")

        # بارگذاری شماره فاکتورها
        cursor.execute(
            "SELECT DISTINCT invoice_number FROM invoice_history ORDER BY invoice_number DESC"
        )
        invoices = ["همه"] + [str(inv[0]) for inv in cursor.fetchall()]
        invoice_filter_cb["values"] = invoices[:50]  # فقط 50 فاکتور آخر
        invoice_filter_cb.set("همه")

        # بارگذاری نام مشتریان
        cursor.execute(
            "SELECT DISTINCT customer_name FROM invoice_history ORDER BY customer_name"
        )
        customers = ["همه"] + [cust[0] for cust in cursor.fetchall()]
        customer_filter_cb["values"] = customers[:50]  # فقط 50 مشتری
        customer_filter_cb.set("همه")

    except Exception as e:
        print(f"خطا در بارگذاری فیلترها: {e}")
        date_filter_cb["values"] = ["همه"]
        invoice_filter_cb["values"] = ["همه"]
        customer_filter_cb["values"] = ["همه"]
    finally:
        cursor.close()
        connection.close()


def show_invoice_details(event, treeview):
    selected = treeview.selection()
    if not selected:
        return

    item = treeview.item(selected[0])
    invoice_number = item["values"][0]

    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute("USE inventory_system")

        # اطلاعات فاکتور اصلی
        cursor.execute(
            """
            SELECT customer_name, customer_phone, total_amount, invoice_date
            FROM invoice_history 
            WHERE invoice_number = %s
        """,
            (invoice_number,),
        )

        invoice_info = cursor.fetchone()
        if not invoice_info:
            messagebox.showerror("خطا", "فاکتور پیدا نشد")
            return

        # آیتم‌های فاکتور
        cursor.execute(
            """
            SELECT product_name, price, quantity, total
            FROM invoice_items
            WHERE invoice_number = %s
            ORDER BY id
        """,
            (invoice_number,),
        )

        items = cursor.fetchall()

        # ایجاد پنجره جزئیات
        show_invoice_detail_window(invoice_number, invoice_info, items)

    except Exception as e:
        messagebox.showerror("خطا", f"خطا در نمایش جزئیات: {str(e)}")
    finally:
        cursor.close()
        connection.close()


def show_invoice_detail_window(invoice_number, invoice_info, items):
    detail_window = Toplevel()
    detail_window.title(f"جزئیات فاکتور شماره {invoice_number}")
    detail_window.geometry("650x550")
    detail_window.configure(bg="white")
    detail_window.resizable(False, False)

    # فریم اصلی
    main_frame = Frame(detail_window, bg="white")
    main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

    # مرکز کردن پنجره
    detail_window.update_idletasks()
    width = 650
    height = 550
    x = (detail_window.winfo_screenwidth() // 2) - (width // 2)
    y = (detail_window.winfo_screenheight() // 2) - (height // 2)
    detail_window.geometry(f"{width}x{height}+{x}+{y}")

    # عنوان (راست‌چین)
    title_label = Label(
        main_frame,
        text=f"📄 فاکتور شماره {invoice_number}",
        font=("fonts/Persian-Yekan.ttf", 16, "bold"),
        bg="white",
        fg="#00198f",
        anchor="e",
    )
    title_label.pack(fill=X, pady=(0, 20))

    # اطلاعات فاکتور
    info_frame = Frame(main_frame, bg="white")
    info_frame.pack(fill=X, pady=(0, 20))

    customer_name, customer_phone, total_amount, invoice_date = invoice_info
    # اطلاعات به صورت راست‌چین
    info_data = [
        ("نام مشتری", customer_name),
        ("شماره تماس", customer_phone),
        ("تاریخ فاکتور", invoice_date),
        ("تعداد اقلام", str(len(items))),
    ]

    for label_text, value_text in info_data:
        row_frame = Frame(info_frame, bg="white")
        row_frame.pack(fill=X, pady=5)

        # برچسب (راست‌چین)
        label = Label(
            row_frame,
            text=label_text,
            font=("fonts/Persian-Yekan.ttf", 12, "bold"),
            bg="white",
            anchor="e",
            width=15,
        )
        label.pack(side=RIGHT, padx=(10, 0))
        # مقدار (راست‌چین)
        value = Label(
            row_frame,
            text=value_text,
            font=("fonts/Persian-Yekan.ttf", 12),
            bg="white",
            anchor="e",
        )
        value.pack(side=RIGHT, expand=True)

    # خط جداکننده
    separator1 = Frame(main_frame, height=2, bg="#e0e0e0")
    separator1.pack(fill=X, pady=10)

    # عنوان آیتم‌ها (راست‌چین)
    items_title = Label(
        main_frame,
        text=("اقلام خریداری شده"),
        font=("fonts/Persian-Yekan.ttf", 13, "bold"),
        bg="white",
        anchor="e",
    )
    items_title.pack(fill=X, pady=(0, 10))

    # فریم آیتم‌ها با اسکرول
    items_container = Frame(main_frame, bg="white")
    items_container.pack(fill=BOTH, expand=True, pady=(0, 10))

    # کانوس و اسکرول‌بار
    canvas = Canvas(items_container, bg="white", highlightthickness=0)
    scrollbar = Scrollbar(items_container, orient=VERTICAL, command=canvas.yview)

    scrollable_frame = Frame(canvas, bg="white")

    scrollable_frame.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # هدر جدول
    header_frame = Frame(scrollable_frame, bg="#f0f0f0")
    header_frame.pack(fill=X)

    # هدرهای راست‌چین
    headers = [("نام محصول", "w"), ("قیمت واحد", "e"), ("تعداد", "e"), ("جمع کل", "e")]

    for header_text, anchor_pos in headers:
        header = Label(
            header_frame,
            text=header_text,
            font=("fonts/Persian-Yekan.ttf", 11, "bold"),
            bg="#f0f0f0",
            anchor=anchor_pos,
            width=20,
        )
        header.pack(side=LEFT, fill=X, expand=(header_text == "نام محصول"))
    # آیتم‌های فاکتور
    for item in items:
        product_name, price, quantity, total = item

        item_frame = Frame(scrollable_frame, bg="white")
        item_frame.pack(fill=X, pady=2)

        # نام محصول (چپ‌چین)
        name_label = Label(
            item_frame,
            text=product_name,
            font=("fonts/Persian-Yekan.ttf", 10),
            bg="white",
            anchor="w",
            width=25,
        )
        name_label.pack(side=LEFT, fill=X, expand=True)

        # قیمت (راست‌چین)
        price_label = Label(
            item_frame,
            text=f"{price:,.0f}",
            font=("fonts/Persian-Yekan.ttf", 10),
            bg="white",
            anchor="e",
            width=15,
        )
        price_label.pack(side=LEFT)

        # تعداد (راست‌چین)
        qty_label = Label(
            item_frame,
            text=f"{quantity}",
            font=("fonts/Persian-Yekan.ttf", 10),
            bg="white",
            anchor="e",
            width=10,
        )
        qty_label.pack(side=LEFT)

        # جمع (راست‌چین)
        total_label = Label(
            item_frame,
            text=f"{total:,.0f}",
            font=("fonts/Persian-Yekan.ttf", 10),
            bg="white",
            anchor="e",
            width=15,
        )
        total_label.pack(side=LEFT)

    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)

    # خط جداکننده پایین
    separator2 = Frame(main_frame, height=2, bg="#e0e0e0")
    separator2.pack(fill=X, pady=15)

    # فریم جمع کل
    total_frame = Frame(main_frame, bg="white")
    total_frame.pack(fill=X)
    # برچسب جمع کل (راست‌چین)
    total_label_text = Label(
        total_frame,
        text="مبلغ کل فاکتور:",
        font=("fonts/Persian-Yekan.ttf", 13, "bold"),
        bg="white",
        anchor="e",
    )
    total_label_text.pack(side=RIGHT)

    # مبلغ جمع کل (راست‌چین)
    total_amount_label = Label(
        total_frame,
        text=f"{total_amount:,.0f} تومان",
        font=("fonts/Persian-Yekan.ttf", 14, "bold"),
        bg="white",
        fg="#28a745",
        anchor="e",
    )
    total_amount_label.pack(side=RIGHT, padx=10)

    # دکمه بستن
    button_frame = Frame(main_frame, bg="white")
    button_frame.pack(fill=X, pady=(20, 0))

    close_button = Button(
        button_frame,
        text="بستن (Esc)",
        font=("fonts/Persian-Yekan.ttf", 12),
        bg="#6c757d",
        fg="white",
        width=15,
        height=1,
        bd=0,
        cursor="hand2",
        command=detail_window.destroy,
    )
    close_button.pack()
    # کلید Escape برای بستن پنجره
    detail_window.bind("<Escape>", lambda e: detail_window.destroy())

    # فوکوس روی پنجره
    detail_window.focus_set()


def export_invoice_history(treeview):
    """صدور تاریخچه فاکتور به CSV"""
    try:
        items = treeview.get_children()
        data = []

        for item in items:
            values = treeview.item(item)["values"]
            data.append(values)

        if not data:
            messagebox.showwarning("هشدار", "هیچ فاکتوری برای صدور وجود ندارد")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="ذخیره تاریخچه فاکتور",
        )

        if file_path:
            with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow(
                    [
                        "شماره فاکتور",
                        "نام مشتری",
                        "شماره تماس",
                        "مبلغ کل",
                        "تاریخ",
                        "تعداد اقلام",
                        "زمان",
                    ]
                )
                writer.writerows(data)

            messagebox.showinfo("موفقیت", f"تاریخچه فاکتورها در\n{file_path}\nذخیره شد")

    except Exception as e:
        messagebox.showerror("خطا", f"خطا در صدور فایل: {str(e)}")


def delete_invoice(treeview):
    """حذف فاکتور از تاریخچه"""
    selected = treeview.selection()
    if not selected:
        messagebox.showerror("خطا", "هیچ فاکتوری انتخاب نشده است")
        return

    item = treeview.item(selected[0])
    invoice_number = item["values"][0]

    confirm = messagebox.askyesno(
        "تأیید حذف",
        f"آیا از حذف فاکتور شماره {invoice_number} مطمئن هستید؟\nاین عمل قابل بازگشت نیست!",
    )

    if not confirm:
        return

    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute("USE inventory_system")

        # حذف فاکتور (CASCADE باعث حذف خودکار آیتم‌ها می‌شود)
        cursor.execute(
            "DELETE FROM invoice_history WHERE invoice_number = %s", (invoice_number,)
        )

        connection.commit()
        messagebox.showinfo("موفقیت", f"فاکتور شماره {invoice_number} حذف شد")

        # تازه‌سازی تاریخچه
        load_invoice_history(treeview)

    except Exception as e:
        messagebox.showerror("خطا", f"خطا در حذف فاکتور: {str(e)}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


def invoice_history_form(window):
    history_frame = Frame(
        window,
        width=window.winfo_width() - 200,
        height=window.winfo_height(),
        bg="white",
    )
    history_frame.place(x=0, y=100)

    # هدر فرم - با رفع مشکل فونت
    heading_label = Label(
        history_frame,
        text="📜 تاریخچه فاکتورها",
        font=("fonts/Persian-Yekan.ttf", 12),
        bg="#00198f",
        fg="white",
        anchor="center",
    )
    heading_label.place(x=0, y=0, relwidth=1, height=40)

    # دکمه بازگشت
    try:
        back_image = PhotoImage(file="images/back_button.png")
        back_button = Button(
            history_frame,
            image=back_image,
            bd=0,
            cursor="hand2",
            bg="#00198f",
            activebackground="#00198f",
            command=lambda: history_frame.place_forget(),
        )
        back_button.place(x=10, y=5)
    except:
        back_button = Button(
            history_frame,
            text="← بازگشت",
            font=("B Nazanin", 12),
            bg="#00198f",
            fg="white",
            bd=0,
            cursor="hand2",
            command=lambda: history_frame.place_forget(),
        )
        back_button.place(x=10, y=5)

    # ============ فیلترها ============
    filter_frame = Frame(history_frame, bg="white", bd=1, relief=SOLID)
    filter_frame.place(x=20, y=60, width=1150, height=80)

    # فیلتر تاریخ
    Label(filter_frame, text="تاریخ", font=("B Nazanin", 12), bg="white").place(
        x=1080, y=10
    )

    date_filter = ttk.Combobox(
        filter_frame,
        font=("B Nazanin", 11),
        width=15,
        state="readonly",
        justify="right",
    )
    date_filter.place(x=930, y=10)

    # فیلتر شماره فاکتور
    Label(
        filter_frame,
        text="شماره فاکتور",
        font=("B Nazanin", 12),
        bg="white",
    ).place(x=840, y=10)

    invoice_filter = ttk.Combobox(
        filter_frame,
        font=("B Nazanin", 11),
        width=15,
        state="readonly",
        justify="right",
    )
    invoice_filter.place(x=680, y=10)

    # فیلتر مشتری
    Label(filter_frame, text="مشتری", font=("B Nazanin", 12), bg="white").place(
        x=610, y=10
    )

    customer_filter = ttk.Combobox(
        filter_frame,
        font=("B Nazanin", 11),
        width=15,
        state="readonly",
        justify="right",
    )
    customer_filter.place(x=450, y=10)

    def apply_filter_with_validation():
        phone = customer_filter.get()

        if not validate_phone_11_digits(phone):
            return

        load_invoice_history(
        invoice_treeview,
        date_filter.get(),
        invoice_filter.get(),
        phone,
    )

    apply_filter_button = Button(
    filter_frame,
    text="🔍 اعمال فیلتر",
    font=("B Nazanin", 11),
    bg="#00198f",
    fg="white",
    width=12,
    command=apply_filter_with_validation,
)


    # دکمه نمایش همه
    show_all_button = Button(
        filter_frame,
        text="📋 نمایش همه",
        font=("B Nazanin", 11),
        bg="#6c757d",
        fg="white",
        width=12,
        command=lambda: load_invoice_history(invoice_treeview),
    )
    show_all_button.place(x=100, y=10)

    # بارگذاری فیلترها
    load_filters(date_filter, invoice_filter, customer_filter)

    # ============ جدول تاریخچه ============
    table_frame = Frame(history_frame, bg="white")
    table_frame.place(x=20, y=150, width=1150, height=400)

    # اسکرول بار عمودی (سمت راست)
    scroll_y = Scrollbar(table_frame)
    scroll_y.pack(side=RIGHT, fill=Y)

    # اسکرول بار افقی (پایین)
    scroll_x = Scrollbar(table_frame, orient=HORIZONTAL)
    scroll_x.pack(side=BOTTOM, fill=X)

    # Treeview تاریخچه
    invoice_treeview = ttk.Treeview(
        table_frame,
        columns=("invoice_no", "customer", "phone", "amount", "date", "items", "time"),
        show="headings",
        yscrollcommand=scroll_y.set,
        xscrollcommand=scroll_x.set,
        height=15,
    )
    invoice_treeview.pack(side=LEFT, fill=BOTH, expand=True)

    # اتصال اسکرول‌بارها
    scroll_y.config(command=invoice_treeview.yview)
    scroll_x.config(command=invoice_treeview.xview)

    # تنظیم هدرها
    headers = [
        ("شماره فاکتور", 175),
        ("نام مشتری", 225),
        ("شماره تماس", 175),
        ("مبلغ کل", 190),
        ("تاریخ", 150),
        ("تعداد اقلام", 150),
        ("زمان", 120),
    ]

    for i, (header, width) in enumerate(headers):
        invoice_treeview.heading(f"#{i+1}", text=header)
        invoice_treeview.column(f"#{i+1}", width=width, anchor="center")

    # ============ دکمه‌های عملیات ============

    # ============ دکمه‌های عملیات ============
    button_frame = Frame(history_frame, bg="white")
    button_frame.place(x=20, y=560, width=1150, height=50)

    # فریم برای قرارگیری دکمه‌ها در وسط
    center_frame = Frame(button_frame, bg="white")
    center_frame.place(relx=0.5, rely=0.5, anchor="center")

    # دکمه مشاهده جزئیات (سمت راست در مرکز)
    details_button = Button(
        center_frame,
        text="👁️ مشاهده جزئیات",
        font=("fonts/Persian-Yekan.ttf", 12),
        bg="#00198f",
        fg="white",
        width=18,
        height=1,
        bd=0,
        cursor="hand2",
        command=lambda: show_invoice_details(None, invoice_treeview),
    )
    details_button.pack(side=LEFT, padx=10)

    # دکمه حذف (وسط در مرکز)
    delete_button = Button(
        center_frame,
        text="🗑️ حذف فاکتور",
        font=("fonts/Persian-Yekan.ttf", 12),
        bg="#00198f",
        fg="white",
        width=18,
        height=1,
        bd=0,
        cursor="hand2",
        command=lambda: delete_invoice(invoice_treeview),
    )
    delete_button.pack(side=LEFT, padx=10)

    # دکمه صدور به CSV (سمت چپ در مرکز)
    export_button = Button(
        center_frame,
        text="📥 CSV صدور به ",
        font=("fonts/Persian-Yekan.ttf", 12),
        bg="#00198f",
        fg="white",
        width=18,
        height=1,
        bd=0,
        cursor="hand2",
        command=lambda: export_invoice_history(invoice_treeview),
    )
    export_button.pack(side=LEFT, padx=10)

    # ============ کنترل کیبورد ============

    def filter_shortcut(event=None):
        apply_filter_button.invoke()

    def show_all_shortcut(event=None):
        show_all_button.invoke()

    def details_shortcut(event=None):
        details_button.invoke()

    def delete_shortcut(event=None):
        delete_button.invoke()

    def export_shortcut(event=None):
        export_button.invoke()

    def close_form(event=None):
        history_frame.place_forget()

   # ============ KEYBOARD SHORTCUTS (Invoice History) ============

# فوکوس فیلترها
    window.bind("<Control-d>", lambda e: date_filter.focus_set())
    window.bind("<Control-i>", lambda e: invoice_filter.focus_set())
    window.bind("<Control-n>", lambda e: customer_filter.focus_set())

# اعمال فیلتر
    window.bind("<Control-Return>", lambda e: apply_filter_button.invoke())

# نمایش همه
    window.bind("<Control-r>", lambda e: show_all_button.invoke())

# جدول
    window.bind("<Control-t>", lambda e: invoice_treeview.focus_set())

# عملیات روی فاکتور
    window.bind("<Control-v>", lambda e: details_button.invoke())
    window.bind("<Control-Shift-D>", lambda e: delete_button.invoke())
    window.bind("<Control-e>", lambda e: export_button.invoke())

# خروج
    window.bind("<Escape>", lambda e: history_frame.place_forget())

# ============ TAB ORDER (Invoice History - RTL) ============

    date_filter.focus_set()

    date_filter.bind("<Tab>", lambda e: move_focus(invoice_filter))
    invoice_filter.bind("<Tab>", lambda e: move_focus(customer_filter))
    customer_filter.bind("<Tab>", lambda e: move_focus(show_all_button))

    show_all_button.bind("<Tab>", lambda e: move_focus(invoice_treeview))
    invoice_treeview.bind("<Tab>", lambda e: move_focus(export_button))

    export_button.bind("<Tab>", lambda e: move_focus(delete_button))
    delete_button.bind("<Tab>", lambda e: move_focus(details_button))

    details_button.bind("<Tab>", lambda e: move_focus(date_filter))


    # ============ بارگذاری اولیه ============
    load_invoice_history(invoice_treeview)

    # تنظیم رویداد دابل کلیک روی فاکتورها
    invoice_treeview.bind(
        "<Double-Button-1>", lambda e: show_invoice_details(e, invoice_treeview)
    )

    return history_frame


# تابع برای استفاده در dashboard.py
def show_invoice_history(window):
    invoice_history_form(window)
