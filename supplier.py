from tkinter import *

def supplier_form(window):
    print("Supplier button clicked!")   # ← این خط را اضافه کن فقط برای تست
    win = Toplevel(window)
    win.title("تامین‌کنندگان")
    win.geometry("800x500")
    win.resizable(False, False)

    Label(win, text="صفحه تامین‌کنندگان", font=('Arial', 20)).pack(pady=20)
