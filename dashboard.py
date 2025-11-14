# dashboard.py
import tkinter as tk
from database import execute_query, rows_to_list
from datetime import datetime

class Dashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#e3f2fd")

        tk.Label(self, text="CMC University", font=("Arial", 36, "bold"),
                 fg="#007acc", bg="#e3f2fd").pack(pady=30)
        tk.Label(self, text="Bài tập lớn - Nhóm 2", font=("Arial", 16),
                 bg="#e3f2fd").pack(pady=10)

        stats = tk.Frame(self, bg="#e3f2fd")
        stats.pack(expand=True)
        inner = tk.Frame(stats, bg="#e3f2fd")
        inner.pack(expand=True)

        self.labels = []
        titles = ["Tổng BN", "Bác sĩ", "Phòng", "Lịch hôm nay", "Chưa khám", "Đã khám", "Đã hủy"]
        colors = ["#3498db", "#2ecc71", "#f1c40f", "#e67e22", "#9b59b6", "#27ae60", "#e74c3c"]

        for i in range(7):
            f = tk.Frame(inner, bg="white", relief="solid", bd=2, padx=40, pady=30)
            f.pack(side="left", padx=20)
            tk.Label(f, text=titles[i], font=("Arial", 12), bg="white").pack()
            lbl = tk.Label(f, text="0", font=("Arial", 36, "bold"), fg=colors[i], bg="white")
            lbl.pack()
            self.labels.append(lbl)

        menu = tk.Frame(self, bg="#e3f2fd")
        menu.pack(side="bottom", pady=50)

        buttons = [
            ("Quản lý BN", "BenhNhanForm", "#3498db"),
            ("Quản lý BS", "BacSiForm", "#2ecc71"),
            ("Phòng khám", "PhongKhamForm", "#f39c12"),
            ("Lịch khám", "LichKhamForm", "#e67e22"),
            ("Tra cứu", "TraCuuForm", "#9b59b6"),
            ("Báo cáo", "BaoCaoForm", "#1abc9c"),
            ("Đăng xuất", "LoginForm", "#95a5a6")
        ]

        for text, page, color in buttons:
            tk.Button(menu, text=text, bg=color, fg="white", width=18, height=2,
                      font=("Arial", 11, "bold"),
                      command=lambda p=page: controller.show_frame(p)).pack(side="left", padx=10)

    def refresh(self):
        today = datetime.now().strftime("%Y-%m-%d")
        bn = len(rows_to_list(execute_query("SELECT * FROM BenhNhan", fetch=True)))
        bs = len(rows_to_list(execute_query("SELECT * FROM BacSi", fetch=True)))
        pk = len(rows_to_list(execute_query("SELECT * FROM PhongKham", fetch=True)))
        lk_today = len(rows_to_list(execute_query(
            f"SELECT * FROM LichKham WHERE CAST(NgayGioKham AS DATE) = '{today}' AND TrangThai != N'Đã hủy'",
            fetch=True)))
        chua = len(rows_to_list(execute_query("SELECT * FROM LichKham WHERE TrangThai = N'Chưa khám'", fetch=True)))
        da = len(rows_to_list(execute_query("SELECT * FROM LichKham WHERE TrangThai = N'Đã khám'", fetch=True)))
        huy = len(rows_to_list(execute_query("SELECT * FROM LichKham WHERE TrangThai = N'Đã hủy'", fetch=True)))

        for lbl, val in zip(self.labels, [bn, bs, pk, lk_today, chua, da, huy]):
            lbl.config(text=str(val))