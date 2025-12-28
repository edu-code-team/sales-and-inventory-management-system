# login.py (نسخه تمیز)
from tkinter import *
from tkinter import messagebox
from database import initialize_system, get_user_info
from dashboard import main as dashboard_main


class LoginSystem:
    def __init__(self):
        # راه‌اندازی سیستم
        if not initialize_system():
            messagebox.showerror("خطا", "خطا در راه‌اندازی سیستم")
            return

        self.setup_window()
        self.setup_ui()

    def setup_window(self):
        self.window = Tk()
        self.window.title("سیستم فروش و انبارداری")
        self.window.geometry("400x400")
        self.window.configure(bg='white')
        self.window.resizable(False, False)

        # مرکز کردن
        self.window.update_idletasks()
        width = 400
        height = 400
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        # عنوان
        Label(self.window, text="سیستم فروش و انبارداری",
              font=('B Nazanin', 18, 'bold'),
              bg='white', fg='#00198f').pack(pady=20)

        Label(self.window, text="ورود به سیستم",
              font=('B Nazanin', 14),
              bg='white', fg='#666').pack(pady=(0, 20))

        # فرم
        self.create_form()

        # دکمه‌ها
        self.create_buttons()

        # اطلاعات
        self.create_info_box()

        # کلیدهای کیبورد
        self.window.bind('<Return>', lambda e: self.login())
        self.window.bind('<Escape>', lambda e: self.window.destroy())

    def create_form(self):
        form_frame = Frame(self.window, bg='white')
        form_frame.pack(pady=20)

        # نام کاربری
        Label(form_frame, text="نام کاربری:",
              font=('B Nazanin', 12),
              bg='white').grid(row=0, column=0, padx=10, pady=10, sticky='e')

        self.username_entry = Entry(form_frame,
                                    font=('B Nazanin', 12),
                                    bg='#f0f8ff',
                                    width=25,
                                    relief=SOLID,
                                    bd=1)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)
        self.username_entry.focus_set()
        self.username_entry.insert(0, 'admin')

        # رمز عبور
        Label(form_frame, text="رمز عبور:",
              font=('B Nazanin', 12),
              bg='white').grid(row=1, column=0, padx=10, pady=10, sticky='e')

        self.password_entry = Entry(form_frame,
                                    font=('B Nazanin', 12),
                                    bg='#f0f8ff',
                                    width=25,
                                    show="•",
                                    relief=SOLID,
                                    bd=1)
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)
        self.password_entry.insert(0, '1234')

        # نمایش رمز
        self.show_pass_var = IntVar()
        Checkbutton(form_frame,
                    text="نمایش رمز عبور",
                    variable=self.show_pass_var,
                    font=('B Nazanin', 10),
                    bg='white',
                    command=self.toggle_password).grid(row=2, column=1, sticky='w', padx=10, pady=5)

    def create_buttons(self):
        button_frame = Frame(self.window, bg='white')
        button_frame.pack(pady=20)

        Button(button_frame, text="🔓 ورود به سیستم",
               font=('B Nazanin', 12, 'bold'),
               bg='#28a745', fg='white',
               width=18, height=1,
               relief=RAISED,
               bd=2,
               cursor='hand2',
               command=self.login).pack(side=LEFT, padx=10)

        Button(button_frame, text="❌ خروج از برنامه",
               font=('B Nazanin', 12, 'bold'),
               bg='#dc3545', fg='white',
               width=18, height=1,
               relief=RAISED,
               bd=2,
               cursor='hand2',
               command=self.window.destroy).pack(side=LEFT, padx=10)

    def create_info_box(self):
        info_frame = Frame(self.window, bg='#d4edda', relief=SOLID, bd=1)
        info_frame.pack(pady=10, fill=X, padx=20)

        info_text = """👤 کاربر پیش‌فرض:
نام کاربری: admin
رمز عبور: 1234
نوع کاربری: ادمین"""

        Label(info_frame, text=info_text,
              font=('B Nazanin', 10),
              bg='#d4edda', fg='#155724',
              justify=LEFT).pack(padx=10, pady=8)

    def toggle_password(self):
        if self.show_pass_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="•")

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("خطا", "لطفاً نام کاربری و رمز عبور را وارد کنید")
            return

        user_info = get_user_info(username, password)

        if not user_info:
            messagebox.showerror("خطا", "نام کاربری یا رمز عبور اشتباه است")
            self.password_entry.delete(0, END)
            self.username_entry.focus_set()
            return

        # خوش‌آمدگویی
        messagebox.showinfo("ورود موفق",
                            f"✅ خوش آمدید {user_info['name']}\n\n"
                            f"👤 نوع کاربری: {user_info['user_type']}")

        # بستن لاگین و باز کردن داشبورد
        self.window.destroy()
        dashboard_main(user_info)

    def run(self):
        self.window.mainloop()


# اجرا
if __name__ == "__main__":
    print("=" * 50)
    print("سیستم فروش و انبارداری")
    print("=" * 50)

    app = LoginSystem()
    app.run()