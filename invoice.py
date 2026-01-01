from tkinter import *
from tkinter import ttk, messagebox
import jdatetime
from database import connect_database

# ================== UI CONSTANTS ==================
PRIMARY_COLOR = "#00198f"
BG_WHITE = "#ffffff"
BORDER_COLOR = "#dee2e6"
BTN_PRIMARY = "#00198f"
BTN_SUCCESS = "#28a745"
BTN_DANGER = "#dc3545"
BTN_WARNING = "#ffc107"
BTN_INFO = "#17a2b8"


def move_focus(widget):
    widget.focus_set()
    return "break"


def add_to_invoice(cart_treeview, product_id, product_name, price, quantity, total):
    for item in cart_treeview.get_children():
        item_data = cart_treeview.item(item)["values"]
        if item_data[0] == product_id:
            new_quantity = item_data[3] + quantity
            new_total = new_quantity * item_data[2]
            cart_treeview.item(
                item,
                values=(
                    product_id,
                    item_data[1],
                    item_data[2],
                    new_quantity,
                    new_total,
                ),
            )
            update_grand_total(cart_treeview)
            return

    cart_treeview.insert(
        "", END, values=(product_id, product_name, price, quantity, total)
    )
    update_grand_total(cart_treeview)


def remove_from_invoice(cart_treeview):
    selected = cart_treeview.selection()
    if not selected:
        messagebox.showerror("خطا", "هیچ آیتمی برای حذف انتخاب نشده است")
        return

    cart_treeview.delete(selected)
    update_grand_total(cart_treeview)


def update_grand_total(cart_treeview):
    total = 0
    for item in cart_treeview.get_children():
        item_data = cart_treeview.item(item)["values"]
        total += item_data[4]

    for widget in cart_treeview.master.master.winfo_children():
        if isinstance(widget, Label) and "مجموع کل" in widget.cget("text"):
            widget.config(text=f"مجموع کل: {total:,.0f} تومان")
            break


def search_product(search_entry, products_treeview, category_filter, status_filter):
    search_text = search_entry.get().strip()
    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute("USE inventory_system")

        query = """
            SELECT p.id, p.name, p.price, p.quantity, p.status, 
                   c.name as category_name, s.name as supplier_name
            FROM product_data p
            LEFT JOIN category_data c ON p.category = c.name
            LEFT JOIN supplier_data s ON p.supplier = s.name
            WHERE 1=1
        """
        params = []

        if search_text and search_text != "جستجوی محصول...":
            query += " AND (p.name LIKE %s OR p.id LIKE %s)"
            params.extend([f"%{search_text}%", f"%{search_text}%"])

        if category_filter != "همه":
            query += " AND p.category = %s"
            params.append(category_filter)

        if status_filter != "همه":
            query += " AND p.status = %s"
            params.append(status_filter)

        cursor.execute(query, tuple(params))
        products = cursor.fetchall()

        products_treeview.delete(*products_treeview.get_children())

        for product in products:
            products_treeview.insert(
                "",
                END,
                values=(
                    product[0],
                    product[1],
                    f"{product[2]:,.0f}",
                    product[3],
                    product[4],
                ),
            )

    except Exception as e:
        messagebox.showerror("خطا", f"خطا در جستجو: {str(e)}")
    finally:
        cursor.close()
        connection.close()


def load_products_to_treeview(products_treeview):
    """بارگذاری محصولات از دیتابیس به Treeview"""
    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute("USE inventory_system")
        cursor.execute(
            """
            SELECT id, name, price, quantity, status 
            FROM product_data 
            WHERE status = 'فعال'
            ORDER BY name
        """
        )
        products = cursor.fetchall()

        products_treeview.delete(*products_treeview.get_children())

        for product in products:
            products_treeview.insert(
                "",
                END,
                values=(
                    product[0],
                    product[1],
                    f"{product[2]:,.0f}",
                    product[3],
                    product[4],
                ),
            )

    except Exception as e:
        messagebox.showerror("خطا", f"خطا در بارگذاری محصولات: {str(e)}")
    finally:
        cursor.close()
        connection.close()


def load_categories_for_filter(filter_combobox):
    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute("USE inventory_system")
        cursor.execute("SELECT name FROM category_data ORDER BY name")
        categories = ["همه"] + [cat[0] for cat in cursor.fetchall()]
        filter_combobox["values"] = categories
        filter_combobox.set("همه")
    except:
        filter_combobox["values"] = ["همه"]
        filter_combobox.set("همه")
    finally:
        cursor.close()
        connection.close()


def select_product_for_invoice(event, products_treeview, cart_treeview, quantity_entry):
    selected = products_treeview.selection()
    if not selected:
        return

    item = products_treeview.item(selected[0])
    values = item["values"]

    stock = int(values[3])
    if stock <= 0:
        messagebox.showwarning("اخطار", "موجودی این محصول صفر است")
        return

    price = int(values[2].replace(",", ""))
    quantity = 1
    total = price * quantity

    add_to_invoice(cart_treeview, values[0], values[1], price, quantity, total)


def show_invoice_preview(
    customer_name_entry, customer_phone_entry, cart_treeview, window
):
    customer_name = customer_name_entry.get().strip()
    customer_phone = customer_phone_entry.get().strip()

    if not customer_name:
        messagebox.showerror("خطا", "لطفاً نام مشتری را وارد کنید")
        customer_name_entry.focus_set()
        return

    if not customer_phone:
        messagebox.showerror("خطا", "لطفاً شماره تماس مشتری را وارد کنید")
        customer_phone_entry.focus_set()
        return

    cart_items = cart_treeview.get_children()
    if not cart_items:
        messagebox.showerror("خطا", "سبد خرید خالی است")
        return

    total_amount = 0
    invoice_items = []

    for item in cart_items:
        item_data = cart_treeview.item(item)["values"]
        product_id = item_data[0]
        product_name = item_data[1]
        price = item_data[2]
        quantity = item_data[3]
        item_total = item_data[4]

        total_amount += item_total
        invoice_items.append(
            {
                "product_id": product_id,
                "product_name": product_name,
                "price": price,
                "quantity": quantity,
                "total": item_total,
            }
        )

    # نمایش پیش‌نمایش فاکتور
    show_invoice_preview_window(
        customer_name,
        customer_phone,
        total_amount,
        invoice_items,
        cart_treeview,
        customer_name_entry,
        customer_phone_entry,
        window,
    )


def show_invoice_preview_window(
    customer_name,
    customer_phone,
    total_amount,
    invoice_items,
    cart_treeview,
    customer_name_entry,
    customer_phone_entry,
    parent_window,
):
    preview_window = Toplevel(parent_window)
    preview_window.title("پیش‌نمایش فاکتور")
    preview_window.geometry("600x700")
    preview_window.configure(bg="white")
    preview_window.resizable(False, False)

    # مرکز کردن پنجره
    preview_window.update_idletasks()
    width = 600
    height = 700
    x = (preview_window.winfo_screenwidth() // 2) - (width // 2)
    y = (preview_window.winfo_screenheight() // 2) - (height // 2)
    preview_window.geometry(f"{width}x{height}+{x}+{y}")

    # عنوان
    Label(
        preview_window,
        text="📋 پیش‌نمایش فاکتور",
        font=("B Nazanin", 18, "bold"),
        bg="white",
        fg="#00198f",
    ).pack(pady=15)

    # اطلاعات فاکتور
    info_frame = Frame(preview_window, bg="white", padx=20, pady=10)
    info_frame.pack(fill=X)

    jalali_date = jdatetime.datetime.now().strftime("%Y/%m/%d")
    info_texts = [
        f"تاریخ: {jalali_date}",
        f"مشتری: {customer_name}",
        f"شماره تماس: {customer_phone}",
    ]

    for text in info_texts:
        Label(
            info_frame, text=text, font=("B Nazanin", 12), bg="white", anchor="w"
        ).pack(fill=X, pady=3)

    # خط جداکننده
    Label(
        preview_window, text="─" * 50, font=("B Nazanin", 10), bg="white", fg="gray"
    ).pack(pady=8)

    # لیست محصولات
    items_frame = Frame(preview_window, bg="white", padx=20)
    items_frame.pack(fill=BOTH, expand=True)

    # هدر جدول
    header_frame = Frame(items_frame, bg="#f0f0f0", height=30)
    header_frame.pack(fill=X)

    headers = ["نام محصول", "تعداد", "قیمت", "جمع"]
    widths = [250, 80, 100, 100]

    for i, (header, width) in enumerate(zip(headers, widths)):
        Label(
            header_frame,
            text=header,
            font=("B Nazanin", 11, "bold"),
            bg="#f0f0f0",
            width=width // 10,
            anchor="center",
        ).pack(side=LEFT, padx=2)

    # محتوای جدول
    canvas = Canvas(items_frame, bg="white", height=300, highlightthickness=0)
    scrollbar = Scrollbar(items_frame, orient=VERTICAL, command=canvas.yview)
    items_container = Frame(canvas, bg="white")

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.create_window((0, 0), window=items_container, anchor="nw")

    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)

    # اضافه کردن محصولات
    for item in invoice_items:
        item_frame = Frame(items_container, bg="white", height=25)
        item_frame.pack(fill=X, pady=1)

        Label(
            item_frame,
            text=item["product_name"][:30],
            font=("B Nazanin", 10),
            bg="white",
            width=30,
            anchor="w",
        ).pack(side=LEFT, padx=2)
        Label(
            item_frame,
            text=item["quantity"],
            font=("B Nazanin", 10),
            bg="white",
            width=8,
            anchor="center",
        ).pack(side=LEFT, padx=2)
        Label(
            item_frame,
            text=f"{item['price']:,}",
            font=("B Nazanin", 10),
            bg="white",
            width=10,
            anchor="center",
        ).pack(side=LEFT, padx=2)
        Label(
            item_frame,
            text=f"{item['total']:,}",
            font=("B Nazanin", 10),
            bg="white",
            width=10,
            anchor="center",
        ).pack(side=LEFT, padx=2)

    # به‌روزرسانی اسکرول منطقه
    items_container.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    # خط جداکننده
    Label(
        preview_window, text="─" * 50, font=("B Nazanin", 10), bg="white", fg="gray"
    ).pack(pady=8)

    # جمع کل
    total_frame = Frame(preview_window, bg="white", padx=20)
    total_frame.pack(fill=X, pady=10)

    Label(
        total_frame,
        text="مبلغ قابل پرداخت:",
        font=("B Nazanin", 13, "bold"),
        bg="white",
    ).pack(side=RIGHT, padx=(10, 0))

    Label(
        total_frame,
        text=f"{total_amount:,} تومان",
        font=("B Nazanin", 15, "bold"),
        bg="white",
        fg="#28a745",
    ).pack(side=LEFT)

    # دکمه‌های پایین
    button_frame = Frame(preview_window, bg="white", pady=20)
    button_frame.pack()

    def confirm_invoice():
        # نمایش پیام تأیید
        response = messagebox.askyesno(
            "تأیید ثبت فاکتور",
            "آیا از ثبت فاکتور اطمینان دارید؟",
            parent=preview_window,
        )

        if response:  # اگر کاربر "بله" را زد
            save_invoice_to_db(
                customer_name,
                customer_phone,
                total_amount,
                invoice_items,
                cart_treeview,
                customer_name_entry,
                customer_phone_entry,
            )
            preview_window.destroy()
        # اگر "خیر" زد، هیچ کاری نکن (باقی می‌ماند در همین پنجره)

    # دکمه ثبت
    confirm_button = Button(
        button_frame,
        text="✅ ثبت فاکتور",
        font=("B Nazanin", 12, "bold"),
        bg=BTN_SUCCESS,
        fg="white",
        width=15,
        height=1,
        bd=0,
        cursor="hand2",
        command=confirm_invoice,
    )
    confirm_button.pack(side=RIGHT, padx=10)

    # دکمه انصراف
    cancel_button = Button(
        button_frame,
        text="❌ انصراف",
        font=("B Nazanin", 12),
        bg=BTN_DANGER,
        fg="white",
        width=12,
        height=1,
        bd=0,
        cursor="hand2",
        command=preview_window.destroy,
    )
    cancel_button.pack(side=LEFT, padx=10)


def save_invoice_to_db(
    customer_name,
    customer_phone,
    total_amount,
    invoice_items,
    cart_treeview,
    customer_name_entry,
    customer_phone_entry,
):
    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute("USE inventory_system")

        jalali_date = jdatetime.datetime.now().strftime("%Y/%m/%d")

        cursor.execute("SELECT MAX(invoice_number) FROM invoice_history")
        max_invoice = cursor.fetchone()[0]
        invoice_number = (max_invoice or 1000) + 1

        cursor.execute(
            """
            INSERT INTO invoice_history 
            (invoice_number, customer_name, customer_phone, total_amount, invoice_date, items_count)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
            (
                invoice_number,
                customer_name,
                customer_phone,
                total_amount,
                jalali_date,
                len(invoice_items),
            ),
        )

        for item in invoice_items:
            cursor.execute(
                """
                INSERT INTO invoice_items 
                (invoice_number, product_id, product_name, price, quantity, total)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                (
                    invoice_number,
                    item["product_id"],
                    item["product_name"],
                    item["price"],
                    item["quantity"],
                    item["total"],
                ),
            )

            cursor.execute(
                """
                UPDATE product_data 
                SET quantity = quantity - %s 
                WHERE id = %s AND quantity >= %s
            """,
                (item["quantity"], item["product_id"], item["quantity"]),
            )

        connection.commit()

        # پاک کردن فرم
        clear_invoice_form(customer_name_entry, customer_phone_entry, cart_treeview)

        # تازه‌سازی لیست محصولات
        for widget in cart_treeview.master.master.winfo_children():
            if hasattr(widget, "winfo_children"):
                for child in widget.winfo_children():
                    if hasattr(child, "winfo_children"):
                        for grandchild in child.winfo_children():
                            if isinstance(grandchild, ttk.Treeview):
                                if grandchild != cart_treeview:
                                    load_products_to_treeview(grandchild)
                                    break

        messagebox.showinfo(
            "موفقیت",
            f"فاکتور شماره {invoice_number} با موفقیت ثبت شد و در تاریخچه ذخیره گردید.",
            parent=cart_treeview.master.master,
        )

    except Exception as e:
        messagebox.showerror(
            "خطا", f"خطا در ثبت فاکتور: {str(e)}", parent=cart_treeview.master.master
        )
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


def clear_invoice_form(customer_name_entry, customer_phone_entry, cart_treeview):
    customer_name_entry.delete(0, END)
    customer_phone_entry.delete(0, END)
    cart_treeview.delete(*cart_treeview.get_children())
    update_grand_total(cart_treeview)


def on_search_focus_in(event, search_entry):
    if search_entry.get() == "جستجوی محصول...":
        search_entry.delete(0, END)
        search_entry.config(fg="black")


def on_search_focus_out(event, search_entry):
    if search_entry.get() == "":
        search_entry.insert(0, "جستجوی محصول...")
        search_entry.config(fg="gray")


def create_card_frame(parent, title, height=None):
    """ایجاد فریم کارت با طراحی یکپارچه"""
    card = Frame(parent, bg=BG_WHITE, bd=1, relief=SOLID)

    # عنوان کارت
    if title:
        title_frame = Frame(card, bg=PRIMARY_COLOR, height=30)
        title_frame.pack(fill=X)
        Label(
            title_frame,
            text=title,
            font=("B Nazanin", 11, "bold"),
            fg="white",
            bg=PRIMARY_COLOR,
        ).pack(side=RIGHT, padx=8)

    return card


def invoice_form(window):
    create_invoice_tables()

    invoice_frame = Frame(
        window,
        width=window.winfo_width() - 200,
        height=window.winfo_height(),
        bg="#f0f2f5",
    )
    invoice_frame.place(x=0, y=100)

    # ============ هدر صفحه ============
    header_frame = Frame(invoice_frame, bg="#00198f", height=40)
    header_frame.place(x=0, y=0, relwidth=1)

    heading_label = Label(
        header_frame,
        text="📋 صدور فاکتور",
        font=("B Nazanin", 16, "bold"),
        bg="#00198f",
        fg="white",
    )
    heading_label.pack(side=RIGHT, padx=15)

    try:
        back_image = PhotoImage(file="images/back_button.png")
        back_button = Button(
            header_frame,
            image=back_image,
            bd=0,
            cursor="hand2",
            bg="#00198f",
            activebackground="#00198f",
            command=lambda: invoice_frame.place_forget(),
        )
        back_button.pack(side=LEFT, padx=8)
    except:
        back_button = Button(
            header_frame,
            text="← بازگشت",
            font=("B Nazanin", 11),
            bg="#00198f",
            fg="white",
            bd=0,
            cursor="hand2",
            activebackground="#00198f",
            command=lambda: invoice_frame.place_forget(),
        )
        back_button.pack(side=LEFT, padx=8)

    # ============ بخش جستجو ============
    search_card = create_card_frame(invoice_frame, "جستجوی محصولات")
    search_card.place(x=20, y=60, width=1150, height=70)

    # جعبه جستجو (راست)
    search_entry = Entry(
        search_card,
        font=("B Nazanin", 11),
        bg="white",
        width=25,
        justify="right",
        bd=1,
        relief=SOLID,
        fg="gray",
    )
    search_entry.place(x=900, y=18)
    search_entry.insert(0, "جستجوی محصول...")

    # اتصال رویدادهای فوکوس
    search_entry.bind("<FocusIn>", lambda e: on_search_focus_in(e, search_entry))
    search_entry.bind("<FocusOut>", lambda e: on_search_focus_out(e, search_entry))

    # دکمه جستجو (سمت راست)
    search_button = Button(
        search_card,
        text="🔍 جستجو",
        font=("B Nazanin", 11),
        bg=BTN_PRIMARY,
        fg="white",
        width=10,
        height=1,
        bd=0,
        cursor="hand2",
        command=lambda: search_product(
            search_entry, products_treeview, category_filter.get(), status_filter.get()
        ),
    )
    search_button.place(x=800, y=18)

    # فیلتر وضعیت (وسط راست)
    Label(search_card, text="وضعیت:", font=("B Nazanin", 11), bg=BG_WHITE).place(
        x=750, y=20
    )

    status_filter = ttk.Combobox(
        search_card,
        values=["همه", "فعال", "غیرفعال"],
        font=("B Nazanin", 10),
        width=12,
        state="readonly",
        justify="right",
    )
    status_filter.set("همه")
    status_filter.place(x=630, y=18)

    # فیلتر دسته‌بندی (وسط چپ)
    Label(search_card, text="دسته‌بندی:", font=("B Nazanin", 11), bg=BG_WHITE).place(
        x=580, y=20
    )

    category_filter = ttk.Combobox(
        search_card,
        font=("B Nazanin", 10),
        width=15,
        state="readonly",
        justify="right",
    )
    category_filter.place(x=430, y=18)

    # ============ بخش لیست محصولات (سمت چپ) ============
    products_card = create_card_frame(invoice_frame, "لیست محصولات")
    products_card.place(x=20, y=140, width=560, height=400)

    # دکمه افزودن محصول به سبد (بالای جدول)
    add_button_frame = Frame(products_card, bg="white", height=35)
    add_button_frame.pack(fill=X, side=TOP, pady=(5, 0))

    add_to_cart_button = Button(
        add_button_frame,
        text="➕ افزودن به فاکتور",
        font=("B Nazanin", 10),
        bg=BTN_SUCCESS,
        fg="white",
        width=16,
        height=1,
        bd=0,
        cursor="hand2",
        command=lambda: select_product_for_invoice(
            None, products_treeview, cart_treeview, None
        ),
    )
    add_to_cart_button.pack(side=RIGHT, padx=(0, 10))

    # جدول محصولات
    products_tree_container = Frame(products_card, bg="white")
    products_tree_container.pack(fill=BOTH, expand=True, padx=2, pady=2)

    prod_scroll_y = Scrollbar(products_tree_container, orient=VERTICAL)
    prod_scroll_x = Scrollbar(products_tree_container, orient=HORIZONTAL)

    products_treeview = ttk.Treeview(
        products_tree_container,
        columns=("id", "name", "price", "stock", "status"),
        show="headings",
        yscrollcommand=prod_scroll_y.set,
        xscrollcommand=prod_scroll_x.set,
        height=14,
    )

    # استایل Treeview
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Treeview",
        background="white",
        foreground="black",
        rowheight=22,
        fieldbackground="white",
        font=("B Nazanin", 9),
    )
    style.configure(
        "Treeview.Heading",
        background="#f8f9fa",
        foreground="#495057",
        font=("B Nazanin", 10, "bold"),
        relief="flat",
    )

    headers = [
        ("شناسه", 50),
        ("نام محصول", 180),
        ("قیمت", 90),
        ("موجودی", 70),
        ("وضعیت", 80),
    ]

    for i, (header, width) in enumerate(headers):
        products_treeview.heading(f"#{i+1}", text=header)
        products_treeview.column(f"#{i+1}", width=width, anchor="center")

    # استفاده از grid برای چیدمان
    products_treeview.grid(row=0, column=0, sticky="nsew")
    prod_scroll_y.grid(row=0, column=1, sticky="ns")
    prod_scroll_x.grid(row=1, column=0, sticky="ew", columnspan=2)

    products_tree_container.grid_rowconfigure(0, weight=1)
    products_tree_container.grid_columnconfigure(0, weight=1)

    prod_scroll_y.config(command=products_treeview.yview)
    prod_scroll_x.config(command=products_treeview.xview)

    # ============ بخش مشخصات مشتری (سمت راست بالا) ============
    customer_card = create_card_frame(invoice_frame, "مشخصات مشتری")
    customer_card.place(x=600, y=140, width=570, height=120)

    # محتوای بخش مشتری (راست‌چین)
    customer_content = Frame(customer_card, bg="white", padx=10, pady=10)
    customer_content.pack(fill=BOTH, expand=True)

    # نام مشتری
    customer_name_frame = Frame(customer_content, bg="white")
    customer_name_frame.pack(fill=X, pady=5)

    customer_name_entry = Entry(
        customer_name_frame,
        font=("B Nazanin", 11),
        bg="white",
        width=30,
        justify="right",
        bd=1,
        relief=SOLID,
    )
    customer_name_entry.pack(side=RIGHT, fill=X, expand=True)

    Label(
        customer_name_frame,
        text="نام مشتری:",
        font=("B Nazanin", 11),
        bg="white",
    ).pack(side=RIGHT, padx=(10, 5))

    # شماره تماس
    customer_phone_frame = Frame(customer_content, bg="white")
    customer_phone_frame.pack(fill=X, pady=5)

    customer_phone_entry = Entry(
        customer_phone_frame,
        font=("B Nazanin", 11),
        bg="white",
        width=30,
        justify="right",
        bd=1,
        relief=SOLID,
    )
    customer_phone_entry.pack(side=RIGHT, fill=X, expand=True)

    Label(
        customer_phone_frame,
        text="شماره تماس:",
        font=("B Nazanin", 11),
        bg="white",
    ).pack(side=RIGHT, padx=(10, 5))

    # ============ بخش سبد خرید (سمت راست پایین) ============
    cart_card = create_card_frame(invoice_frame, "سبد خرید")
    cart_card.place(x=600, y=270, width=570, height=270)

    # جدول سبد خرید
    cart_tree_container = Frame(cart_card, bg="white")
    cart_tree_container.pack(fill=BOTH, expand=True, padx=2, pady=2)

    cart_scroll_y = Scrollbar(cart_tree_container, orient=VERTICAL)
    cart_scroll_x = Scrollbar(cart_tree_container, orient=HORIZONTAL)

    cart_treeview = ttk.Treeview(
        cart_tree_container,
        columns=("id", "name", "price", "quantity", "total"),
        show="headings",
        yscrollcommand=cart_scroll_y.set,
        xscrollcommand=cart_scroll_x.set,
        height=8,
    )

    cart_headers = [
        ("شناسه", 50),
        ("نام محصول", 180),
        ("قیمت", 90),
        ("تعداد", 70),
        ("جمع", 90),
    ]

    for i, (header, width) in enumerate(cart_headers):
        cart_treeview.heading(f"#{i+1}", text=header)
        cart_treeview.column(f"#{i+1}", width=width, anchor="center")

    # استفاده از grid برای چیدمان
    cart_treeview.grid(row=0, column=0, sticky="nsew")
    cart_scroll_y.grid(row=0, column=1, sticky="ns")
    cart_scroll_x.grid(row=1, column=0, sticky="ew", columnspan=2)

    cart_tree_container.grid_rowconfigure(0, weight=1)
    cart_tree_container.grid_columnconfigure(0, weight=1)

    cart_scroll_y.config(command=cart_treeview.yview)
    cart_scroll_x.config(command=cart_treeview.xview)

    # دکمه‌های مدیریت سبد و مجموع کل
    bottom_controls = Frame(cart_card, bg="white", height=35)
    bottom_controls.pack(fill=X, side=BOTTOM, pady=2)

    # مجموع کل (سمت راست)
    total_frame = Frame(bottom_controls, bg="white")
    total_frame.pack(side=RIGHT, padx=10)

    total_label = Label(
        total_frame,
        text="مجموع کل: 0 تومان",
        font=("B Nazanin", 11, "bold"),
        bg="white",
        fg=BTN_SUCCESS,
    )
    total_label.pack()

    # دکمه‌های مدیریت (سمت چپ)
    button_frame = Frame(bottom_controls, bg="white")
    button_frame.pack(side=LEFT, padx=10)

    remove_button = Button(
        button_frame,
        text="🗑️ حذف",
        font=("B Nazanin", 10),
        bg=BTN_DANGER,
        fg="white",
        width=8,
        height=1,
        bd=0,
        cursor="hand2",
        command=lambda: remove_from_invoice(cart_treeview),
    )
    remove_button.pack(side=LEFT, padx=(0, 5))

    clear_cart_button = Button(
        button_frame,
        text="🧹 پاک کردن",
        font=("B Nazanin", 10),
        bg=BTN_WARNING,
        fg="white",
        width=10,
        height=1,
        bd=0,
        cursor="hand2",
        command=lambda: clear_invoice_form(
            customer_name_entry, customer_phone_entry, cart_treeview
        ),
    )
    clear_cart_button.pack(side=LEFT)

    # ============ دکمه‌های اصلی پایین صفحه ============
    action_frame = Frame(invoice_frame, bg="#f0f2f5")
    action_frame.place(x=20, y=550, width=1150, height=70)

    # ردیف دکمه‌ها (راست‌چین)
    buttons_row = Frame(action_frame, bg="#f0f2f5")
    buttons_row.pack(expand=True)

    # دکمه نمایش پیش‌نمایش فاکتور
    preview_button = Button(
        buttons_row,
        text="👁️ نمایش فاکتور",
        font=("B Nazanin", 12, "bold"),
        bg=BTN_PRIMARY,
        fg="white",
        width=16,
        height=1,
        bd=0,
        cursor="hand2",
        command=lambda: show_invoice_preview(
            customer_name_entry, customer_phone_entry, cart_treeview, window
        ),
    )
    preview_button.pack(side=RIGHT, padx=10)

    save_draft_button = Button(
        buttons_row,
        text="💾 ذخیره پیش‌نویس",
        font=("B Nazanin", 10),
        bg=BTN_INFO,
        fg="white",
        width=14,
        height=1,
        bd=0,
        cursor="hand2",
    )
    save_draft_button.pack(side=RIGHT, padx=10)

    print_button = Button(
        buttons_row,
        text="🖨️ چاپ فاکتور",
        font=("B Nazanin", 10),
        bg=BTN_INFO,
        fg="white",
        width=12,
        height=1,
        bd=0,
        cursor="hand2",
    )
    print_button.pack(side=RIGHT, padx=10)

    cancel_button = Button(
        buttons_row,
        text="❌ انصراف",
        font=("B Nazanin", 10),
        bg=BTN_DANGER,
        fg="white",
        width=12,
        height=1,
        bd=0,
        cursor="hand2",
        command=lambda: invoice_frame.place_forget(),
    )
    cancel_button.pack(side=RIGHT, padx=10)

    # ============ کنترل کیبورد ============
    def search_shortcut(event=None):
        search_button.invoke()

    def add_to_cart_shortcut(event=None):
        add_to_cart_button.invoke()

    window.bind("<F1>", lambda e: search_entry.focus_set())
    window.bind("<F2>", lambda e: category_filter.focus_set())
    window.bind("<F3>", lambda e: status_filter.focus_set())
    window.bind("<F4>", search_shortcut)
    window.bind("<F5>", add_to_cart_shortcut)
    window.bind("<F6>", lambda e: remove_button.invoke())
    window.bind("<F7>", lambda e: clear_cart_button.invoke())
    window.bind("<F8>", lambda e: preview_button.invoke())
    window.bind("<F9>", lambda e: customer_name_entry.focus_set())
    window.bind("<F10>", lambda e: customer_phone_entry.focus_set())
    window.bind("<Escape>", lambda e: invoice_frame.place_forget())

    # Tab Order (راست‌چین)
    search_entry.focus_set()
    search_entry.bind("<Tab>", lambda e: move_focus(category_filter))
    category_filter.bind("<Tab>", lambda e: move_focus(status_filter))
    status_filter.bind("<Tab>", lambda e: move_focus(products_treeview))
    products_treeview.bind("<Tab>", lambda e: move_focus(add_to_cart_button))
    add_to_cart_button.bind("<Tab>", lambda e: move_focus(cart_treeview))
    cart_treeview.bind("<Tab>", lambda e: move_focus(remove_button))
    remove_button.bind("<Tab>", lambda e: move_focus(clear_cart_button))
    clear_cart_button.bind("<Tab>", lambda e: move_focus(customer_name_entry))
    customer_name_entry.bind("<Tab>", lambda e: move_focus(customer_phone_entry))
    customer_phone_entry.bind("<Tab>", lambda e: move_focus(preview_button))
    preview_button.bind("<Tab>", lambda e: move_focus(search_entry))

    # ============ بارگذاری اولیه ============
    load_categories_for_filter(category_filter)
    load_products_to_treeview(products_treeview)  # بارگذاری محصولات

    products_treeview.bind(
        "<Double-Button-1>",
        lambda e: select_product_for_invoice(e, products_treeview, cart_treeview, None),
    )

    return invoice_frame


def create_invoice_tables():
    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute("USE inventory_system")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS invoice_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                invoice_number INT UNIQUE NOT NULL,
                customer_name VARCHAR(100) NOT NULL,
                customer_phone VARCHAR(15),
                total_amount DECIMAL(15,2) NOT NULL,
                invoice_date VARCHAR(10) NOT NULL,
                items_count INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_invoice_number (invoice_number),
                INDEX idx_customer (customer_name),
                INDEX idx_date (invoice_date)
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS invoice_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                invoice_number INT NOT NULL,
                product_id INT NOT NULL,
                product_name VARCHAR(100) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                quantity INT NOT NULL,
                total DECIMAL(15,2) NOT NULL,
                FOREIGN KEY (invoice_number) REFERENCES invoice_history(invoice_number)
                    ON DELETE CASCADE,
                INDEX idx_invoice (invoice_number),
                INDEX idx_product (product_id)
            )
        """
        )

        connection.commit()
        print("✅ جداول فاکتور ایجاد شدند")

    except Exception as e:
        print(f"❌ خطا در ایجاد جداول فاکتور: {e}")
    finally:
        cursor.close()
        connection.close()


def show_invoice_form(window):
    invoice_form(window)
