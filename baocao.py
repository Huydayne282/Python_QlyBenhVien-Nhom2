# baocao.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database import execute_query, rows_to_list


class BaoCaoForm(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f5f5f5")

        header = tk.Frame(self, bg="#1abc9c", height=80)
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="BÁO CÁO - THỐNG KÊ",
                 font=("Arial", 24, "bold"), bg="#1abc9c", fg="white").pack(pady=20)

        # Frame chứa các nút và tùy chọn
        control_frame = tk.Frame(self, bg="#f5f5f5")
        control_frame.pack(pady=15, padx=20, fill="x")

        # Nút thống kê
        btn_frame = tk.Frame(control_frame, bg="#f5f5f5")
        btn_frame.pack(side="left")

        tk.Button(btn_frame, text="Thống kê hôm nay", command=self.thongke_homnay,
                  bg="#e74c3c", fg="white", font=("Arial", 11, "bold"),
                  width=18, height=2).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Thống kê tuần", command=self.thongke_tuan,
                  bg="#3498db", fg="white", font=("Arial", 11, "bold"),
                  width=18, height=2).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Thống kê tháng", command=self.thongke_thang,
                  bg="#2ecc71", fg="white", font=("Arial", 11, "bold"),
                  width=18, height=2).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Thống kê tùy chọn", command=self.thongke_tuychon,
                  bg="#9b59b6", fg="white", font=("Arial", 11, "bold"),
                  width=18, height=2).pack(side="left", padx=5)

        # Nút quay lại
        tk.Button(control_frame, text="Quay lại", command=lambda: controller.show_frame("Dashboard"),
                  bg="#6c757d", fg="white", font=("Arial", 11, "bold"),
                  width=18, height=2).pack(side="right", padx=5)

        # Frame hiển thị thông tin tổng quan
        self.info_frame = tk.Frame(self, bg="white", relief="solid", bd=1)
        self.info_frame.pack(fill="x", padx=20, pady=10)

        # Tạo labels cho thông tin
        self.lbl_tong_lich = tk.Label(self.info_frame, text="Tổng số lịch: 0",
                                      font=("Arial", 12, "bold"), bg="white", fg="#2c3e50")
        self.lbl_tong_lich.pack(side="left", padx=20, pady=10)

        self.lbl_chua_kham = tk.Label(self.info_frame, text="Chưa khám: 0",
                                      font=("Arial", 12), bg="white", fg="#ffc107")
        self.lbl_chua_kham.pack(side="left", padx=20, pady=10)

        self.lbl_da_kham = tk.Label(self.info_frame, text="Đã khám: 0",
                                    font=("Arial", 12), bg="white", fg="#28a745")
        self.lbl_da_kham.pack(side="left", padx=20, pady=10)

        self.lbl_da_huy = tk.Label(self.info_frame, text="Đã hủy: 0",
                                   font=("Arial", 12), bg="white", fg="#dc3545")
        self.lbl_da_huy.pack(side="left", padx=20, pady=10)

        # Tạo figure cho biểu đồ
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 5))
        self.fig.patch.set_facecolor('#f5f5f5')
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=10)

        # Hiển thị thống kê mặc định
        self.thongke_homnay()

    def cap_nhat_thong_tin(self, data):
        """Cập nhật thông tin tổng quan"""
        tong_lich = sum([row[1] for row in data])
        chua_kham = next((row[1] for row in data if "Chưa" in str(row[0])), 0)
        da_kham = next((row[1] for row in data if "Đã khám" in str(row[0])), 0)
        da_huy = next((row[1] for row in data if "hủy" in str(row[0])), 0)

        self.lbl_tong_lich.config(text=f"Tổng số lịch: {tong_lich}")
        self.lbl_chua_kham.config(text=f"Chưa khám: {chua_kham}")
        self.lbl_da_kham.config(text=f"Đã khám: {da_kham}")
        self.lbl_da_huy.config(text=f"Đã hủy: {da_huy}")

    def thongke_homnay(self):
        """Thống kê lịch khám trong ngày hôm nay"""
        today = datetime.now().strftime("%Y-%m-%d")
        start = f"{today} 00:00"
        end = f"{today} 23:59"
        self.ve_bieu_do(start, end, "Thống kê hôm nay")

    def thongke_tuan(self):
        """Thống kê lịch khám trong tuần"""
        today = datetime.now()
        start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        end = (today + timedelta(days=6 - today.weekday())).strftime("%Y-%m-%d")
        self.ve_bieu_do(f"{start} 00:00", f"{end} 23:59", "Thống kê tuần")

    def thongke_thang(self):
        """Thống kê lịch khám trong tháng"""
        today = datetime.now()
        start = today.strftime("%Y-%m-01")
        year_month = today.strftime("%Y-%m")
        end = (datetime.strptime(f"{year_month}-01", "%Y-%m-%d") + timedelta(days=32)).replace(day=1) - timedelta(
            days=1)
        end = end.strftime("%Y-%m-%d")
        self.ve_bieu_do(f"{start} 00:00", f"{end} 23:59", "Thống kê tháng")

    def thongke_tuychon(self):
        """Thống kê theo khoảng thời gian tùy chọn với combobox"""
        dialog = tk.Toplevel(self)
        dialog.title("Thống kê tùy chọn")
        dialog.geometry("600x400")  # TĂNG KÍCH THƯỚC Ở ĐÂY
        dialog.configure(bg="#f0f0f0")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        main_frame = tk.Frame(dialog, bg="white", relief="solid", bd=2)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(main_frame, text="CHỌN KHOẢNG THỜI GIAN",
                 font=("Arial", 16, "bold"), bg="white", fg="#1abc9c").pack(pady=20)

        # Frame chứa ngày bắt đầu
        start_frame = tk.LabelFrame(main_frame, text=" TỪ NGÀY ",
                                    font=("Arial", 12, "bold"), bg="white", fg="#2c3e50",
                                    relief="solid", bd=1)
        start_frame.pack(fill="x", padx=20, pady=15)

        # Combobox cho ngày bắt đầu - SỬA LẠI LAYOUT
        start_inner_frame = tk.Frame(start_frame, bg="white")
        start_inner_frame.pack(padx=10, pady=15)

        # Ngày
        tk.Label(start_inner_frame, text="Ngày:", font=("Arial", 12, "bold"),
                 bg="white").grid(row=0, column=0, padx=5, pady=8, sticky="w")

        start_day_combo = ttk.Combobox(start_inner_frame,
                                       values=[str(i).zfill(2) for i in range(1, 32)],
                                       state="readonly", font=("Arial", 12), width=5)  # GIẢM WIDTH
        start_day_combo.grid(row=0, column=1, padx=5, pady=8)
        start_day_combo.set(datetime.now().strftime("%d"))

        # Tháng
        tk.Label(start_inner_frame, text="Tháng:", font=("Arial", 12, "bold"),
                 bg="white").grid(row=0, column=2, padx=5, pady=8, sticky="w")

        start_month_combo = ttk.Combobox(start_inner_frame,
                                         values=[str(i).zfill(2) for i in range(1, 13)],
                                         state="readonly", font=("Arial", 12), width=5)  # GIẢM WIDTH
        start_month_combo.grid(row=0, column=3, padx=5, pady=8)
        start_month_combo.set(datetime.now().strftime("%m"))

        # Năm - THÊM DÒNG NÀY ĐỂ HIỂN THỊ
        tk.Label(start_inner_frame, text="Năm:", font=("Arial", 12, "bold"),
                 bg="white").grid(row=0, column=4, padx=5, pady=8, sticky="w")

        current_year = datetime.now().year
        start_year_combo = ttk.Combobox(start_inner_frame,
                                        values=[str(i) for i in range(current_year - 5, current_year + 6)],
                                        state="readonly", font=("Arial", 12), width=8)  # GIẢM WIDTH
        start_year_combo.grid(row=0, column=5, padx=5, pady=8)
        start_year_combo.set(str(current_year))

        # Frame chứa ngày kết thúc
        end_frame = tk.LabelFrame(main_frame, text=" ĐẾN NGÀY ",
                                  font=("Arial", 12, "bold"), bg="white", fg="#2c3e50",
                                  relief="solid", bd=1)
        end_frame.pack(fill="x", padx=20, pady=15)

        # Combobox cho ngày kết thúc - SỬA LẠI LAYOUT
        end_inner_frame = tk.Frame(end_frame, bg="white")
        end_inner_frame.pack(padx=10, pady=15)

        # Ngày
        tk.Label(end_inner_frame, text="Ngày:", font=("Arial", 12, "bold"),
                 bg="white").grid(row=0, column=0, padx=5, pady=8, sticky="w")

        end_day_combo = ttk.Combobox(end_inner_frame,
                                     values=[str(i).zfill(2) for i in range(1, 32)],
                                     state="readonly", font=("Arial", 12), width=5)  # GIẢM WIDTH
        end_day_combo.grid(row=0, column=1, padx=5, pady=8)
        end_day_combo.set(datetime.now().strftime("%d"))

        # Tháng
        tk.Label(end_inner_frame, text="Tháng:", font=("Arial", 12, "bold"),
                 bg="white").grid(row=0, column=2, padx=5, pady=8, sticky="w")

        end_month_combo = ttk.Combobox(end_inner_frame,
                                       values=[str(i).zfill(2) for i in range(1, 13)],
                                       state="readonly", font=("Arial", 12), width=5)  # GIẢM WIDTH
        end_month_combo.grid(row=0, column=3, padx=5, pady=8)
        end_month_combo.set(datetime.now().strftime("%m"))

        # Năm - THÊM DÒNG NÀY ĐỂ HIỂN THỊ
        tk.Label(end_inner_frame, text="Năm:", font=("Arial", 12, "bold"),
                 bg="white").grid(row=0, column=4, padx=5, pady=8, sticky="w")

        end_year_combo = ttk.Combobox(end_inner_frame,
                                      values=[str(i) for i in range(current_year - 5, current_year + 6)],
                                      state="readonly", font=("Arial", 12), width=8)  # GIẢM WIDTH
        end_year_combo.grid(row=0, column=5, padx=5, pady=8)
        end_year_combo.set(str(current_year))

        def xac_nhan():
            try:
                # Lấy giá trị từ combobox
                start_day = start_day_combo.get()
                start_month = start_month_combo.get()
                start_year = start_year_combo.get()

                end_day = end_day_combo.get()
                end_month = end_month_combo.get()
                end_year = end_year_combo.get()

                # Kiểm tra dữ liệu
                if not all([start_day, start_month, start_year, end_day, end_month, end_year]):
                    messagebox.showerror("Lỗi", "Vui lòng chọn đầy đủ ngày, tháng, năm!")
                    return

                # Tạo đối tượng datetime
                start_date = datetime(int(start_year), int(start_month), int(start_day))
                end_date = datetime(int(end_year), int(end_month), int(end_day))

                # Kiểm tra tính hợp lệ
                if start_date > end_date:
                    messagebox.showerror("Lỗi", "Ngày bắt đầu không được sau ngày kết thúc!")
                    return

                # Kiểm tra ngày trong tháng
                def is_valid_date(year, month, day):
                    try:
                        datetime(year, month, day)
                        return True
                    except ValueError:
                        return False

                if not is_valid_date(int(start_year), int(start_month), int(start_day)):
                    messagebox.showerror("Lỗi", f"Ngày {start_day}/{start_month}/{start_year} không hợp lệ!")
                    return

                if not is_valid_date(int(end_year), int(end_month), int(end_day)):
                    messagebox.showerror("Lỗi", f"Ngày {end_day}/{end_month}/{end_year} không hợp lệ!")
                    return

                # Chuyển đổi sang chuỗi
                start_str = start_date.strftime("%Y-%m-%d 00:00")
                end_str = end_date.strftime("%Y-%m-%d 23:59")
                title = f"Thống kê từ {start_day}/{start_month}/{start_year} đến {end_day}/{end_month}/{end_year}"

                dialog.destroy()
                self.ve_bieu_do(start_str, end_str, title)

            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xử lý ngày tháng: {str(e)}")

        # Nút điều khiển
        btn_frame = tk.Frame(main_frame, bg="white")
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="XÁC NHẬN", command=xac_nhan,
                  bg="#1abc9c", fg="white", font=("Arial", 14, "bold"),
                  width=15, height=2).pack(side="left", padx=10)
        tk.Button(btn_frame, text="HỦY", command=dialog.destroy,
                  bg="#e74c3c", fg="white", font=("Arial", 14, "bold"),
                  width=15, height=2).pack(side="left", padx=10)

        # Focus vào combobox đầu tiên
        start_day_combo.focus_set()

    def ve_bieu_do(self, start, end, title):
        """Vẽ biểu đồ thống kê"""
        try:
            # Query thống kê theo trạng thái
            query_trang_thai = """
                               SELECT TrangThai, COUNT(*) \
                               FROM LichKham
                               WHERE NgayGioKham BETWEEN ? AND ?
                               GROUP BY TrangThai \
                               """
            data_trang_thai = execute_query(query_trang_thai, (start, end), fetch=True)

            # Query thống kê theo ngày
            query_theo_ngay = """
                              SELECT CAST(NgayGioKham AS DATE), COUNT(*)
                              FROM LichKham
                              WHERE NgayGioKham BETWEEN ? AND ?
                              GROUP BY CAST(NgayGioKham AS DATE)
                              ORDER BY CAST(NgayGioKham AS DATE) \
                              """
            data_theo_ngay = execute_query(query_theo_ngay, (start, end), fetch=True)

            # Chuẩn bị dữ liệu cho biểu đồ trạng thái
            labels = ["Chưa khám", "Đã khám", "Đã hủy"]
            sizes = [0, 0, 0]
            colors = ["#ffc107", "#28a745", "#dc3545"]

            for row in data_trang_thai:
                if "Chưa" in str(row[0]):
                    sizes[0] = row[1]
                elif "Đã khám" in str(row[0]):
                    sizes[1] = row[1]
                elif "hủy" in str(row[0]):
                    sizes[2] = row[1]

            # Xóa các biểu đồ cũ
            self.ax1.clear()
            self.ax2.clear()

            # Vẽ biểu đồ tròn (trạng thái)
            if sum(sizes) > 0:
                self.ax1.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors,
                             startangle=90, textprops={'fontsize': 10})
                self.ax1.set_title("Phân bố trạng thái", fontsize=12, weight='bold', pad=10)
            else:
                self.ax1.text(0.5, 0.5, 'Không có dữ liệu', ha='center', va='center',
                              fontsize=12, transform=self.ax1.transAxes)
                self.ax1.set_title("Phân bố trạng thái", fontsize=12, weight='bold', pad=10)

            # Vẽ biểu đồ cột (theo ngày)
            if data_theo_ngay:
                dates = [datetime.strptime(str(row[0]), "%Y-%m-%d").strftime("%d-%m") for row in data_theo_ngay]
                counts = [row[1] for row in data_theo_ngay]

                bars = self.ax2.bar(dates, counts, color='#3498db', alpha=0.7)
                self.ax2.set_title("Số lượng lịch theo ngày", fontsize=12, weight='bold', pad=10)
                self.ax2.set_xlabel("Ngày")
                self.ax2.set_ylabel("Số lượng")

                # Thêm số liệu lên trên các cột
                for bar, count in zip(bars, counts):
                    height = bar.get_height()
                    self.ax2.text(bar.get_x() + bar.get_width() / 2., height + 0.1,
                                  f'{count}', ha='center', va='bottom', fontsize=9)

                # Xoay nhãn trục x để dễ đọc
                self.ax2.tick_params(axis='x', rotation=45)
            else:
                self.ax2.text(0.5, 0.5, 'Không có dữ liệu', ha='center', va='center',
                              fontsize=12, transform=self.ax2.transAxes)
                self.ax2.set_title("Số lượng lịch theo ngày", fontsize=12, weight='bold', pad=10)

            # Điều chỉnh layout
            self.fig.suptitle(title, fontsize=14, weight='bold', y=0.95)
            self.fig.tight_layout(rect=[0, 0, 1, 0.95])

            # Cập nhật thông tin tổng quan
            self.cap_nhat_thong_tin(data_trang_thai)

            # Vẽ lại canvas
            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi vẽ biểu đồ: {str(e)}")
