# database.py - نسخه بدون پیام‌های دیباگ
import pymysql
from tkinter import messagebox


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


def safe_execute(cursor, sql, params=None):
    """اجرای ایمن دستور SQL"""
    try:
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        return True
    except Exception as e:
        return False


def check_and_create_database():
    """بررسی و ایجاد دیتابیس"""
    cursor, connection = connect_database()
    if not cursor or not connection:
        return False

    try:
        safe_execute(cursor, 'CREATE DATABASE IF NOT EXISTS inventory_system')
        safe_execute(cursor, 'USE inventory_system')
        return True
    except Exception as e:
        return False
    finally:
        cursor.close()
        connection.close()


def check_table_structure(cursor):
    """بررسی و اصلاح ساختار جداول"""

    # 1. جدول user_types
    cursor.execute("SHOW TABLES LIKE 'user_types'")
    if not cursor.fetchone():
        sql = '''
            CREATE TABLE user_types (
                id INT AUTO_INCREMENT PRIMARY KEY,
                type_name VARCHAR(100) UNIQUE NOT NULL,
                can_employees BOOLEAN DEFAULT 0,
                can_shifts BOOLEAN DEFAULT 0,
                can_user_types BOOLEAN DEFAULT 0,
                can_suppliers BOOLEAN DEFAULT 0,
                can_categories BOOLEAN DEFAULT 0,
                can_products BOOLEAN DEFAULT 0,
                can_sales BOOLEAN DEFAULT 0,
                can_invoices BOOLEAN DEFAULT 0,
                can_invoice_history BOOLEAN DEFAULT 0,
                is_admin BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''
        safe_execute(cursor, sql)

        safe_execute(cursor, '''
            INSERT INTO user_types 
            (type_name, can_employees, can_shifts, can_user_types, can_suppliers, 
             can_categories, can_products, can_sales, can_invoices, can_invoice_history, is_admin)
            VALUES ('ادمین', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
        ''')
    else:
        cursor.execute("SHOW COLUMNS FROM user_types LIKE 'can_invoice_history'")
        if not cursor.fetchone():
            safe_execute(cursor,
                         'ALTER TABLE user_types ADD COLUMN can_invoice_history BOOLEAN DEFAULT 0 AFTER can_invoices')

    # 2. جدول employee_data
    cursor.execute("SHOW TABLES LIKE 'employee_data'")
    if not cursor.fetchone():
        sql = '''
            CREATE TABLE employee_data (
                empid INT PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100),
                gender VARCHAR(50),
                dob VARCHAR(30),
                contact VARCHAR(30),
                work_shift VARCHAR(50),
                address VARCHAR(100),
                usertype VARCHAR(50),
                password VARCHAR(50)
            )
        '''
        safe_execute(cursor, sql)

        cursor.execute("SELECT COUNT(*) FROM employee_data WHERE name = 'admin'")
        if cursor.fetchone()[0] == 0:
            safe_execute(cursor, '''
                INSERT INTO employee_data 
                (empid, name, usertype, password)
                VALUES (1000, 'admin', 'ادمین', '1234')
            ''')

    # 3. سایر جداول
    tables_def = [
        ('category_data', 'id INT PRIMARY KEY, name VARCHAR(100), description TEXT'),
        ('supplier_data', 'invoice INT PRIMARY KEY, name VARCHAR(100), contact VARCHAR(15), description TEXT'),
        ('product_data',
         'id INT AUTO_INCREMENT PRIMARY KEY, category VARCHAR(50), supplier VARCHAR(50), name VARCHAR(100), price DECIMAL(10,2), quantity INT, status VARCHAR(50)'),
        ('shift_data',
         'shift_id INT PRIMARY KEY AUTO_INCREMENT, shift_name VARCHAR(100) NOT NULL UNIQUE, start_time VARCHAR(10) NOT NULL, end_time VARCHAR(10) NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
    ]

    for table_name, columns in tables_def:
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        if not cursor.fetchone():
            safe_execute(cursor, f'CREATE TABLE {table_name} ({columns})')


def initialize_system():
    """راه‌اندازی سیستم - ساکت"""
    # 1. ایجاد دیتابیس
    if not check_and_create_database():
        return False

    cursor, connection = connect_database()
    if not cursor or not connection:
        return False

    try:
        cursor.execute('USE inventory_system')

        # 2. بررسی و اصلاح جداول
        check_table_structure(cursor)

        connection.commit()
        return True

    except Exception as e:
        return False
    finally:
        cursor.close()
        connection.close()


def get_user_info(username, password):
    """دریافت اطلاعات کاربر"""
    cursor, connection = connect_database()
    if not cursor or not connection:
        return None

    try:
        cursor.execute('USE inventory_system')

        sql = '''
            SELECT 
                e.empid, 
                e.name, 
                e.usertype,
                COALESCE(ut.can_employees, 0) as can_employees,
                COALESCE(ut.can_shifts, 0) as can_shifts,
                COALESCE(ut.can_user_types, 0) as can_user_types,
                COALESCE(ut.can_suppliers, 0) as can_suppliers,
                COALESCE(ut.can_categories, 0) as can_categories,
                COALESCE(ut.can_products, 0) as can_products,
                COALESCE(ut.can_sales, 0) as can_sales,
                COALESCE(ut.can_invoices, 0) as can_invoices,
                COALESCE(ut.can_invoice_history, 0) as can_invoice_history
            FROM employee_data e
            LEFT JOIN user_types ut ON e.usertype = ut.type_name
            WHERE TRIM(e.name) = TRIM(%s) AND e.password = %s
        '''

        cursor.execute(sql, (username, password))
        user = cursor.fetchone()

        if user:
            return {
                'id': user[0],
                'name': user[1],
                'user_type': user[2],
                'permissions': {
                    'employees': bool(user[3]),
                    'shifts': bool(user[4]),
                    'user_types': bool(user[5]),
                    'suppliers': bool(user[6]),
                    'categories': bool(user[7]),
                    'products': bool(user[8]),
                    'sales': bool(user[9]),
                    'invoices': bool(user[10]),
                    'invoice_history': bool(user[11])
                }
            }
        return None

    except Exception as e:
        return None
    finally:
        cursor.close()
        connection.close()


def get_shifts_from_db():
    """دریافت شیفت‌ها"""
    cursor, connection = connect_database()
    if not cursor or not connection:
        return []

    try:
        cursor.execute('USE inventory_system')
        cursor.execute('SELECT shift_name FROM shift_data')
        return [s[0] for s in cursor.fetchall()]
    except:
        return []
    finally:
        cursor.close()
        connection.close()