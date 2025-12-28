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
                   can_sales, can_invoices, can_invoice_history
            FROM user_types WHERE type_name = %s
        ''', (user_type_name,))

        result = cursor.fetchone()
        return result if result else (0, 0, 0, 0, 0, 0, 0, 0, 0)

    except Exception as e:
        # فقط خطاهای واقعی را نمایش بده
        import traceback
        error_msg = str(e)
        if "can_invoice_history" in error_msg:
            # ستون وجود ندارد، مقادیر پیش‌فرض برگردان
            return (0, 0, 0, 0, 0, 0, 0, 0, 0)
        return (0, 0, 0, 0, 0, 0, 0, 0, 0)
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
        'sales': 6,
        'invoices': 7,
        'invoice_history': 8
    }

    index = permission_map.get(permission_name, -1)
    return permissions[index] == 1 if index >= 0 else False