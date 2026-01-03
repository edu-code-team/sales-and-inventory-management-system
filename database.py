# database.py - نسخه اصلاح شده (بدون حذف داده‌ها)
import pymysql
from tkinter import messagebox


def connect_database():
    """اتصال به پایگاه داده"""
    try:
        connection = pymysql.connect(
            host="localhost", user="root", passwd="", charset="utf8mb4"
        )
        cursor = connection.cursor()
        return cursor, connection
    except Exception as e:
        messagebox.showerror("خطا", f"اتصال به پایگاه داده ناموفق: {e}")
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
        print(f"⚠️ خطا در اجرای SQL: {e}")
        return False


def check_and_create_database():
    """بررسی و ایجاد دیتابیس"""
    cursor, connection = connect_database()
    if not cursor or not connection:
        return False

    try:
        safe_execute(cursor, "CREATE DATABASE IF NOT EXISTS inventory_system")
        safe_execute(cursor, "USE inventory_system")
        print("✅ دیتابیس بررسی شد")
        return True
    except Exception as e:
        print(f"❌ خطا در دیتابیس: {e}")
        return False
    finally:
        cursor.close()
        connection.close()


def check_table_structure(cursor):
    """بررسی و اصلاح ساختار جداول"""
    print("\n🔍 بررسی ساختار جداول...")

    # 1. جدول user_types
    cursor.execute("SHOW TABLES LIKE 'user_types'")
    if not cursor.fetchone():
        # جدول وجود ندارد، ایجاد کن
        sql = """
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
        """
        safe_execute(cursor, sql)
        print("✅ جدول user_types ایجاد شد")

        # اضافه کردن ادمین
        safe_execute(
            cursor,
            """
            INSERT INTO user_types 
            (type_name, can_employees, can_shifts, can_user_types, can_suppliers, 
             can_categories, can_products, can_sales, can_invoices, can_invoice_history, is_admin)
            VALUES ('ادمین', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
        """,
        )
    else:
        print("✅ جدول user_types از قبل موجود است")
        # بررسی ستون can_invoice_history
        cursor.execute("SHOW COLUMNS FROM user_types LIKE 'can_invoice_history'")
        if not cursor.fetchone():
            print("➕ اضافه کردن ستون can_invoice_history...")
            safe_execute(
                cursor,
                "ALTER TABLE user_types ADD COLUMN can_invoice_history BOOLEAN DEFAULT 0 AFTER can_invoices",
            )

    # 2. جدول employee_data
    cursor.execute("SHOW TABLES LIKE 'employee_data'")
    if not cursor.fetchone():
        sql = """
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
        """
        safe_execute(cursor, sql)
        print("✅ جدول employee_data ایجاد شد")
        # اضافه کردن کاربر admin فقط اگر جدول جدید ایجاد شد
        cursor.execute("SELECT COUNT(*) FROM employee_data WHERE name = 'admin'")
        if cursor.fetchone()[0] == 0:
            safe_execute(
                cursor,
                """
                INSERT INTO employee_data 
                (empid, name, usertype, password)
                VALUES (1000, 'admin', 'ادمین', '1234')
            """,
            )
            print("✅ کاربر admin اضافه شد")
    else:
        print("✅ جدول employee_data از قبل موجود است")
        # فقط اگر کاربر admin وجود ندارد اضافه کن
        cursor.execute("SELECT COUNT(*) FROM employee_data WHERE name = 'admin'")
        if cursor.fetchone()[0] == 0:
            safe_execute(
                cursor,
                """
                INSERT INTO employee_data 
                (empid, name, usertype, password)
                VALUES (1000, 'admin', 'ادمین', '1234')
            """,
            )
            print("✅ کاربر admin اضافه شد (به جدول موجود)")

    # 3. سایر جداول (بدون DROP کردن)
    tables_def = [
        ("category_data", "id INT PRIMARY KEY, name VARCHAR(100), description TEXT"),
        (
            "supplier_data",
            "invoice INT PRIMARY KEY, name VARCHAR(100), contact VARCHAR(15), description TEXT",
        ),
        (
            "product_data",
            "id INT AUTO_INCREMENT PRIMARY KEY, category VARCHAR(50), supplier VARCHAR(50), name VARCHAR(100), price DECIMAL(10,2), quantity INT, status VARCHAR(50)",
        ),
        (
            "shift_data",
            "shift_id INT PRIMARY KEY AUTO_INCREMENT, shift_name VARCHAR(100) NOT NULL UNIQUE, start_time VARCHAR(10) NOT NULL, end_time VARCHAR(10) NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        ),
    ]

    for table_name, columns in tables_def:
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        if not cursor.fetchone():
            safe_execute(cursor, f"CREATE TABLE {table_name} ({columns})")
            print(f"✅ جدول {table_name} ایجاد شد")
        else:
            print(f"✅ جدول {table_name} از قبل موجود است")


def initialize_system():
    """راه‌اندازی سیستم - بدون حذف داده‌های قبلی"""
    print("=" * 50)
    print("🚀 سیستم فروش و انبارداری")
    print("=" * 50)
    print("🔧 در حال بررسی سیستم...")

    # 1. ایجاد دیتابیس
    if not check_and_create_database():
        return False

    cursor, connection = connect_database()
    if not cursor or not connection:
        return False

    try:
        cursor.execute("USE inventory_system")

        # 2. بررسی و اصلاح جداول (بدون حذف داده‌ها)
        check_table_structure(cursor)

        connection.commit()

        # 3. نمایش وضعیت
        print("\n📊 وضعیت سیستم:")

        # تعداد کاربران
        cursor.execute("SELECT COUNT(*) FROM employee_data")
        user_count = cursor.fetchone()[0]
        print(f"👥 تعداد کاربران: {user_count}")

        if user_count > 0:
            cursor.execute("SELECT name, usertype FROM employee_data ORDER BY name")
            users = cursor.fetchall()
            print("📋 لیست کاربران:")
            for user in users:
                print(f"  • {user[0]} ({user[1]})")

        # تعداد انواع کاربری
        cursor.execute("SELECT COUNT(*) FROM user_types")
        type_count = cursor.fetchone()[0]
        print(f"🎭 تعداد انواع کاربری: {type_count}")

        print("\n✅ سیستم آماده است")
        return True

    except Exception as e:
        print(f"❌ خطا در راه‌اندازی: {e}")
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
        cursor.execute("USE inventory_system")

        sql = """
            SELECT 
                e.empid, 
                e.name, 
                e.usertype,
                COALESCE(ut.can_employees, 0),
                COALESCE(ut.can_shifts, 0),
                COALESCE(ut.can_user_types, 0),
                COALESCE(ut.can_suppliers, 0),
                COALESCE(ut.can_categories, 0),
                COALESCE(ut.can_products, 0),
                COALESCE(ut.can_invoices, 0),
                COALESCE(ut.can_invoice_history, 0)
            FROM employee_data e
            LEFT JOIN user_types ut ON e.usertype = ut.type_name
            WHERE TRIM(e.name) = TRIM(%s) AND e.password = %s
        """

        cursor.execute(sql, (username, password))
        user = cursor.fetchone()

        if user:
            return {
                "id": user[0],
                "name": user[1],
                "user_type": user[2],
                "permissions": {
                    "employees": bool(user[3]),
                    "shifts": bool(user[4]),
                    "user_types": bool(user[5]),
                    "suppliers": bool(user[6]),
                    "categories": bool(user[7]),
                    "products": bool(user[8]),
                    "invoices": bool(user[9]),
                    "invoice_history": bool(user[10]),
                },
            }

        return None

    except Exception as e:
        print(f"❌ خطا در get_user_info: {e}")
        return None


def get_shifts_from_db():
    """دریافت لیست شیفت‌ها"""
    cursor, connection = connect_database()
    if not cursor or not connection:
        return []

    try:
        cursor.execute("USE inventory_system")
        cursor.execute("SELECT shift_name FROM shift_data")
        shifts = cursor.fetchall()
        return [s[0] for s in shifts]
    except Exception as e:
        print(f"❌ خطا در get_shifts_from_db: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def get_count(table_name):
    cursor, connection = connect_database()
    if not cursor or not connection:
        return 0

    try:
        cursor.execute("USE inventory_system")
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        return count
    except:
        return 0
    finally:
        cursor.close()
        connection.close()
