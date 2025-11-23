# main.py
import tkinter as tk
from login import LoginForm
from dashboard import Dashboard
from benhnhan import BenhNhanForm
from bacsi import BacSiForm
from phongkham import PhongKhamForm
from lichkham import LichKhamForm
from tracuu import TraCuuForm
from baocao import BaoCaoForm


class HospitalPython(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CMC University - Hệ thống Quản lý Bệnh viện")
        self.state('zoomed')
        self.configure(bg="#f0f0f0")

        # Thiết lập icon (nếu có)
        try:
            self.iconbitmap("hospital_icon.ico")  # Thay bằng đường dẫn icon của bạn
        except:
            pass  # Bỏ qua nếu không có icon

        container = tk.Frame(self)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Danh sách các form
        forms = [
            LoginForm, Dashboard, BenhNhanForm, BacSiForm,
            PhongKhamForm, LichKhamForm, TraCuuForm, BaoCaoForm
        ]

        for F in forms:
            frame_name = F.__name__
            frame = F(container, self)
            self.frames[frame_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginForm")

        # Xử lý sự kiện đóng cửa sổ
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def show_frame(self, name):
        """Hiển thị frame và refresh nếu có method refresh"""
        frame = self.frames[name]
        frame.tkraise()

        # Gọi refresh nếu frame có method refresh
        if hasattr(frame, 'refresh'):
            try:
                frame.refresh()
            except Exception as e:
                print(f"Lỗi khi refresh frame {name}: {e}")

        # Cập nhật title tùy theo frame
        self.update_title(name)

    def update_title(self, frame_name):
        """Cập nhật title của cửa sổ dựa trên frame hiện tại"""
        titles = {
            "LoginForm": "Đăng nhập - Hệ thống Quản lý Bệnh viện",
            "Dashboard": "Bảng điều khiển - Hệ thống Quản lý Bệnh viện",
            "BenhNhanForm": "Quản lý Bệnh nhân - Hệ thống Quản lý Bệnh viện",
            "BacSiForm": "Quản lý Bác sĩ - Hệ thống Quản lý Bệnh viện",
            "PhongKhamForm": "Quản lý Phòng khám - Hệ thống Quản lý Bệnh viện",
            "LichKhamForm": "Quản lý Lịch khám - Hệ thống Quản lý Bệnh viện",
            "TraCuuForm": "Tra cứu - Hệ thống Quản lý Bệnh viện",
            "BaoCaoForm": "Báo cáo - Hệ thống Quản lý Bệnh viện"
        }
        self.title(titles.get(frame_name, "Hệ thống Quản lý Bệnh viện"))

    def on_closing(self):
        """Xử lý sự kiện đóng cửa sổ"""
        if messagebox.askokcancel("Thoát", "Bạn có chắc chắn muốn thoát chương trình?"):
            self.destroy()

    def get_current_frame(self):
        """Lấy frame hiện tại đang hiển thị"""
        for frame in self.frames.values():
            if frame.winfo_ismapped():
                return frame
        return None


# Thêm import messagebox nếu cần
from tkinter import messagebox

if __name__ == "__main__":
    try:
        app = HospitalPython()
        app.mainloop()
    except Exception as e:
        print(f"Lỗi khởi chạy ứng dụng: {e}")
        messagebox.showerror("Lỗi", f"Không thể khởi chạy ứng dụng: {e}")
