from tkinter import *
from employees import employee_form
from supplier import supplier_form
from category import category_form
from products import product_form
from datetime import datetime
from shift import shift_form


# GUI Part
window = Tk()
window.rowconfigure(0, weight=0)
window.rowconfigure(1, weight=0)
window.rowconfigure(2, weight=1)

window.columnconfigure(0, weight=1)



def toggle_window():
    if window.state() == "zoomed":
        window.state("normal")
    else:
        window.state("zoomed")
        Button(
            window,
            text="🗕",
            font=("Yekan", 14, "bold"),
            width=4,
            height=1,
            bg="#00198f",
            fg="white",
            command=toggle_window,
        ).place(x=1250, y=10)


def update_datetime():
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    SubtitleLabel.config(
        text=f"ادمین خوش آمدید\t\t تاریخ: {date_str}\t\t ساعت: {time_str}"
    )
    window.after(1000, update_datetime)


window.config(bg="#fef9fb")

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

logoButten = Button(
    window,
    text="  خروج  ",
    bg="#4b39e9",
    font=("Yekan", 16, "bold"),
    fg="#fef9fb",
    command=window.destroy,
)

logoButten.place(x=1100, y=10)

SubtitleLabel = Label(
    window,
    text="ادمین خوش آمدید\t\t تاریخ: 01-11-2025\t\t ساعت:14:36:17",
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
employee_button.pack(fill=X)

# ============ دکمه جدید: تعریف شیفت ============
# اگر آیکون shift.png ندارید، از یکی از آیکون‌های موجود استفاده کنید یا بدون آیکون بسازید
try:
    shift_icon = PhotoImage(file="images/clock.png")  # یا time.png یا هر آیکون ساعت دیگر
except:
    # اگر آیکون وجود ندارد، دکمه بدون آیکون بسازید
    shift_icon = None

shift_button = Button(
    leftFrame,
    text="       تعریف شیفت",
    font=("fonts/Persian-Yekan.ttf", 15, "bold"),
    anchor="w",
    padx=10,
    command=lambda: shift_form(window),
    bg="#fef9fb",  # رنگ پس‌زمینه
    fg="#00198f",  # رنگ متن
    relief=FLAT,  # حاشیه صاف
    bd=0,  # بدون border
    cursor="hand2"  # حالت دست هنگام hover
)

# اگر آیکون دارید، آن را اضافه کنید
if shift_icon:
    shift_button.config(image=shift_icon, compound=LEFT)

shift_button.pack(fill=X)


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
supplier_button.pack(fill=X)


category_icon = PhotoImage(file="images/category.png")
category_button = Button(
    leftFrame,
    image=category_icon,
    compound=LEFT,
    text="       دسته بندی ",
    font=("fonts/Persian-Yekan.ttf", 15, "bold"),
    command=lambda: category_form(window),
)
category_button.pack(fill=X)

products_icon = PhotoImage(file="images/products.png")
products_button = Button(
    leftFrame,
    image=products_icon,
    compound=LEFT,
    text="         محصولات ",
    font=("fonts/Persian-Yekan.ttf", 15, "bold"),
    command=lambda: product_form(window),
)
products_button.pack(fill=X)

sale_icon = PhotoImage(file="images/sale.png")
sale_button = Button(
    leftFrame,
    image=sale_icon,
    compound=LEFT,
    text="             فروش",
    font=("fonts/Persian-Yekan.ttf", 15, "bold"),
)
sale_button.pack(fill=X)

exit_icon = PhotoImage(file="images/exit.png")
exit_button = Button(
    leftFrame,
    image=exit_icon,
    compound=LEFT,
    text="             خروج",
    font=("fonts/Persian-Yekan.ttf", 15, "bold"),
)
exit_button.pack(fill=X)


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


category_frame = Frame(content, bg="#00198f", bd=4, relief=RIDGE)
category_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
totl_category_icon = PhotoImage(file="images/total_category.png")
totl_category_icon_label = Label(category_frame, image=totl_category_icon, bg="#00198f")
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


product_frame = Frame(content, bg="#00198f", bd=4, relief=RIDGE)
product_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
totl_product_icon = PhotoImage(file="images/total_product.png")
totl_product_icon_label = Label(product_frame, image=totl_product_icon, bg="#00198f")
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


sale_frame = Frame(content, bg="#00198f", bd=4, relief=RIDGE)
sale_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
totl_sale_icon = PhotoImage(file="images/total_sale.png")
totl_sale_icon_label = Label(sale_frame, image=totl_sale_icon, bg="#00198f")
totl_sale_icon_label.pack(pady=8)

totl_sale_label = Label(
    sale_frame,
    text=" تعداد فروش ",
    bg="#00198f",
    fg="#fef9fb",
    font=("fonts/Persian-Yekan.ttf", 15, "bold"),
)
totl_sale_label.pack()

totl_sale_count = Label(
    sale_frame,
    text="0",
    bg="#00198f",
    fg="#fef9fb",
    font=("fonts/Persian-Yekan.ttf", 25, "bold"),
)
totl_sale_count.pack()
window.mainloop()
