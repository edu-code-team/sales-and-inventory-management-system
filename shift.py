from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pymysql


def treeview_data(shift_treeview):
    """بارگذاری داده‌های شیفت در جدول"""
    cursor, connection = connect_database()
    if not cursor or not connection:
        return
    try:
        cursor.execute('USE inventory_system')
        cursor.execute('SELECT shift_id, shift_name, start_time, end_time FROM shift_data ORDER BY shift_name')
        shift_records = cursor.fetchall()
        shift_treeview.delete(*shift_treeview.get_children())
        for records in shift_records:
            shift_treeview.insert('', END, values=records)
    except Exception as e:
        messagebox.showerror('خطا', f'خطا در بارگذاری داده‌ها: {e}')
    finally:
        cursor.close()
        connection.close()


def connect_database():
    """اتصال به پایگاه داده"""
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            passwd='',
            charset='utf8mb4'
        )
        cursor = connection.cursor()
        return cursor, connection
    except Exception as e:
        messagebox.showerror('خطا', f'اتصال به پایگاه داده ناموفق: {e}')
        return None, None


def create_shift_table():
    """ایجاد جدول شیفت در پایگاه داده"""
    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute('CREATE DATABASE IF NOT EXISTS inventory_system DEFAULT CHARACTER SET utf8')
        cursor.execute('USE inventory_system')

        # ایجاد جدول شیفت
        cursor.execute('''CREATE TABLE IF NOT EXISTS shift_data (
            shift_id INT PRIMARY KEY AUTO_INCREMENT,
            shift_name VARCHAR(100) NOT NULL UNIQUE,
            start_time VARCHAR(10) NOT NULL,
            end_time VARCHAR(10) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

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
        hours, minutes = time_str.split(':')
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
        cursor.execute('USE inventory_system')
        cursor.execute('SELECT shift_name FROM shift_data ORDER BY shift_name')
        shifts = cursor.fetchall()
        return [shift[0] for shift in shifts]
    except:
        return []
    finally:
        cursor.close()
        connection.close()


def shift_form(window):
    """فرم تعریف شیفت"""

    def select_data(event):
        """انتخاب ردیف از جدول"""
        index = shift_treeview.selection()
        if not index:
            return

        content = shift_treeview.item(index)
        row = content['values']

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
            messagebox.showerror('خطا', 'نام شیفت را وارد کنید')
            return

        if not start_time or not end_time:
            messagebox.showerror('خطا', 'ساعت شروع و پایان را وارد کنید')
            return

        # اعتبارسنجی فرمت زمان
        if not validate_time_format(start_time) or not validate_time_format(end_time):
            messagebox.showerror('خطا', 'فرمت زمان باید HH:MM باشد (مثال: 08:30)')
            return

        cursor, connection = connect_database()
        if not cursor or not connection:
            return

        try:
            cursor.execute('USE inventory_system')

            # بررسی تکراری نبودن نام شیفت
            cursor.execute('SELECT * FROM shift_data WHERE shift_name = %s', (shift_name,))
            if cursor.fetchone():
                messagebox.showerror('خطا', 'این نام شیفت قبلاً ثبت شده است')
                return

            # اضافه کردن شیفت جدید
            cursor.execute('INSERT INTO shift_data (shift_name, start_time, end_time) VALUES (%s, %s, %s)',
                           (shift_name, start_time, end_time))
            connection.commit()

            treeview_data(shift_treeview)
            messagebox.showinfo('موفقیت', 'شیفت جدید با موفقیت اضافه شد')

            # پاک کردن فیلدها بعد از اضافه کردن
            clear_fields()

        except Exception as e:
            messagebox.showerror('خطا', f'خطا در اضافه کردن شیفت: {e}')
        finally:
            cursor.close()
            connection.close()

    def update_shift():
        """به‌روزرسانی شیفت"""
        selected_item = shift_treeview.selection()
        if not selected_item:
            messagebox.showerror('خطا', 'لطفاً یک شیفت را برای ویرایش انتخاب کنید')
            return

        # دریافت داده‌های انتخاب شده
        item = shift_treeview.item(selected_item[0])
        shift_id = item['values'][0]
        old_shift_name = item['values'][1]

        # دریافت داده‌های جدید از فیلدها
        new_shift_name = shift_name_entry.get().strip()
        new_start_time = start_time_entry.get().strip()
        new_end_time = end_time_entry.get().strip()

        if not new_shift_name or not new_start_time or not new_end_time:
            messagebox.showerror('خطا', 'تمامی فیلدها باید پر شوند')
            return

        # اعتبارسنجی فرمت زمان
        if not validate_time_format(new_start_time) or not validate_time_format(new_end_time):
            messagebox.showerror('خطا', 'فرمت زمان باید HH:MM باشد (مثال: 08:30)')
            return

        cursor, connection = connect_database()
        if not cursor or not connection:
            return

        try:
            cursor.execute('USE inventory_system')

            # بررسی تکراری نبودن نام شیفت (به جز خودش)
            if new_shift_name != old_shift_name:
                cursor.execute('SELECT * FROM shift_data WHERE shift_name = %s AND shift_id != %s',
                               (new_shift_name, shift_id))
                if cursor.fetchone():
                    messagebox.showerror('خطا', 'این نام شیفت قبلاً ثبت شده است')
                    return

            # به‌روزرسانی شیفت
            cursor.execute('UPDATE shift_data SET shift_name = %s, start_time = %s, end_time = %s WHERE shift_id = %s',
                           (new_shift_name, new_start_time, new_end_time, shift_id))
            connection.commit()

            treeview_data(shift_treeview)
            messagebox.showinfo('موفقیت', 'شیفت با موفقیت ویرایش شد')

            # پاک کردن فیلدها
            clear_fields()

        except Exception as e:
            messagebox.showerror('خطا', f'خطا در ویرایش شیفت: {e}')
        finally:
            cursor.close()
            connection.close()

    def delete_shift():
        """حذف شیفت"""
        selected_item = shift_treeview.selection()
        if not selected_item:
            messagebox.showerror('خطا', 'لطفاً یک شیفت را برای حذف انتخاب کنید')
            return

        # دریافت نام شیفت انتخاب شده
        item = shift_treeview.item(selected_item[0])
        shift_id = item['values'][0]
        shift_name = item['values'][1]

        # تأیید حذف
        confirm = messagebox.askyesno('تأیید حذف',
                                      f'آیا از حذف شیفت "{shift_name}" مطمئن هستید؟')
        if not confirm:
            return

        cursor, connection = connect_database()
        if not cursor or not connection:
            return

        try:
            cursor.execute('USE inventory_system')

            # بررسی اینکه آیا این شیفت در جدول کارمندان استفاده شده
            cursor.execute('SELECT COUNT(*) FROM employee_data WHERE work_shift = %s', (shift_name,))
            employee_count = cursor.fetchone()[0]

            if employee_count > 0:
                messagebox.showwarning('اخطار',
                                       f'این شیفت در {employee_count} کارمند استفاده شده است. ابتدا شیفت کارمندان را تغییر دهید.')
                return

            # حذف شیفت
            cursor.execute('DELETE FROM shift_data WHERE shift_id = %s', (shift_id,))
            connection.commit()

            treeview_data(shift_treeview)
            messagebox.showinfo('موفقیت', 'شیفت با موفقیت حذف شد')

            # پاک کردن فیلدها
            clear_fields()

        except Exception as e:
            messagebox.showerror('خطا', f'خطا در حذف شیفت: {e}')
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
    shift_frame = Frame(window, width=1165, height=567, bg='white')
    shift_frame.place(x=200, y=100)

    heading_label = Label(shift_frame, text='تعریف شیفت', font=('fonts/Persian-Yekan.ttf', 16, 'bold'),
                          bg='#00198f', fg='white')
    heading_label.place(x=0, y=0, relwidth=1)

    # اگر back_button.png ندارید، از این استفاده کنید یا کامنت کنید
    try:
        back_image = PhotoImage(file='images/back_button.png')
        back_button = Button(shift_frame, image=back_image, bd=0, cursor='hand2', bg='white',
                             command=lambda: shift_frame.place_forget())
        back_button.place(x=10, y=10)
    except:
        # اگر آیکون وجود ندارد، دکمه متنی ایجاد کنید
        back_button = Button(shift_frame, text='← بازگشت', font=('fonts/Persian-Yekan.ttf', 12),
                             bg='#00198f', fg='white', bd=0, cursor='hand2',
                             command=lambda: shift_frame.place_forget())
        back_button.place(x=10, y=10)

    top_frame = Frame(shift_frame, bg='white')
    top_frame.place(x=0, y=50, relwidth=1, height=235)

    # ایجاد جدول Treeview
    style = ttk.Style()
    style.configure("Treeview.Heading", font=('fonts/Persian-Yekan.ttf', 12, 'bold'),
                    background='#00198f', foreground='white')
    style.configure("Treeview", font=('fonts/Persian-Yekan.ttf', 11), rowheight=25)

    horizontal_scrollbar = Scrollbar(top_frame, orient=HORIZONTAL)
    vertical_scrollbar = Scrollbar(top_frame, orient=VERTICAL)

    shift_treeview = ttk.Treeview(
        top_frame,
        columns=('shift_id', 'shift_name', 'start_time', 'end_time'),
        show='headings',
        yscrollcommand=vertical_scrollbar.set,
        xscrollcommand=horizontal_scrollbar.set
    )

    horizontal_scrollbar.config(command=shift_treeview.xview)
    vertical_scrollbar.config(command=shift_treeview.yview)

    horizontal_scrollbar.pack(side=BOTTOM, fill=X)
    vertical_scrollbar.pack(side=RIGHT, fill=Y)
    shift_treeview.pack(fill=BOTH, expand=True)

    # تنظیم ستون‌ها
    shift_treeview.heading('shift_id', text='شناسه')
    shift_treeview.heading('shift_name', text='نام شیفت')
    shift_treeview.heading('start_time', text='ساعت شروع (HH:MM)')
    shift_treeview.heading('end_time', text='ساعت پایان (HH:MM)')

    shift_treeview.column('shift_id', width=60)
    shift_treeview.column('shift_name', width=200)
    shift_treeview.column('start_time', width=120)
    shift_treeview.column('end_time', width=120)

    # ایجاد فرم ورود اطلاعات
    detail_frame = Frame(shift_frame, bg='white')
    detail_frame.place(x=30, y=300)

    # نام شیفت
    shift_name_label = Label(detail_frame, text='نام شیفت *', font=('fonts/Persian-Yekan.ttf', 12), bg='white')
    shift_name_label.grid(row=0, column=0, padx=20, pady=10, sticky='w')
    shift_name_entry = Entry(detail_frame, font=('fonts/Persian-Yekan.ttf', 12), bg='lightblue', width=25)
    shift_name_entry.grid(row=0, column=1, padx=20, pady=10)

    # ساعت شروع
    start_time_label = Label(detail_frame, text='ساعت شروع *', font=('fonts/Persian-Yekan.ttf', 12), bg='white')
    start_time_label.grid(row=0, column=2, padx=20, pady=10, sticky='w')
    start_time_entry = Entry(detail_frame, font=('fonts/Persian-Yekan.ttf', 12), bg='lightblue', width=15)
    start_time_entry.insert(0, '08:00')
    start_time_entry.grid(row=0, column=3, padx=20, pady=10)
    Label(detail_frame, text='(فرمت: HH:MM)', font=('fonts/Persian-Yekan.ttf', 10), bg='white', fg='gray').grid(row=1,
                                                                                                                column=3,
                                                                                                                sticky='w',
                                                                                                                padx=20)

    # ساعت پایان
    end_time_label = Label(detail_frame, text='ساعت پایان *', font=('fonts/Persian-Yekan.ttf', 12), bg='white')
    end_time_label.grid(row=0, column=4, padx=20, pady=10, sticky='w')
    end_time_entry = Entry(detail_frame, font=('fonts/Persian-Yekan.ttf', 12), bg='lightblue', width=15)
    end_time_entry.insert(0, '16:00')
    end_time_entry.grid(row=0, column=5, padx=20, pady=10)
    Label(detail_frame, text='(فرمت: HH:MM)', font=('fonts/Persian-Yekan.ttf', 10), bg='white', fg='gray').grid(row=1,
                                                                                                                column=5,
                                                                                                                sticky='w',
                                                                                                                padx=20)

    # ایجاد دکمه‌ها
    button_frame = Frame(shift_frame, bg='white')
    button_frame.place(x=200, y=500)

    add_button = Button(button_frame, text='➕ افزودن شیفت', font=('fonts/Persian-Yekan.ttf', 12), fg='white',
                        bg='#00198f', width=15, command=add_shift)
    add_button.grid(row=0, column=0, padx=10)

    update_button = Button(button_frame, text='✏️ ویرایش شیفت', font=('fonts/Persian-Yekan.ttf', 12), fg='white',
                           bg='#00198f', width=15, command=update_shift)
    update_button.grid(row=0, column=1, padx=10)

    delete_button = Button(button_frame, text='🗑️ حذف شیفت', font=('fonts/Persian-Yekan.ttf', 12), fg='white',
                           bg='#00198f', width=15, command=delete_shift)
    delete_button.grid(row=0, column=2, padx=10)

    clear_button = Button(button_frame, text='🧹 پاک کردن فیلدها', font=('fonts/Persian-Yekan.ttf', 12), fg='white',
                          bg='#00198f', width=15, command=clear_fields)
    clear_button.grid(row=0, column=3, padx=10)

    # اتصال رویداد انتخاب در جدول
    shift_treeview.bind('<ButtonRelease-1>', lambda event: select_data(event))

    # ایجاد جدول و بارگذاری داده‌ها
    create_shift_table()
    treeview_data(shift_treeview)

    return shift_frame