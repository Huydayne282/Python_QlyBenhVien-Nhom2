# login.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk


class LoginForm(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#e3f2fd")

        # Load logo
        try:
            logo = Image.open("logo.png").resize((260, 160), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(logo)
            logo_label = tk.Label(self, image=self.logo_img, bg="#e3f2fd")
            logo_label.pack(pady=(50, 20))
        except Exception as e:
            print(f"Không thể load ảnh: {e}")
            # Fallback logo
            logo_frame = tk.Frame(self, bg="#e3f2fd", width=260, height=160)
            logo_frame.pack(pady=(50, 20))
            logo_frame.pack_propagate(False)

            canvas = tk.Canvas(logo_frame, width=260, height=160, bg="#007acc", highlightthickness=0)
            canvas.pack()
            canvas.create_oval(30, 10, 230, 150, fill="white", outline="white")
            canvas.create_text(130, 60, text="CMC", font=("Arial", 32, "bold"), fill="#007acc")
            canvas.create_text(130, 100, text="HOSPITAL", font=("Arial", 18, "bold"), fill="#007acc")

        # Form đăng nhập
        form = tk.Frame(self, bg="white", relief="solid", bd=3, padx=60, pady=50)
        form.pack(pady=30)
        tk.Label(form, text="ĐĂNG NHẬP HỆ THỐNG", font=("Arial", 20, "bold"),
                 bg="white", fg="#007acc").pack(pady=(0, 30))

        # Tài khoản
        tk.Label(form, text="Tài khoản:", font=("Arial", 14), bg="white").pack(anchor="w", padx=30)
        self.entry_user = tk.Entry(form, font=("Arial", 14), width=30)
        self.entry_user.pack(pady=10, padx=30)

        # Mật khẩu
        tk.Label(form, text="Mật khẩu:", font=("Arial", 14), bg="white").pack(anchor="w", padx=30)
        self.entry_pass = tk.Entry(form, font=("Arial", 14), width=30, show="*")
        self.entry_pass.pack(pady=10, padx=30)

        # Checkbox hiển thị mật khẩu
        self.show_pass = tk.BooleanVar()
        show_pass_btn = tk.Checkbutton(form, text="Hiển thị mật khẩu",
                                       variable=self.show_pass, bg="white",
                                       command=self.toggle_password,
                                       font=("Arial", 10))
        show_pass_btn.pack(pady=5)

        # Nút đăng nhập
        self.login_btn = tk.Button(form, text="ĐĂNG NHẬP", font=("Arial", 14, "bold"), bg="#007acc",
                                   fg="white", width=25, height=2, command=self.login)
        self.login_btn.pack(pady=30)

        # Label hiển thị lỗi
        self.error = tk.Label(form, text="", fg="red", bg="white", font=("Arial", 12))
        self.error.pack()

        # Bind events
        self.entry_user.bind('<KeyPress>', self.clear_error)
        self.entry_pass.bind('<KeyPress>', self.clear_error)
        self.entry_pass.bind('<Return>', lambda e: self.login())

        # Focus vào ô username
        self.entry_user.focus_set()

    def clear_error(self, event=None):
        """Xóa thông báo lỗi khi user bắt đầu gõ"""
        self.error.config(text="")

    def toggle_password(self):
        """Ẩn/hiện mật khẩu"""
        if self.show_pass.get():
            self.entry_pass.config(show="")
        else:
            self.entry_pass.config(show="*")

    def login(self):
        """Xử lý đăng nhập"""
        # Clear error trước
        self.error.config(text="")

        # Validate
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not username or not password:
            self.error.config(text="Vui lòng nhập đầy đủ thông tin!")
            return

        # Hiệu ứng loading
        original_text = self.login_btn.cget("text")
        self.login_btn.config(text="ĐANG XỬ LÝ...", state="disabled")

        # Giả lập loading và xử lý đăng nhập
        self.after(500, self.process_login, username, password, original_text)

    def process_login(self, username, password, original_text):
        """Xử lý đăng nhập sau khi loading"""
        if username == "nhom2" and password == "36":
            self.controller.show_frame("Dashboard")
        else:
            self.error.config(text="Sai tài khoản hoặc mật khẩu!")

        # Khôi phục nút
        self.login_btn.config(text=original_text, state="normal")
