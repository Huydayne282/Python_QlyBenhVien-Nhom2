# baocao.py
import tkinter as tk
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database import execute_query

class BaoCaoForm(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f5f5f5")

        header = tk.Frame(self, bg="#1abc9c", height=80)
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="BÁO CÁO - THỐNG KÊ",
                 font=("Arial", 24, "bold"), bg="#1abc9c", fg="white").pack(pady=20)

        btns = tk.Frame(self, bg="#f5f5f5")
        btns.pack(pady=15)
        tk.Button(btns, text="Thống kê tuần", command=self.thongke_tuan,
                  bg="#3498db", fg="white", font=("Arial", 11, "bold"),
                  width=18, height=2).pack(side="left", padx=10)
        tk.Button(btns, text="Thống kê tháng", command=self.thongke_thang,
                  bg="#2ecc71", fg="white", font=("Arial", 11, "bold"),
                  width=18, height=2).pack(side="left", padx=10)
        tk.Button(btns, text="Quay lại", command=lambda: controller.show_frame("Dashboard"),
                  bg="#6c757d", fg="white", font=("Arial", 11, "bold"),
                  width=18, height=2).pack(side="left", padx=10)

        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)

    def thongke_tuan(self):
        today = datetime.now()
        start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        end = (today + timedelta(days=6 - today.weekday())).strftime("%Y-%m-%d")
        self.ve_bieu_do(start, end, "Thống kê tuần")

    def thongke_thang(self):
        today = datetime.now()
        start = today.strftime("%Y-%m-01")
        year_month = today.strftime("%Y-%m")
        end = (datetime.strptime(f"{year_month}-01", "%Y-%m-%d") + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        end = end.strftime("%Y-%m-%d")
        self.ve_bieu_do(start, end, "Thống kê tháng")

    def ve_bieu_do(self, start, end, title):
        query = """
            SELECT TrangThai, COUNT(*) FROM LichKham 
            WHERE NgayGioKham BETWEEN ? AND ? 
            GROUP BY TrangThai
        """
        data = execute_query(query, (f"{start} 00:00", f"{end} 23:59"), fetch=True)

        labels = ["Chưa khám", "Đã khám", "Đã hủy"]
        sizes = [0, 0, 0]
        colors = ["#ffc107", "#28a745", "#dc3545"]

        for row in data:
            if "Chưa" in str(row[0]):
                sizes[0] = row[1]
            elif "Đã khám" in str(row[0]):
                sizes[1] = row[1]
            elif "hủy" in str(row[0]):
                sizes[2] = row[1]

        self.ax.clear()

        if sum(sizes) > 0:
            self.ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors,
                        startangle=90, textprops={'fontsize': 12, 'weight': 'bold'})
            self.ax.set_title(f"{title} ({start} → {end})", fontsize=14, weight='bold', pad=20)
        else:
            self.ax.text(0.5, 0.5, 'Không có dữ liệu', ha='center', va='center',
                         fontsize=16, transform=self.ax.transAxes)
            self.ax.set_title(f"{title} ({start} → {end})", fontsize=14, weight='bold', pad=20)

        self.canvas.draw()