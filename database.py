import pymysql
from tkinter import messagebox


def connect_database():
    """اتصال به پایگاه داده (تابع مشترک)"""
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


def get_shifts_from_db():
    """دریافت لیست شیفت‌ها از دیتابیس"""
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