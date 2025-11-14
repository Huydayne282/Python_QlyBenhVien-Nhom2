# login.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class LoginForm(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#e3f2fd")

        try:
            logo = Image.open("assets/cmc_logo.png").resize((260, 160), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(logo)
            tk.Label(self, image=self.logo_img, bg="#e3f2fd").pack(pady=(50, 20))
        except:
            tk.Label(self, text="CMC University", font=("Arial", 36, "bold"),
                     fg="#007acc", bg="#e3f2fd").pack(pady=(50, 10))

        form = tk.Frame(self, bg="white", relief="solid", bd=3, padx=60, pady=50)
        form.pack(pady=30)
        tk.Label(form, text="ĐĂNG NHẬP HỆ THỐNG", font=("Arial", 20, "bold"),
                 bg="white", fg="#007acc").pack(pady=(0, 30))

        tk.Label(form, text="Tài khoản:", font=("Arial", 14), bg="white").pack(anchor="w", padx=30)
        self.entry_user = tk.Entry(form, font=("Arial", 14), width=30)
        self.entry_user.pack(pady=10, padx=30)

        tk.Label(form, text="Mật khẩu:", font=("Arial", 14), bg="white").pack(anchor="w", padx=30)
        self.entry_pass = tk.Entry(form, font=("Arial", 14), width=30, show="*")
        self.entry_pass.pack(pady=10, padx=30)

        tk.Button(form, text="ĐĂNG NHẬP", font=("Arial", 14, "bold"), bg="#007acc",
                  fg="white", width=25, height=2, command=self.login).pack(pady=30)

        self.error = tk.Label(form, text="", fg="red", bg="white", font=("Arial", 12))
        self.error.pack()

    def login(self):
        if self.entry_user.get() == "nhom2" and self.entry_pass.get() == "36":
            self.controller.show_frame("Dashboard")
        else:
            self.error.config(text="Sai tài khoản hoặc mật khẩu!")