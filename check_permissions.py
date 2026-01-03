# check_permissions.py
from database import connect_database


def get_user_permissions(user_type_name):
    """دریافت دسترسی‌های یک نوع کاربری"""
    cursor, connection = connect_database()
    if not cursor or not connection:
        return None

    try:
        cursor.execute('USE inventory_system')
        cursor.execute('''
            SELECT can_employees, can_shifts, can_user_types,
                   can_suppliers, can_categories, can_products,
                   can_invoices, can_invoice_history  # ❗ فقط 8 ستون
            FROM user_types WHERE type_name = %s
        ''', (user_type_name,))

        result = cursor.fetchone()
        return result if result else (0, 0, 0, 0, 0, 0, 0, 0)  # ❗ 8 تا صفر

    except Exception as e:
        # فقط خطاهای واقعی را نمایش بده
        import traceback
        error_msg = str(e)
        if "can_invoice_history" in error_msg:
            # ستون وجود ندارد، مقادیر پیش‌فرض برگردان
            return (0, 0, 0, 0, 0, 0, 0, 0)  # ❗ 8 تا صفر
        return (0, 0, 0, 0, 0, 0, 0, 0)  # ❗ 8 تا صفر
    finally:
        cursor.close()
        connection.close()


def can_access(user_type_name, permission_name):
    """بررسی دسترسی کاربر به یک قابلیت"""
    permissions = get_user_permissions(user_type_name)
    if not permissions:
        return False

    permission_map = {
        'employees': 0,
        'shifts': 1,
        'user_types': 2,
        'suppliers': 3,
        'categories': 4,
        'products': 5,
        'invoices': 6,           # ❗ قبلاً 7 بود
        'invoice_history': 7     # ❗ قبلاً 8 بود
    }

    index = permission_map.get(permission_name, -1)
    return permissions[index] == 1 if index >= 0 else False