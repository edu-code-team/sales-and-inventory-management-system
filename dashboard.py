# dashboard.py
from tkinter import *
from tkinter import ttk, messagebox
from employees import employee_form
from supplier import supplier_form
from category import category_form
from products import product_form
from datetime import datetime
from shift import shift_form
from user_type import user_type_form
from check_permissions import can_access
from database import get_count
import sys
import subprocess
import os


def main(user_info=None):
    """تابع اصلی اجرای داشبورد"""
    if not user_info:
        # اگر کاربر اطلاعات نداشت، لاگین را اجرا کن
        run_login()
        return

    # GUI Part
    window = Tk()
    window.title(f"سیستم فروش و انبارداری - {user_info['name']}")

    # اطلاعات کاربر جاری
    current_user = user_info

    window.rowconfigure(0, weight=0)
    window.rowconfigure(1, weight=0)
    window.rowconfigure(2, weight=1)
    window.columnconfigure(0, weight=1)

    def toggle_window():
        if window.state() == "zoomed":
            window.state("normal")
        else:
            window.state("zoomed")

    def update_datetime():
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        SubtitleLabel.config(
            text=f"{current_user['name']} خوش آمدید ({current_user['user_type']}) \t\t تاریخ: {date_str}\t\t ساعت: {time_str}"
        )
        window.after(1000, update_datetime)

    window.config(bg="#fef9fb")

    # نمایش پنجره در حالت تمام صفحه
    window.state("zoomed")

    bg_image = PhotoImage(file="images/inventory.png")
    titleLable = Label(
        window,
        image=bg_image,
        compound=LEFT,
        text="                               سیستم فروش و انبار داری ",
        font=("fonts/Persian-Yekan.ttf", 30, "bold"),
        bg="#813ffe",
        fg="#07070a",
        anchor="w",
        padx=20,
    )
    titleLable.grid(row=0, column=0, sticky="ew")

    # دکمه خروج (برای خروج از برنامه)
    logoButten = Button(
        window,
        text="  خروج از سیستم  ",
        bg="#dc3545",
        font=("Yekan", 14, "bold"),
        fg="#fef9fb",
        command=lambda: logout(window),
    )
    logoButten.place(x=1100, y=10)

    # دکمه تغییر کاربر
    change_user_button = Button(
        window,
        text="  تغییر کاربر  ",
        bg="#4b39e9",
        font=("Yekan", 14, "bold"),
        fg="#fef9fb",
        command=lambda: change_user(window),
    )
    change_user_button.place(x=950, y=10)

    SubtitleLabel = Label(
        window,
        text=f"{current_user['name']} خوش آمدید ({current_user['user_type']}) \t\t تاریخ: 01-11-2025\t\t ساعت:14:36:17",
        font=("fonts/Persian-Yekan.ttf", 15),
        bg="#4b39e9",
        fg="#fef9fb",
    )
    SubtitleLabel.grid(row=1, column=0, sticky="ew")
    update_datetime()

    main_frame = Frame(window, bg="#fef9fb")
    main_frame.grid(row=2, column=0, sticky="nsew")

    main_frame.columnconfigure(0, weight=0)
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(0, weight=1)

    leftFrame = Frame(main_frame)
    leftFrame.grid(row=0, column=0, sticky="ns")

    content = Frame(main_frame, bg="#fef9fb")
    content.grid(row=0, column=1, sticky="nsew")

    for i in range(3):
        content.rowconfigure(i, weight=1)

    for j in range(2):
        content.columnconfigure(j, weight=1)

    LogoImage = PhotoImage(file="images/checklist-1.png")
    imageLable = Label(leftFrame, image=LogoImage)
    imageLable.pack()

    menuLabel = Label(
        leftFrame,
        text="منو",
        font=("fonts/Persian-Yekan.ttf", 14, "bold"),
        bg="#00198f",
        fg="#fef9fb",
    )
    menuLabel.pack(fill=X)

    # ایجاد دکمه‌های منو
    employee_icon = PhotoImage(file="images/employee.png")
    employee_button = Button(
        leftFrame,
        image=employee_icon,
        compound=LEFT,
        text="          کارمندان",
        font=("fonts/Persian-Yekan.ttf", 15, "bold"),
        anchor="w",
        padx=10,
        command=lambda: employee_form(window),
    )

    # ============ دکمه تعریف شیفت ============
    shift_button = Button(
        leftFrame,
        compound=LEFT,
        text="       تعریف شیفت",
        font=("fonts/Persian-Yekan.ttf", 15, "bold"),
        padx=10,
        command=lambda: shift_form(window),
    )

    # ============ دکمه تعریف کاربری ============
    try:
        user_type_icon = PhotoImage(file="images/user.png")
    except:
        user_type_icon = None

    user_type_button = Button(
        leftFrame,
        image=user_type_icon,
        compound=LEFT,
        text="       تعریف کاربری",
        font=("fonts/Persian-Yekan.ttf", 15, "bold"),
        padx=10,
        command=lambda: user_type_form(window),
    )

    user_type_button.image = user_type_icon

    supplier_icon = PhotoImage(file="images/supplier.png")
    supplier_button = Button(
        leftFrame,
        image=supplier_icon,
        compound=LEFT,
        text="   تامین کنندگان",
        font=("fonts/Persian-Yekan.ttf", 15, "bold"),
        padx=10,
        command=lambda: supplier_form(window),
    )

    category_icon = PhotoImage(file="images/category.png")
    category_button = Button(
        leftFrame,
        image=category_icon,
        compound=LEFT,
        text="       دسته بندی ",
        font=("fonts/Persian-Yekan.ttf", 15, "bold"),
        command=lambda: category_form(window),
    )

    products_icon = PhotoImage(file="images/products.png")
    products_button = Button(
        leftFrame,
        image=products_icon,
        compound=LEFT,
        text="         محصولات ",
        font=("fonts/Persian-Yekan.ttf", 15, "bold"),
        command=lambda: product_form(window),
    )

    # ============ دکمه صدور فاکتور ============
    try:
        invoice_icon = PhotoImage(file="images/invoice.png")
    except:
        invoice_icon = None

    invoice_button = Button(
        leftFrame,
        compound=LEFT,
        text="       صدور فاکتور",
        font=("fonts/Persian-Yekan.ttf", 15, "bold"),
        padx=10,
    )

    if invoice_icon:
        invoice_button.config(image=invoice_icon, compound=LEFT)

    # ============ دکمه تاریخچه فاکتور ============
    try:
        invoice_history_icon = PhotoImage(file="images/invoice_history.png")
    except:
        invoice_history_icon = None

    invoice_history_button = Button(
        leftFrame,
        compound=LEFT,
        text="   تاریخچه فاکتور",
        font=("fonts/Persian-Yekan.ttf", 15, "bold"),
        padx=10,
    )

    if invoice_history_icon:
        invoice_history_button.config(image=invoice_history_icon, compound=LEFT)
    elif invoice_icon:
        invoice_history_button.config(image=invoice_icon, compound=LEFT)

    exit_icon = PhotoImage(file="images/exit.png")
    exit_button = Button(
        leftFrame,
        image=exit_icon,
        compound=LEFT,
        text="             خروج",
        font=("fonts/Persian-Yekan.ttf", 15, "bold"),
        command=lambda: logout(window),
    )

    def create_menu_for_user():
        """ایجاد منو بر اساس دسترسی کاربر"""

        # ابتدا همه دکمه‌ها را مخفی می‌کنیم
        for button in [
            employee_button,
            shift_button,
            user_type_button,
            supplier_button,
            category_button,
            products_button,
            invoice_button,
            invoice_history_button,
            exit_button,
        ]:
            button.pack_forget()

        # نمایش دکمه‌های مجاز
        if can_access(current_user["user_type"], "employees"):
            employee_button.pack(fill=X)

        if can_access(current_user["user_type"], "shifts"):
            shift_button.pack(fill=X)

        if can_access(current_user["user_type"], "user_types"):
            user_type_button.pack(fill=X)

        if can_access(current_user["user_type"], "suppliers"):
            supplier_button.pack(fill=X)

        if can_access(current_user["user_type"], "categories"):
            category_button.pack(fill=X)

        if can_access(current_user["user_type"], "products"):
            products_button.pack(fill=X)

        if can_access(current_user["user_type"], "invoices"):
            invoice_button.pack(fill=X)

        if can_access(current_user["user_type"], "invoice_history"):
            invoice_history_button.pack(fill=X)

        # دکمه خروج همیشه نمایش داده شود
        exit_button.pack(fill=X)

    def logout(win):
        """خروج از سیستم"""
        if messagebox.askyesno("خروج", "آیا از خروج از سیستم مطمئن هستید؟"):
            win.destroy()
            # اجرای مجدد لاگین
            run_login()

    def change_user(win):
        """تغییر کاربر"""
        if messagebox.askyesno("تغییر کاربر", "آیا می‌خواهید کاربر دیگری وارد شود؟"):
            win.destroy()
            # اجرای مجدد لاگین
            run_login()

    def run_login():
        """اجرای برنامه لاگین"""
        # راه اول: اجرای مجدد فایل login.py
        python = sys.executable
        subprocess.Popen([python, "login.py"])
        sys.exit(0)

    # ایجاد منو
    create_menu_for_user()

    # ویجت‌های داشبورد (آمارها)
    emp_frame = Frame(content, bg="#00198f", bd=4, relief=RIDGE)
    emp_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    totl_emp_icon = PhotoImage(file="images/total_employee.png")
    totl_emp_icon_label = Label(emp_frame, image=totl_emp_icon, bg="#00198f")
    totl_emp_icon_label.pack(pady=8)

    totl_emp_label = Label(
        emp_frame,
        text="تعداد کارمندان",
        bg="#00198f",
        fg="#fef9fb",
        font=("fonts/Persian-Yekan.ttf", 15, "bold"),
    )
    totl_emp_label.pack()

    totl_emp_count = Label(
        emp_frame,
        text="0",
        bg="#00198f",
        fg="#fef9fb",
        font=("fonts/Persian-Yekan.ttf", 25, "bold"),
    )

    totl_emp_count.pack()
    totl_emp_count.config(text=str(get_count("employee_data")))

    sup_frame = Frame(content, bg="#00198f", bd=4, relief=RIDGE)
    sup_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    totl_sup_icon = PhotoImage(file="images/total_sup.png")
    totl_sup_icon_label = Label(sup_frame, image=totl_sup_icon, bg="#00198f")
    totl_sup_icon_label.pack(pady=8)

    totl_sup_label = Label(
        sup_frame,
        text=" تعداد تامین کنندگان  ",
        bg="#00198f",
        fg="#fef9fb",
        font=("fonts/Persian-Yekan.ttf", 15, "bold"),
    )
    totl_sup_label.pack()

    totl_sup_count = Label(
        sup_frame,
        text="0",
        bg="#00198f",
        fg="#fef9fb",
        font=("fonts/Persian-Yekan.ttf", 25, "bold"),
    )
    totl_sup_count.pack()
    totl_sup_count.config(text=str(get_count("supplier_data")))

    category_frame = Frame(content, bg="#00198f", bd=4, relief=RIDGE)
    category_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    totl_category_icon = PhotoImage(file="images/total_category.png")
    totl_category_icon_label = Label(
        category_frame, image=totl_category_icon, bg="#00198f"
    )
    totl_category_icon_label.pack(pady=8)

    totl_category_label = Label(
        category_frame,
        text=" تعداد دسته بندی ها  ",
        bg="#00198f",
        fg="#fef9fb",
        font=("fonts/Persian-Yekan.ttf", 15, "bold"),
    )
    totl_category_label.pack()

    totl_category_count = Label(
        category_frame,
        text="0",
        bg="#00198f",
        fg="#fef9fb",
        font=("fonts/Persian-Yekan.ttf", 25, "bold"),
    )
    totl_category_count.pack()
    totl_category_count.config(text=str(get_count("category_data")))

    product_frame = Frame(content, bg="#00198f", bd=4, relief=RIDGE)
    product_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
    totl_product_icon = PhotoImage(file="images/total_product.png")
    totl_product_icon_label = Label(
        product_frame, image=totl_product_icon, bg="#00198f"
    )
    totl_product_icon_label.pack(pady=8)

    totl_product_label = Label(
        product_frame,
        text="    تعداد محصولات     ",
        bg="#00198f",
        fg="#fef9fb",
        font=("fonts/Persian-Yekan.ttf", 15, "bold"),
    )
    totl_product_label.pack()

    totl_product_count = Label(
        product_frame,
        text="0",
        bg="#00198f",
        fg="#fef9fb",
        font=("fonts/Persian-Yekan.ttf", 25, "bold"),
    )
    totl_product_count.pack()
    totl_product_count.config(text=str(get_count("product_data")))

    window.mainloop()


def run_login():
    """اجرای مستقیم لاگین"""
    from login import LoginSystem

    app = LoginSystem()
    app.run()


# تابع قدیمی برای سازگاری
def show_dashboard():
    """نمایش داشبورد (برای استفاده از خارج)"""
    main()


if __name__ == "__main__":
    # اگر مستقیماً اجرا شد، برو به لاگین
    run_login()
