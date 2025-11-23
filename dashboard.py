# dashboard.py
import tkinter as tk
from tkinter import ttk
from database import execute_query, rows_to_list
from datetime import datetime
from PIL import Image, ImageTk
import os


class Dashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#e3f2fd")

        # Header với logo và tiêu đề
        header_frame = tk.Frame(self, bg="#007acc", height=120)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)

        # Tạo logo (có thể thay bằng ảnh thực tế)
        logo_frame = tk.Frame(header_frame, bg="#007acc")
        logo_frame.pack(side="left", padx=30, pady=20)

        # Tạo hình tròn màu trắng làm logo
        logo_canvas = tk.Canvas(logo_frame, width=60, height=60, bg="#007acc", highlightthickness=0)
        logo_canvas.pack()
        logo_canvas.create_oval(5, 5, 55, 55, fill="white", outline="white")
        logo_canvas.create_text(30, 30, text="+", font=("Arial", 24, "bold"), fill="#007acc")

        # Tiêu đề
        title_frame = tk.Frame(header_frame, bg="#007acc")
        title_frame.pack(side="left", padx=10, pady=30)

        tk.Label(title_frame, text="CMC Hospital", font=("Arial", 36, "bold"),
                 fg="white", bg="#007acc").pack()
        tk.Label(title_frame, text="Bài tập lớn - Nhóm 2", font=("Arial", 14),
                 fg="white", bg="#007acc").pack()

        # Frame chính chứa thống kê và menu
        main_frame = tk.Frame(self, bg="#e3f2fd")
        main_frame.pack(expand=True, fill="both", padx=20, pady=10)

        # Frame thống kê
        stats_frame = tk.LabelFrame(main_frame, text=" THỐNG KÊ HỆ THỐNG ",
                                    font=("Arial", 14, "bold"), bg="#e3f2fd",
                                    fg="#007acc", relief="solid", bd=2)
        stats_frame.pack(fill="x", pady=(0, 20))

        # Biểu tượng cho các thống kê (có thể thay bằng ảnh thực tế)
        icons = ["👥", "👨‍⚕️", "🏥", "📅", "⏳", "✅", "❌"]
        self.labels = []
        titles = ["Tổng BN", "Bác sĩ", "Phòng", "Lịch hôm nay", "Chưa khám", "Đã khám", "Đã hủy"]
        colors = ["#3498db", "#2ecc71", "#f1c40f", "#e67e22", "#9b59b6", "#27ae60", "#e74c3c"]

        stats_inner = tk.Frame(stats_frame, bg="#e3f2fd")
        stats_inner.pack(padx=20, pady=15)

        for i in range(7):
            f = tk.Frame(stats_inner, bg="white", relief="raised", bd=1,
                         padx=15, pady=10)
            f.grid(row=0, column=i, padx=8, sticky="nsew")

            # Biểu tượng
            icon_label = tk.Label(f, text=icons[i], font=("Arial", 20),
                                  bg="white")
            icon_label.pack()

            # Tiêu đề
            tk.Label(f, text=titles[i], font=("Arial", 10, "bold"),
                     bg="white").pack()

            # Số liệu
            lbl = tk.Label(f, text="0", font=("Arial", 24, "bold"),
                           fg=colors[i], bg="white")
            lbl.pack()
            self.labels.append(lbl)

        # Cân bằng các cột
        for i in range(7):
            stats_inner.columnconfigure(i, weight=1)

        # Frame menu chức năng
        menu_frame = tk.LabelFrame(main_frame, text=" CHỨC NĂNG HỆ THỐNG ",
                                   font=("Arial", 14, "bold"), bg="#e3f2fd",
                                   fg="#007acc", relief="solid", bd=2)
        menu_frame.pack(fill="both", expand=True)

        # Danh sách nút chức năng với biểu tượng
        buttons = [
            ("👥 Quản lý BN", "BenhNhanForm", "#3498db"),
            ("👨‍⚕️ Quản lý BS", "BacSiForm", "#2ecc71"),
            ("🏥 Phòng khám", "PhongKhamForm", "#f39c12"),
            ("📅 Lịch khám", "LichKhamForm", "#e67e22"),
            ("🔍 Tra cứu", "TraCuuForm", "#9b59b6"),
            ("📊 Báo cáo", "BaoCaoForm", "#1abc9c"),
            ("🚪 Đăng xuất", "LoginForm", "#95a5a6")
        ]

        menu_inner = tk.Frame(menu_frame, bg="#e3f2fd")
        menu_inner.pack(expand=True, padx=20, pady=20)

        # Tạo 2 hàng cho menu
        for i, (text, page, color) in enumerate(buttons):
            row = i // 4  # 4 nút mỗi hàng
            col = i % 4

            btn = tk.Button(menu_inner, text=text, bg=color, fg="white",
                            width=16, height=2, font=("Arial", 11, "bold"),
                            command=lambda p=page: controller.show_frame(p),
                            relief="raised", bd=2)
            btn.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        # Cân bằng layout cho menu
        for i in range(4):
            menu_inner.columnconfigure(i, weight=1)
        for i in range(2):
            menu_inner.rowconfigure(i, weight=1)

        # Footer
        footer_frame = tk.Frame(self, bg="#007acc", height=40)
        footer_frame.pack(fill="x", side="bottom")
        footer_frame.pack_propagate(False)

        tk.Label(footer_frame, text="© 2025 CMC Hospital - Hệ thống quản lý bệnh viện",
                 font=("Arial", 10), fg="white", bg="#007acc").pack(pady=10)

        # Làm mới dữ liệu khi khởi tạo
        self.refresh()

    def refresh(self):
        """Làm mới dữ liệu thống kê"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")

            # Lấy dữ liệu từ database
            bn = len(rows_to_list(execute_query("SELECT * FROM BENHNHAN", fetch=True)))
            bs = len(rows_to_list(execute_query("SELECT * FROM BACSI", fetch=True)))
            pk = len(rows_to_list(execute_query("SELECT * FROM PHONGKHAM", fetch=True)))

            lk_today = len(rows_to_list(execute_query(
                f"SELECT * FROM LichKham WHERE CAST(NgayGioKham AS DATE) = '{today}' AND TrangThai != N'Đã hủy'",
                fetch=True)))

            chua = len(rows_to_list(execute_query("SELECT * FROM LichKham WHERE TrangThai = N'Chưa khám'", fetch=True)))
            da = len(rows_to_list(execute_query("SELECT * FROM LichKham WHERE TrangThai = N'Đã khám'", fetch=True)))
            huy = len(rows_to_list(execute_query("SELECT * FROM LichKham WHERE TrangThai = N'Đã hủy'", fetch=True)))

            # Cập nhật labels
            for lbl, val in zip(self.labels, [bn, bs, pk, lk_today, chua, da, huy]):
                lbl.config(text=str(val))

        except Exception as e:
            print(f"Lỗi khi làm mới dashboard: {e}")
