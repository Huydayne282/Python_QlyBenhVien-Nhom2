import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import pyodbc
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ==================== KẾT NỐI SQL ====================
connection_string = 'Driver={SQL Server};Server=LAPTOP-JINK9QGU;Database=Quanlybenhvien;UID=huy;PWD=123;'

def get_conn():
    return pyodbc.connect(connection_string)

def execute_query(query, params=None, fetch=False):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        if fetch:
            result = cursor.fetchall()
            conn.commit()
            return result if result else []
        else:
            conn.commit()
    except Exception as e:
        messagebox.showerror("Lỗi CSDL", str(e))
        return []
    finally:
        cursor.close()
        conn.close()

def rows_to_list(rows):
    return [tuple("" if item is None else item for item in row) for row in rows]

def get_next_id(table, column):
    try:
        result = execute_query(f"SELECT MAX({column}) FROM {table}", fetch=True)
        return (result[0][0] or 0) + 1 if result else 1
    except:
        return 1

# ==================== KIỂM TRA LỊCH KHÁM ====================
def kiem_tra_trung_lich(ma_bs, ma_phong, ngay_gio, ma_lich_hien_tai=None):
    try:
        dt = datetime.strptime(ngay_gio, "%Y-%m-%d %H:%M")
        if dt < datetime.now():
            return False, "Không thể đặt lịch trong quá khứ!"
        start_time = dt
        end_time = dt + timedelta(minutes=30)

        query_bs = """
            SELECT COUNT(*) FROM LichKham
            WHERE MaBacSi = ?
            AND TrangThai != N'Đã hủy'
            AND NgayGioKham BETWEEN ? AND ?
        """
        if ma_lich_hien_tai:
            query_bs += " AND MaLichKham != ?"
            result_bs = execute_query(query_bs, (ma_bs, start_time, end_time, ma_lich_hien_tai), fetch=True)
        else:
            result_bs = execute_query(query_bs, (ma_bs, start_time, end_time), fetch=True)

        if result_bs and result_bs[0][0] > 0:
            return False, f"Bác sĩ đã có lịch khám vào thời gian này!\nVui lòng chọn thời gian khác."

        query_phong = """
            SELECT COUNT(*) FROM LichKham
            WHERE MaPhong = ?
            AND TrangThai != N'Đã hủy'
            AND NgayGioKham BETWEEN ? AND ?
        """
        if ma_lich_hien_tai:
            query_phong += " AND MaLichKham != ?"
            result_phong = execute_query(query_phong, (ma_phong, start_time, end_time, ma_lich_hien_tai), fetch=True)
        else:
            result_phong = execute_query(query_phong, (ma_phong, start_time, end_time), fetch=True)

        if result_phong and result_phong[0][0] > 0:
            return False, f"Phòng khám đã có bệnh nhân vào thời gian này!\nVui lòng chọn phòng hoặc thời gian khác."

        date_str = dt.strftime("%Y-%m-%d")
        query_count = """
            SELECT COUNT(*) FROM LichKham
            WHERE MaBacSi = ?
            AND TrangThai != N'Đã hủy'
            AND CAST(NgayGioKham AS DATE) = ?
        """
        result_count = execute_query(query_count, (ma_bs, date_str), fetch=True)
        if result_count and result_count[0][0] >= 18:
            return False, f"Bác sĩ đã đủ 18 ca khám trong ngày {date_str}!\nVui lòng chọn ngày khác."

        query_count_phong = """
            SELECT COUNT(*) FROM LichKham
            WHERE MaPhong = ?
            AND TrangThai != N'Đã hủy'
            AND CAST(NgayGioKham AS DATE) = ?
        """
        result_count_phong = execute_query(query_count_phong, (ma_phong, date_str), fetch=True)
        if result_count_phong and result_count_phong[0][0] >= 18:
            return False, f"Phòng khám đã đủ 18 ca trong ngày {date_str}!\nVui lòng chọn phòng khác."

        return True, "OK"
    except ValueError:
        return False, "Định dạng ngày giờ không đúng! Vui lòng nhập theo format: YYYY-MM-DD HH:MM"
    except Exception as e:
        return False, f"Lỗi kiểm tra: {str(e)}"

# ==================== ĐĂNG NHẬP ====================
class LoginForm(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#e3f2fd")

        try:
            logo = Image.open("cmc_logo.png").resize((260, 160), Image.Resampling.LANCZOS)
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
        self.entry_user.insert(0, "")
        tk.Label(form, text="Mật khẩu:", font=("Arial", 14), bg="white").pack(anchor="w", padx=30)
        self.entry_pass = tk.Entry(form, font=("Arial", 14), width=30, show="*")
        self.entry_pass.pack(pady=10, padx=30)
        self.entry_pass.insert(0, "")
        tk.Button(form, text="ĐĂNG NHẬP", font=("Arial", 14, "bold"), bg="#007acc",
                  fg="white", width=25, height=2, command=self.login).pack(pady=30)
        self.error = tk.Label(form, text="", fg="red", bg="white", font=("Arial", 12))
        self.error.pack()

    def login(self):
        if self.entry_user.get() == "nhom2" and self.entry_pass.get() == "36":
            self.controller.show_frame("Dashboard")
        else:
            self.error.config(text="Sai tài khoản hoặc mật khẩu!")

# ==================== DASHBOARD ====================
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

# ==================== QUẢN LÝ BỆNH NHÂN ====================
class BenhNhanForm(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f5f5f5")

        header = tk.Frame(self, bg="#3498db", height=80)
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="QUẢN LÝ BỆNH NHÂN",
                 font=("Arial", 24, "bold"), bg="#3498db", fg="white").pack(pady=20)

        btns = tk.Frame(self, bg="#f5f5f5")
        btns.pack(pady=10)
        tk.Button(btns, text="Thêm", command=self.them, bg="#28a745", fg="white",
                  font=("Arial", 11, "bold"), width=15, height=2).pack(side="left", padx=5)
        tk.Button(btns, text="Sửa", command=self.sua, bg="#17a2b8", fg="white",
                  font=("Arial", 11, "bold"), width=15, height=2).pack(side="left", padx=5)
        tk.Button(btns, text="Xóa", command=self.xoa, bg="#dc3545", fg="white",
                  font=("Arial", 11, "bold"), width=15, height=2).pack(side="left", padx=5)
        tk.Button(btns, text="Làm mới", command=self.refresh, bg="#ffc107", fg="white",
                  font=("Arial", 11, "bold"), width=15, height=2).pack(side="left", padx=5)
        tk.Button(btns, text="Quay lại", command=lambda: controller.show_frame("Dashboard"),
                  bg="#6c757d", fg="white", font=("Arial", 11, "bold"), width=15, height=2).pack(side="left", padx=5)

        tree_frame = tk.Frame(self, bg="white", relief="solid", bd=2)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        cols = ("MaBenhNhan", "HoTen", "NgaySinh", "GioiTinh", "DiaChi", "SoDienThoai", "TrangThaiBenhNhan")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=20)

        for col in cols:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c, False))
            self.tree.column(col, width=120, anchor="center")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.refresh()

    def sort_column(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        try:
            l.sort(key=lambda t: int(t[0]), reverse=reverse)
        except ValueError:
            l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        data = rows_to_list(execute_query("SELECT * FROM BenhNhan ORDER BY MaBenhNhan ASC", fetch=True))
        for row in data:
            self.tree.insert("", "end", values=row)

    def them(self):
        self.open_dialog("Thêm bệnh nhân", True)

    def sua(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Chọn", "Vui lòng chọn bệnh nhân!")
        values = self.tree.item(sel[0], "values")
        self.open_dialog("Sửa bệnh nhân", False, values)

    def xoa(self):
        sel = self.tree.selection()
        if sel and messagebox.askyesno("Xóa", "Xóa bệnh nhân này?"):
            ma = self.tree.item(sel[0], "values")[0]
            execute_query("DELETE FROM BenhNhan WHERE MaBenhNhan=?", (ma,))
            self.refresh()

    def open_dialog(self, title, is_add, data=None):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("500x600")
        dialog.configure(bg="#f0f0f0")

        main_frame = tk.Frame(dialog, bg="white", relief="solid", bd=2)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(main_frame, text=title.upper(), font=("Arial", 16, "bold"),
                 bg="white", fg="#3498db").pack(pady=15)

        form_frame = tk.Frame(main_frame, bg="white")
        form_frame.pack(padx=30, pady=10)

        labels = ["Họ tên:", "Ngày sinh:", "Giới tính:", "Địa chỉ:", "Số điện thoại:", "Trạng thái:"]
        entries = []

        for i, l in enumerate(labels):
            tk.Label(form_frame, text=l, font=("Arial", 11, "bold"),
                     bg="white").grid(row=i, column=0, padx=10, pady=12, sticky="w")
            e = tk.Entry(form_frame, width=35, font=("Arial", 11))
            e.grid(row=i, column=1, padx=10, pady=12)
            if not is_add and data:
                e.insert(0, data[i+1])
            entries.append(e)
        tk.Label(form_frame, text="(YYYY-MM-DD)", font=("Arial", 9, "italic"),
                 bg="white", fg="#666").grid(row=1, column=2, sticky="w")

        def save():
            vals = [e.get().strip() for e in entries]
            if not all(vals):
                return messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")

            if is_add:
                ma = get_next_id("BenhNhan", "MaBenhNhan")
                execute_query("INSERT INTO BenhNhan VALUES (?, ?, ?, ?, ?, ?, ?)", (ma, *vals))
                messagebox.showinfo("Thành công", f"Đã thêm bệnh nhân mã {ma}")
            else:
                ma = data[0]
                execute_query("UPDATE BenhNhan SET HoTen=?, NgaySinh=?, GioiTinh=?, DiaChi=?, SoDienThoai=?, TrangThaiBenhNhan=? WHERE MaBenhNhan=?", (*vals, ma))
                messagebox.showinfo("Thành công", f"Đã cập nhật bệnh nhân mã {ma}")
            self.refresh()
            dialog.destroy()

        btn_frame = tk.Frame(main_frame, bg="white")
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Lưu", command=save, bg="#28a745", fg="white",
                  font=("Arial", 12, "bold"), width=15, height=2).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Hủy", command=dialog.destroy, bg="#6c757d", fg="white",
                  font=("Arial", 12, "bold"), width=15, height=2).pack(side="left", padx=10)

# ==================== QUẢN LÝ BÁC SĨ ====================
class BacSiForm(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f5f5f5")

        header = tk.Frame(self, bg="#2ecc71", height=80)
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="QUẢN LÝ BÁC SĨ",
                 font=("Arial", 24, "bold"), bg="#2ecc71", fg="white").pack(pady=20)

        btns = tk.Frame(self, bg="#f5f5f5")
        btns.pack(pady=10)
        tk.Button(btns, text="Thêm", command=self.them, bg="#28a745", fg="white",
                  font=("Arial", 11, "bold"), width=15, height=2).pack(side="left", padx=5)
        tk.Button(btns, text="Sửa", command=self.sua, bg="#17a2b8", fg="white",
                  font=("Arial", 11, "bold"), width=15, height=2).pack(side="left", padx=5)
        tk.Button(btns, text="Xóa", command=self.xoa, bg="#dc3545", fg="white",
                  font=("Arial", 11, "bold"), width=15, height=2).pack(side="left", padx=5)
        tk.Button(btns, text="Làm mới", command=self.refresh, bg="#ffc107", fg="white",
                  font=("Arial", 11, "bold"), width=15, height=2).pack(side="left", padx=5)
        tk.Button(btns, text="Quay lại", command=lambda: controller.show_frame("Dashboard"),
                  bg="#6c757d", fg="white", font=("Arial", 11, "bold"), width=15, height=2).pack(side="left", padx=5)

        tree_frame = tk.Frame(self, bg="white", relief="solid", bd=2)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        cols = ("MaBacSi", "HoTen", "NgaySinh", "GioiTinh", "DiaChi", "ChuyenKhoa")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=20)

        for col in cols:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c, False))
            self.tree.column(col, width=130, anchor="center")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.refresh()

    def sort_column(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        try:
            l.sort(key=lambda t: int(t[0]), reverse=reverse)
        except ValueError:
            l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        data = rows_to_list(execute_query("SELECT * FROM BacSi ORDER BY MaBacSi ASC", fetch=True))
        for row in data:
            self.tree.insert("", "end", values=row)

    def them(self):
        self.open_dialog("Thêm bác sĩ", True)

    def sua(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Chọn", "Vui lòng chọn bác sĩ!")
        values = self.tree.item(sel[0], "values")
        self.open_dialog("Sửa bác sĩ", False, values)

    def xoa(self):
        sel = self.tree.selection()
        if sel and messagebox.askyesno("Xóa", "Xóa bác sĩ này?"):
            ma = self.tree.item(sel[0], "values")[0]
            execute_query("DELETE FROM BacSi WHERE MaBacSi=?", (ma,))
            self.refresh()

    def open_dialog(self, title, is_add, data=None):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("500x550")
        dialog.configure(bg="#f0f0f0")

        main_frame = tk.Frame(dialog, bg="white", relief="solid", bd=2)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(main_frame, text=title.upper(), font=("Arial", 16, "bold"),
                 bg="white", fg="#2ecc71").pack(pady=15)

        form_frame = tk.Frame(main_frame, bg="white")
        form_frame.pack(padx=30, pady=10)

        labels = ["Họ tên:", "Ngày sinh:", "Giới tính:", "Địa chỉ:", "Chuyên khoa:"]
        entries = []

        for i, l in enumerate(labels):
            tk.Label(form_frame, text=l, font=("Arial", 11, "bold"),
                     bg="white").grid(row=i, column=0, padx=10, pady=12, sticky="w")
            e = tk.Entry(form_frame, width=35, font=("Arial", 11))
            e.grid(row=i, column=1, padx=10, pady=12)
            if not is_add and data:
                e.insert(0, data[i+1])
            entries.append(e)
        tk.Label(form_frame, text="(YYYY-MM-DD)", font=("Arial", 9, "italic"),
                 bg="white", fg="#666").grid(row=1, column=2, sticky="w")

        def save():
            vals = [e.get().strip() for e in entries]
            if not all(vals):
                return messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")

            if is_add:
                ma = get_next_id("BacSi", "MaBacSi")
                execute_query("INSERT INTO BacSi VALUES (?, ?, ?, ?, ?, ?)", (ma, *vals))
                messagebox.showinfo("Thành công", f"Đã thêm bác sĩ mã {ma}")
            else:
                ma = data[0]
                execute_query("UPDATE BacSi SET HoTen=?, NgaySinh=?, GioiTinh=?, DiaChi=?, ChuyenKhoa=? WHERE MaBacSi=?", (*vals, ma))
                messagebox.showinfo("Thành công", f"Đã cập nhật bác sĩ mã {ma}")
            self.refresh()
            dialog.destroy()

        btn_frame = tk.Frame(main_frame, bg="white")
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Lưu", command=save, bg="#28a745", fg="white",
                  font=("Arial", 12, "bold"), width=15, height=2).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Hủy", command=dialog.destroy, bg="#6c757d", fg="white",
                  font=("Arial", 12, "bold"), width=15, height=2).pack(side="left", padx=10)

# ==================== QUẢN LÝ PHÒNG KHÁM ====================
class PhongKhamForm(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f5f5f5")

        header = tk.Frame(self, bg="#f39c12", height=80)
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="QUẢN LÝ PHÒNG KHÁM",
                 font=("Arial", 24, "bold"), bg="#f39c12", fg="white").pack(pady=20)

        btns = tk.Frame(self, bg="#f5f5f5")
        btns.pack(pady=10)
        tk.Button(btns, text="Thêm", command=self.them, bg="#28a745", fg="white",
                  font=("Arial", 11, "bold"), width=15, height=2).pack(side="left", padx=5)
        tk.Button(btns, text="Sửa", command=self.sua, bg="#17a2b8", fg="white",
                  font=("Arial", 11, "bold"), width=15, height=2).pack(side="left", padx=5)
        tk.Button(btns, text="Xóa", command=self.xoa, bg="#dc3545", fg="white",
                  font=("Arial", 11, "bold"), width=15, height=2).pack(side="left", padx=5)
        tk.Button(btns, text="Làm mới", command=self.refresh, bg="#ffc107", fg="white",
                  font=("Arial", 11, "bold"), width=15, height=2).pack(side="left", padx=5)
        tk.Button(btns, text="Quay lại", command=lambda: controller.show_frame("Dashboard"),
                  bg="#6c757d", fg="white", font=("Arial", 11, "bold"), width=15, height=2).pack(side="left", padx=5)

        tree_frame = tk.Frame(self, bg="white", relief="solid", bd=2)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        cols = ("MaPhong", "TenPhong", "ChuyenKhoa", "TinhTrang")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=20)

        col_widths = [100, 200, 200, 150]
        for col, width in zip(cols, col_widths):
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c, False))
            self.tree.column(col, width=width, anchor="center")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.refresh()

    def sort_column(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        try:
            l.sort(key=lambda t: int(t[0]), reverse=reverse)
        except ValueError:
            l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        data = rows_to_list(execute_query("SELECT MaPhong, TenPhong, ChuyenKhoa, TinhTrang FROM PhongKham ORDER BY MaPhong ASC", fetch=True))
        for row in data:
            self.tree.insert("", "end", values=row)

    def them(self):
        self.open_dialog("Thêm phòng khám", True)

    def sua(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Chọn", "Vui lòng chọn phòng khám!")
        values = self.tree.item(sel[0], "values")
        self.open_dialog("Sửa phòng khám", False, values)

    def xoa(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Chọn", "Vui lòng chọn phòng khám!")
        ma = self.tree.item(sel[0], "values")[0]
        if messagebox.askyesno("Xóa", f"Xóa phòng {ma}?"):
            execute_query("DELETE FROM PhongKham WHERE MaPhong = ?", (ma,))
            self.refresh()

    def open_dialog(self, title, is_add, data=None):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("500x450")
        dialog.configure(bg="#f0f0f0")

        main_frame = tk.Frame(dialog, bg="white", relief="solid", bd=2)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(main_frame, text=title.upper(), font=("Arial", 16, "bold"),
                 bg="white", fg="#f39c12").pack(pady=15)

        form_frame = tk.Frame(main_frame, bg="white")
        form_frame.pack(padx=30, pady=10)

        labels = ["Tên phòng:", "Chuyên khoa:", "Tình trạng:"]
        entries = []

        for i, txt in enumerate(labels):
            tk.Label(form_frame, text=txt, font=("Arial", 11, "bold"),
                     bg="white").grid(row=i, column=0, padx=10, pady=15, sticky="w")
            e = tk.Entry(form_frame, width=35, font=("Arial", 11))
            e.grid(row=i, column=1, padx=10, pady=15)
            if not is_add and data:
                e.insert(0, data[i+1])
            entries.append(e)

        def save():
            ten, chuyenkhoa, tinhtrang = [e.get().strip() for e in entries]
            if not all([ten, chuyenkhoa, tinhtrang]):
                return messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")
            if is_add:
                ma = get_next_id("PhongKham", "MaPhong")
                execute_query("INSERT INTO PhongKham (MaPhong, TenPhong, ChuyenKhoa, TinhTrang) VALUES (?, ?, ?, ?)",
                              (ma, ten, chuyenkhoa, tinhtrang))
                messagebox.showinfo("Thành công", f"Đã thêm phòng mã {ma}")
            else:
                ma = data[0]
                execute_query("UPDATE PhongKham SET TenPhong=?, ChuyenKhoa=?, TinhTrang=? WHERE MaPhong=?",
                              (ten, chuyenkhoa, tinhtrang, ma))
                messagebox.showinfo("Thành công", f"Đã cập nhật phòng mã {ma}")
            self.refresh()
            dialog.destroy()

        btn_frame = tk.Frame(main_frame, bg="white")
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Lưu", command=save, bg="#28a745", fg="white",
                  font=("Arial", 12, "bold"), width=15, height=2).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Hủy", command=dialog.destroy, bg="#6c757d", fg="white",
                  font=("Arial", 12, "bold"), width=15, height=2).pack(side="left", padx=10)

# ==================== QUẢN LÝ LỊCH KHÁM ====================
class LichKhamForm(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f5f5f5")

        header = tk.Frame(self, bg="#007acc", height=80)
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="QUẢN LÝ LỊCH KHÁM",
                 font=("Arial", 24, "bold"), bg="#007acc", fg="white").pack(pady=20)

        btns = tk.Frame(self, bg="#f5f5f5")
        btns.pack(pady=15)
        tk.Button(btns, text="Đặt lịch mới", command=self.dat_lich,
                  bg="#28a745", fg="white", font=("Arial", 11, "bold"),
                  width=18, height=2).pack(side="left", padx=8)
        tk.Button(btns, text="Sửa lịch", command=self.sua_lich,
                  bg="#17a2b8", fg="white", font=("Arial", 11, "bold"),
                  width=18, height=2).pack(side="left", padx=8)
        tk.Button(btns, text="Hủy lịch", command=self.huy_lich,
                  bg="#dc3545", fg="white", font=("Arial", 11, "bold"),
                  width=18, height=2).pack(side="left", padx=8)
        tk.Button(btns, text="Làm mới", command=self.refresh,
                  bg="#ffc107", fg="white", font=("Arial", 11, "bold"),
                  width=18, height=2).pack(side="left", padx=8)
        tk.Button(btns, text="Quay lại", command=lambda: controller.show_frame("Dashboard"),
                  bg="#6c757d", fg="white", font=("Arial", 11, "bold"),
                  width=18, height=2).pack(side="left", padx=8)

        filter_frame = tk.Frame(self, bg="white", relief="solid", bd=1)
        filter_frame.pack(pady=10, padx=20, fill="x")
        tk.Label(filter_frame, text="Lọc theo trạng thái:",
                 font=("Arial", 11, "bold"), bg="white").pack(side="left", padx=20, pady=10)
        self.filter_var = tk.StringVar(value="all")
        tk.Radiobutton(filter_frame, text="Tất cả", variable=self.filter_var,
                       value="all", command=self.refresh, bg="white",
                       font=("Arial", 10, "bold")).pack(side="left", padx=15)
        tk.Radiobutton(filter_frame, text="Chưa khám", variable=self.filter_var,
                       value="chua", command=self.refresh, bg="white",
                       font=("Arial", 10, "bold"), fg="#ffc107").pack(side="left", padx=15)
        tk.Radiobutton(filter_frame, text="Đã khám", variable=self.filter_var,
                       value="da", command=self.refresh, bg="white",
                       font=("Arial", 10, "bold"), fg="#28a745").pack(side="left", padx=15)
        tk.Radiobutton(filter_frame, text="Đã hủy", variable=self.filter_var,
                       value="huy", command=self.refresh, bg="white",
                       font=("Arial", 10, "bold"), fg="#dc3545").pack(side="left", padx=15)

        tree_frame = tk.Frame(self, bg="white", relief="solid", bd=2)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        cols = ("Mã", "Mã BN", "Mã BS", "Mã Phòng", "Thời gian", "Trạng thái")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=20)

        col_widths = [80, 100, 100, 120, 180, 130]
        for col, width in zip(cols, col_widths):
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c, False))
            self.tree.column(col, width=width, anchor="center")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        style = ttk.Style()
        style.configure("Treeview", rowheight=30, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

        self.tree.tag_configure("chua_kham", background="#fff3cd")
        self.tree.tag_configure("da_kham", background="#d4edda")
        self.tree.tag_configure("da_huy", background="#f8d7da")

        self.refresh()

    def sort_column(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        try:
            l.sort(key=lambda t: int(t[0]), reverse=reverse)
        except ValueError:
            l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        query = "SELECT MaLichKham, MaBenhNhan, MaBacSi, MaPhong, NgayGioKham, TrangThai FROM LichKham WHERE 1=1"
        fv = self.filter_var.get()
        if fv == "chua":
            query += " AND TrangThai = N'Chưa khám'"
        elif fv == "da":
            query += " AND TrangThai = N'Đã khám'"
        elif fv == "huy":
            query += " AND TrangThai = N'Đã hủy'"
        query += " ORDER BY MaLichKham ASC"
        data = rows_to_list(execute_query(query, fetch=True))
        for row in data:
            tag = ""
            if row[5] == "Chưa khám":
                tag = "chua_kham"
            elif row[5] == "Đã khám":
                tag = "da_kham"
            elif row[5] == "Đã hủy":
                tag = "da_huy"
            self.tree.insert("", "end", values=row, tags=(tag,))

    def dat_lich(self):
        dialog = tk.Toplevel(self)
        dialog.title("Đặt lịch khám")
        dialog.geometry("700x800")
        dialog.configure(bg="#f0f0f0")

        main_frame = tk.Frame(dialog, bg="white", relief="solid", bd=2)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(main_frame, text="THÔNG TIN ĐẶT LỊCH KHÁM",
                 font=("Arial", 16, "bold"), bg="white", fg="#007acc").pack(pady=15)

        form_frame = tk.Frame(main_frame, bg="white")
        form_frame.pack(padx=30, pady=10)

        # Mã BN với thông tin đầy đủ
        tk.Label(form_frame, text="Mã Bệnh nhân:", font=("Arial", 11, "bold"),
                 bg="white", fg="#333").grid(row=0, column=0, padx=10, pady=12, sticky="w")
        e_bn = tk.Entry(form_frame, width=35, font=("Arial", 11))
        e_bn.grid(row=0, column=1, padx=10, pady=12)

        # Label hiển thị thông tin BN
        lbl_bn_info = tk.Label(form_frame, text="", font=("Arial", 9), bg="white", fg="#0066cc")
        lbl_bn_info.grid(row=1, column=1, sticky="w", padx=10)

        def show_bn_list():
            bn_data = execute_query("SELECT MaBenhNhan, HoTen, SoDienThoai FROM BenhNhan ORDER BY MaBenhNhan",
                                    fetch=True)
            list_window = tk.Toplevel(dialog)
            list_window.title("Danh sách bệnh nhân")
            list_window.geometry("700x450")

            # Tạo frame chứa treeview và scrollbar
            tree_frame = tk.Frame(list_window)
            tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

            cols = ("Mã", "Họ tên", "SĐT")
            tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=15)

            # Định nghĩa headings và columns
            tree.heading("Mã", text="Mã")
            tree.heading("Họ tên", text="Họ tên")
            tree.heading("SĐT", text="SĐT")

            tree.column("Mã", width=100, anchor="center")
            tree.column("Họ tên", width=300, anchor="w")
            tree.column("SĐT", width=200, anchor="center")

            # Thêm scrollbar
            vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            tree.pack(side="left", fill="both", expand=True)
            vsb.pack(side="right", fill="y")

            # Thêm dữ liệu
            for row in bn_data:
                tree.insert("", "end", values=row)

            def chon():
                sel = tree.selection()
                if sel:
                    values = tree.item(sel[0], "values")
                    e_bn.delete(0, tk.END)
                    e_bn.insert(0, values[0])
                    lbl_bn_info.config(text=f"✓ {values[1]} - SĐT: {values[2]}")
                    list_window.destroy()

            btn_frame = tk.Frame(list_window)
            btn_frame.pack(pady=10)
            tk.Button(btn_frame, text="Chọn", command=chon, bg="#007acc", fg="white",
                      font=("Arial", 11, "bold"), width=15).pack(pady=10)

        # Mã BS với thông tin đầy đủ
        tk.Label(form_frame, text="Mã Bác sĩ:", font=("Arial", 11, "bold"),
                 bg="white", fg="#333").grid(row=2, column=0, padx=10, pady=12, sticky="w")
        e_bs = tk.Entry(form_frame, width=35, font=("Arial", 11))
        e_bs.grid(row=2, column=1, padx=10, pady=12)

        # Label hiển thị thông tin BS
        lbl_bs_info = tk.Label(form_frame, text="", font=("Arial", 9), bg="white", fg="#0066cc")
        lbl_bs_info.grid(row=3, column=1, sticky="w", padx=10)

        def show_bs_list():
            bs_data = execute_query("SELECT MaBacSi, HoTen, ChuyenKhoa FROM BacSi ORDER BY MaBacSi", fetch=True)
            list_window = tk.Toplevel(dialog)
            list_window.title("Danh sách bác sĩ")
            list_window.geometry("700x450")

            tree_frame = tk.Frame(list_window)
            tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

            cols = ("Mã", "Họ tên", "Chuyên khoa")
            tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=15)

            tree.heading("Mã", text="Mã")
            tree.heading("Họ tên", text="Họ tên")
            tree.heading("Chuyên khoa", text="Chuyên khoa")

            tree.column("Mã", width=100, anchor="center")
            tree.column("Họ tên", width=300, anchor="w")
            tree.column("Chuyên khoa", width=200, anchor="center")

            vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            tree.pack(side="left", fill="both", expand=True)
            vsb.pack(side="right", fill="y")

            for row in bs_data:
                tree.insert("", "end", values=row)

            def chon():
                sel = tree.selection()
                if sel:
                    values = tree.item(sel[0], "values")
                    e_bs.delete(0, tk.END)
                    e_bs.insert(0, values[0])
                    lbl_bs_info.config(text=f"✓ {values[1]} - {values[2]}")
                    list_window.destroy()

            btn_frame = tk.Frame(list_window)
            btn_frame.pack(pady=10)
            tk.Button(btn_frame, text="Chọn", command=chon, bg="#007acc", fg="white",
                      font=("Arial", 11, "bold"), width=15).pack(pady=10)

        # Mã Phòng với thông tin đầy đủ
        tk.Label(form_frame, text="Mã Phòng:", font=("Arial", 11, "bold"),
                 bg="white", fg="#333").grid(row=4, column=0, padx=10, pady=12, sticky="w")
        e_phong = tk.Entry(form_frame, width=35, font=("Arial", 11))
        e_phong.grid(row=4, column=1, padx=10, pady=12)

        # Label hiển thị thông tin Phòng
        lbl_phong_info = tk.Label(form_frame, text="", font=("Arial", 9), bg="white", fg="#0066cc")
        lbl_phong_info.grid(row=5, column=1, sticky="w", padx=10)

        def show_phong_list():
            phong_data = execute_query("SELECT MaPhong, TenPhong, ChuyenKhoa FROM PhongKham ORDER BY MaPhong",
                                       fetch=True)
            list_window = tk.Toplevel(dialog)
            list_window.title("Danh sách phòng khám")
            list_window.geometry("700x450")

            tree_frame = tk.Frame(list_window)
            tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

            cols = ("Mã", "Tên phòng", "Chuyên khoa")
            tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=15)

            tree.heading("Mã", text="Mã")
            tree.heading("Tên phòng", text="Tên phòng")
            tree.heading("Chuyên khoa", text="Chuyên khoa")

            tree.column("Mã", width=100, anchor="center")
            tree.column("Tên phòng", width=300, anchor="w")
            tree.column("Chuyên khoa", width=200, anchor="center")

            vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            tree.pack(side="left", fill="both", expand=True)
            vsb.pack(side="right", fill="y")

            for row in phong_data:
                tree.insert("", "end", values=row)

            def chon():
                sel = tree.selection()
                if sel:
                    values = tree.item(sel[0], "values")
                    e_phong.delete(0, tk.END)
                    e_phong.insert(0, values[0])
                    lbl_phong_info.config(text=f"✓ {values[1]} - {values[2]}")
                    list_window.destroy()

            btn_frame = tk.Frame(list_window)
            btn_frame.pack(pady=10)
            tk.Button(btn_frame, text="Chọn", command=chon, bg="#007acc", fg="white",
                      font=("Arial", 11, "bold"), width=15).pack(pady=10)

        # Ngày giờ
        tk.Label(form_frame, text="Ngày giờ:", font=("Arial", 11, "bold"),
                 bg="white", fg="#333").grid(row=6, column=0, padx=10, pady=12, sticky="w")
        e_time = tk.Entry(form_frame, width=35, font=("Arial", 11))
        e_time.grid(row=6, column=1, padx=10, pady=12)
        tk.Label(form_frame, text="(VD: 2025-11-15 09:30)",
                 font=("Arial", 9, "italic"), bg="white", fg="#666").grid(row=7, column=1, sticky="w", padx=10)

        # Trạng thái
        tk.Label(form_frame, text="Trạng thái:", font=("Arial", 11, "bold"),
                 bg="white", fg="#333").grid(row=8, column=0, padx=10, pady=12, sticky="w")
        status_var = tk.StringVar(value="Chưa khám")
        status_frame = tk.Frame(form_frame, bg="white")
        status_frame.grid(row=8, column=1, sticky="w", padx=10, pady=12)
        tk.Radiobutton(status_frame, text="Chưa khám", variable=status_var,
                       value="Chưa khám", bg="white", font=("Arial", 10)).pack(side="left", padx=5)
        tk.Radiobutton(status_frame, text="Đã khám", variable=status_var,
                       value="Đã khám", bg="white", font=("Arial", 10)).pack(side="left", padx=5)

        # Thông tin kiểm tra
        info_frame = tk.Frame(main_frame, bg="#e7f3ff", relief="solid", bd=1)
        info_frame.pack(fill="x", padx=30, pady=15)
        tk.Label(info_frame, text="Kiểm tra tính khả dụng",
                 font=("Arial", 11, "bold"), bg="#e7f3ff", fg="#0066cc").pack(pady=10)
        check_label = tk.Label(info_frame, text="", font=("Arial", 10),
                               bg="#e7f3ff", fg="#333", justify="left")
        check_label.pack(padx=15, pady=5)

        def kiem_tra():
            bn = e_bn.get().strip()
            bs = e_bs.get().strip()
            phong = e_phong.get().strip()
            time = e_time.get().strip()
            if not all([bn, bs, phong, time]):
                check_label.config(text="Vui lòng điền đầy đủ thông tin!", fg="red")
                return
            # Kiểm tra thông tin BN, BS, Phòng có tồn tại không
            try:
                bn_check = execute_query("SELECT HoTen, SoDienThoai FROM BenhNhan WHERE MaBenhNhan=?", (bn,), fetch=True)
                if not bn_check:
                    check_label.config(text=f"Mã bệnh nhân {bn} không tồn tại!", fg="red")
                    return

                bs_check = execute_query("SELECT HoTen, ChuyenKhoa FROM BacSi WHERE MaBacSi=?", (bs,), fetch=True)
                if not bs_check:
                    check_label.config(text=f"Mã bác sĩ {bs} không tồn tại!", fg="red")
                    return

                phong_check = execute_query("SELECT TenPhong FROM PhongKham WHERE MaPhong=?", (phong,), fetch=True)
                if not phong_check:
                    check_label.config(text=f"Mã phòng {phong} không tồn tại!", fg="red")
                    return
                # Cập nhật labels với thông tin đầy đủ
                lbl_bn_info.config(text=f"✓ {bn_check[0][0]} - SĐT: {bn_check[0][1]}")
                lbl_bs_info.config(text=f"✓ {bs_check[0][0]} - {bs_check[0][1]}")
                lbl_phong_info.config(text=f"✓ {phong_check[0][0]}")
            except Exception as e:
                check_label.config(text=f"Lỗi kiểm tra dữ liệu: {str(e)}", fg="red")
                return
            is_valid, msg = kiem_tra_trung_lich(bs, phong, time)
            if is_valid:
                date_str = time.split()[0]
                count_bs = execute_query(
                    "SELECT COUNT(*) FROM LichKham WHERE MaBacSi = ? AND CAST(NgayGioKham AS DATE) = ? AND TrangThai != N'Đã hủy'",
                    (bs, date_str), fetch=True)[0][0]
                count_phong = execute_query(
                    "SELECT COUNT(*) FROM LichKham WHERE MaPhong = ? AND CAST(NgayGioKham AS DATE) = ? AND TrangThai != N'Đã hủy'",
                    (phong, date_str), fetch=True)[0][0]
                info_text = f"✅ Có thể đặt lịch!\n\n"
                info_text += f"• Bác sĩ {bs}: {count_bs}/18 ca trong ngày\n"
                info_text += f"• Phòng {phong}: {count_phong}/18 ca trong ngày\n"
                info_text += f"• Thời gian: {time} (Trống)"
                check_label.config(text=info_text, fg="green")
            else:
                check_label.config(text=f"❌ {msg}", fg="red")

        def save():
            bn = e_bn.get().strip()
            bs = e_bs.get().strip()
            phong = e_phong.get().strip()
            time = e_time.get().strip()
            status = status_var.get()

            if not all([bn, bs, phong, time]):
                return messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")

            # Kiểm tra định dạng thời gian
            try:
                datetime.strptime(time, "%Y-%m-%d %H:%M")
            except ValueError:
                return messagebox.showerror("Lỗi",
                                            "Định dạng thời gian không đúng! Vui lòng nhập theo format: YYYY-MM-DD HH:MM")

            # Kiểm tra tồn tại các mã
            try:
                bn_check = execute_query("SELECT HoTen FROM BenhNhan WHERE MaBenhNhan=?", (bn,), fetch=True)
                if not bn_check:
                    return messagebox.showerror("Lỗi", f"Mã bệnh nhân {bn} không tồn tại!")

                bs_check = execute_query("SELECT HoTen FROM BacSi WHERE MaBacSi=?", (bs,), fetch=True)
                if not bs_check:
                    return messagebox.showerror("Lỗi", f"Mã bác sĩ {bs} không tồn tại!")

                phong_check = execute_query("SELECT TenPhong FROM PhongKham WHERE MaPhong=?", (phong,), fetch=True)
                if not phong_check:
                    return messagebox.showerror("Lỗi", f"Mã phòng {phong} không tồn tại!")
            except Exception as e:
                return messagebox.showerror("Lỗi", f"Lỗi kiểm tra dữ liệu: {str(e)}")

            is_valid, msg = kiem_tra_trung_lich(bs, phong, time)
            if not is_valid:
                return messagebox.showerror("Không thể đặt lịch", msg)

            try:
                ma = get_next_id("LichKham", "MaLichKham")
                execute_query("INSERT INTO LichKham VALUES (?, ?, ?, ?, ?, ?)",
                              (ma, bn, bs, phong, time, status))
                messagebox.showinfo("Thành công", f"Đã đặt lịch khám thành công!\nMã lịch: {ma}")
                self.refresh()
                self.controller.frames["Dashboard"].refresh()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi lưu: {str(e)}")

        btn_frame = tk.Frame(main_frame, bg="white")
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Kiểm tra", command=kiem_tra, bg="#ffc107", fg="white",
                  font=("Arial", 12, "bold"), width=15, height=2).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Lưu", command=save, bg="#28a745", fg="white",
                  font=("Arial", 12, "bold"), width=15, height=2).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Hủy", command=dialog.destroy, bg="#6c757d", fg="white",
                  font=("Arial", 12, "bold"), width=15, height=2).pack(side="left", padx=10)

    def sua_lich(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Chọn", "Vui lòng chọn lịch cần sửa!")

        values = self.tree.item(sel[0], "values")
        ma_lich, ma_bn, ma_bs, ma_phong, ngay_gio, trang_thai = values

        # KHÔNG cho sửa lịch đã hủy
        if trang_thai == "Đã hủy":
            return messagebox.showwarning("Lỗi", "Không thể sửa lịch đã hủy! Hãy tạo lịch mới.")

        self.open_dialog_sua_lich(ma_lich, ma_bn, ma_bs, ma_phong, ngay_gio, trang_thai)

    def open_dialog_sua_lich(self, ma_lich, ma_bn, ma_bs, ma_phong, ngay_gio, trang_thai):
        dialog = tk.Toplevel(self)
        dialog.title("Sửa lịch khám")
        dialog.geometry("500x500")
        dialog.configure(bg="#f0f0f0")

        main_frame = tk.Frame(dialog, bg="white", relief="solid", bd=2)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(main_frame, text="SỬA THÔNG TIN LỊCH KHÁM",
                 font=("Arial", 16, "bold"), bg="white", fg="#007acc").pack(pady=15)

        form_frame = tk.Frame(main_frame, bg="white")
        form_frame.pack(padx=30, pady=10)

        # Mã BN
        tk.Label(form_frame, text="Mã Bệnh nhân:", font=("Arial", 11, "bold"),
                 bg="white").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        e_bn = tk.Entry(form_frame, width=30, font=("Arial", 11))
        e_bn.grid(row=0, column=1, padx=10, pady=10)
        e_bn.insert(0, ma_bn)

        # Mã BS
        tk.Label(form_frame, text="Mã Bác sĩ:", font=("Arial", 11, "bold"),
                 bg="white").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        e_bs = tk.Entry(form_frame, width=30, font=("Arial", 11))
        e_bs.grid(row=1, column=1, padx=10, pady=10)
        e_bs.insert(0, ma_bs)

        # Mã Phòng
        tk.Label(form_frame, text="Mã Phòng:", font=("Arial", 11, "bold"),
                 bg="white").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        e_phong = tk.Entry(form_frame, width=30, font=("Arial", 11))
        e_phong.grid(row=2, column=1, padx=10, pady=10)
        e_phong.insert(0, ma_phong)

        # Ngày giờ
        tk.Label(form_frame, text="Ngày giờ:", font=("Arial", 11, "bold"),
                 bg="white").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        e_time = tk.Entry(form_frame, width=30, font=("Arial", 11))
        e_time.grid(row=3, column=1, padx=10, pady=10)
        # Chuyển đổi định dạng thời gian (bỏ giây nếu có)
        ngay_gio_simple = ngay_gio.split('.')[0]  # Bỏ phần giây nếu có
        e_time.insert(0, ngay_gio_simple)
        tk.Label(form_frame, text="(VD: 2025-11-15 09:30)",
                 font=("Arial", 9, "italic"), bg="white", fg="#666").grid(row=4, column=1, sticky="w", padx=10)

        # Trạng thái
        tk.Label(form_frame, text="Trạng thái:", font=("Arial", 11, "bold"),
                 bg="white").grid(row=5, column=0, padx=10, pady=10, sticky="w")
        status_var = tk.StringVar(value=trang_thai)
        status_frame = tk.Frame(form_frame, bg="white")
        status_frame.grid(row=5, column=1, sticky="w", padx=10, pady=10)
        tk.Radiobutton(status_frame, text="Chưa khám", variable=status_var,
                       value="Chưa khám", bg="white", font=("Arial", 10)).pack(side="left", padx=5)
        tk.Radiobutton(status_frame, text="Đã khám", variable=status_var,
                       value="Đã khám", bg="white", font=("Arial", 10)).pack(side="left", padx=5)

        def save():
            bn = e_bn.get().strip()
            bs = e_bs.get().strip()
            phong = e_phong.get().strip()
            time = e_time.get().strip()
            status = status_var.get()

            if not all([bn, bs, phong, time]):
                return messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")

            # Kiểm tra định dạng thời gian
            try:
                datetime.strptime(time, "%Y-%m-%d %H:%M")
            except ValueError:
                return messagebox.showerror("Lỗi",
                                            "Định dạng thời gian không đúng! Vui lòng nhập theo format: YYYY-MM-DD HH:MM")

            # Kiểm tra trùng lịch (loại trừ lịch hiện tại)
            is_valid, msg = kiem_tra_trung_lich(bs, phong, time, ma_lich_hien_tai=ma_lich)
            if not is_valid:
                return messagebox.showerror("Lỗi", msg)

            try:
                execute_query(
                    "UPDATE LichKham SET MaBenhNhan=?, MaBacSi=?, MaPhong=?, NgayGioKham=?, TrangThai=? WHERE MaLichKham=?",
                    (bn, bs, phong, time, status, ma_lich))
                messagebox.showinfo("Thành công", f"Đã cập nhật lịch khám mã {ma_lich} thành công!")
                self.refresh()
                self.controller.frames["Dashboard"].refresh()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi cập nhật: {str(e)}")

        btn_frame = tk.Frame(main_frame, bg="white")
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Lưu", command=save, bg="#28a745", fg="white",
                  font=("Arial", 12, "bold"), width=15, height=2).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Hủy", command=dialog.destroy, bg="#6c757d", fg="white",
                  font=("Arial", 12, "bold"), width=15, height=2).pack(side="left", padx=10)

    def huy_lich(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Chọn", "Vui lòng chọn lịch cần hủy!")
        values = self.tree.item(sel[0], "values")
        ma, tt = values[0], values[5]
        if tt == "Đã khám":
            return messagebox.showwarning("Lỗi", "Không thể hủy lịch đã khám!")
        if messagebox.askyesno("Xác nhận", f"Hủy lịch mã {ma}?"):
            execute_query("UPDATE LichKham SET TrangThai = N'Đã hủy' WHERE MaLichKham = ?", (ma,))
            messagebox.showinfo("Thành công", "Đã hủy lịch!")
            self.refresh()
            self.controller.frames["Dashboard"].refresh()

# ==================== TRA CỨU ====================
class TraCuuForm(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f5f5f5")

        header = tk.Frame(self, bg="#9b59b6", height=80)
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="TRA CỨU LỊCH KHÁM",
                 font=("Arial", 24, "bold"), bg="#9b59b6", fg="white").pack(pady=20)

        search_frame = tk.Frame(self, bg="white", relief="solid", bd=2)
        search_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(search_frame, text="Nhập ngày:", font=("Arial", 11, "bold"),
                 bg="white").pack(side="left", padx=15, pady=15)
        self.entry_date = tk.Entry(search_frame, width=20, font=("Arial", 11))
        self.entry_date.pack(side="left", padx=5, pady=15)

        tk.Button(search_frame, text="Tìm", command=self.tim_kiem, bg="#007acc",
                  fg="white", font=("Arial", 10, "bold"), width=12).pack(side="left", padx=5)
        tk.Button(search_frame, text="Hôm nay", command=self.hom_nay, bg="#28a745",
                  fg="white", font=("Arial", 10, "bold"), width=12).pack(side="left", padx=5)
        tk.Button(search_frame, text="Hủy lịch", command=self.huy_lich, bg="#dc3545",
                  fg="white", font=("Arial", 10, "bold"), width=12).pack(side="left", padx=5)
        tk.Button(search_frame, text="Quay lại", command=lambda: controller.show_frame("Dashboard"),
                  bg="#6c757d", fg="white", font=("Arial", 10, "bold"), width=12).pack(side="left", padx=5)

        self.filter_var = tk.StringVar(value="all")
        filter_frame = tk.Frame(self, bg="white", relief="solid", bd=1)
        filter_frame.pack(pady=10, padx=20, fill="x")
        tk.Label(filter_frame, text="Lọc:", font=("Arial", 11, "bold"),
                 bg="white").pack(side="left", padx=15, pady=10)
        tk.Radiobutton(filter_frame, text="Tất cả", variable=self.filter_var,
                       value="all", command=self.tim_kiem, bg="white",
                       font=("Arial", 10, "bold")).pack(side="left", padx=15)
        tk.Radiobutton(filter_frame, text="Chưa khám", variable=self.filter_var,
                       value="chua", command=self.tim_kiem, bg="white",
                       font=("Arial", 10, "bold")).pack(side="left", padx=15)
        tk.Radiobutton(filter_frame, text="Đã khám", variable=self.filter_var,
                       value="da", command=self.tim_kiem, bg="white",
                       font=("Arial", 10, "bold")).pack(side="left", padx=15)
        tk.Radiobutton(filter_frame, text="Đã hủy", variable=self.filter_var,
                       value="huy", command=self.tim_kiem, bg="white",
                       font=("Arial", 10, "bold")).pack(side="left", padx=15)

        tree_frame = tk.Frame(self, bg="white", relief="solid", bd=2)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        cols = ("Mã", "Mã BN", "Mã BS", "Mã Phòng", "Thời gian", "Trạng thái")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=20)

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="center")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.tag_configure("chua_kham", background="#fff3cd")
        self.tree.tag_configure("da_kham", background="#d4edda")
        self.tree.tag_configure("da_huy", background="#f8d7da")

        self.hom_nay()

    def hom_nay(self):
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.tim_kiem()

    def tim_kiem(self):
        date = self.entry_date.get().strip()
        if not date:
            return messagebox.showwarning("Lỗi", "Vui lòng nhập ngày!")

        for i in self.tree.get_children():
            self.tree.delete(i)

        query = """
            SELECT MaLichKham, MaBenhNhan, MaBacSi, MaPhong, NgayGioKham, TrangThai
            FROM LichKham WHERE CAST(NgayGioKham AS DATE) = ?
        """
        fv = self.filter_var.get()
        if fv == "chua":
            query += " AND TrangThai = N'Chưa khám'"
        elif fv == "da":
            query += " AND TrangThai = N'Đã khám'"
        elif fv == "huy":
            query += " AND TrangThai = N'Đã hủy'"

        query += " ORDER BY MaLichKham ASC"
        data = rows_to_list(execute_query(query, (date,), fetch=True))

        for row in data:
            tag = ""
            if row[5] == "Chưa khám":
                tag = "chua_kham"
            elif row[5] == "Đã khám":
                tag = "da_kham"
            elif row[5] == "Đã hủy":
                tag = "da_huy"
            self.tree.insert("", "end", values=row, tags=(tag,))

    def huy_lich(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Chọn", "Vui lòng chọn lịch cần hủy!")

        values = self.tree.item(sel[0], "values")
        ma, tt = values[0], values[5]

        if tt == "Đã khám":
            return messagebox.showwarning("Lỗi", "Không thể hủy lịch đã khám xong!")
        if tt == "Đã hủy":
            return messagebox.showinfo("Info", "Lịch này đã được hủy!")

        if messagebox.askyesno("Xác nhận", f"Hủy lịch mã {ma}?"):
            execute_query("UPDATE LichKham SET TrangThai = N'Đã hủy' WHERE MaLichKham = ?", (ma,))
            messagebox.showinfo("Thành công", "Đã hủy lịch!")
            self.tim_kiem()

# ==================== BÁO CÁO ====================
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

# ==================== CHẠY CHƯƠNG TRÌNH ====================
class HospitalPython(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CMC University - Quản lý bệnh viện")
        self.state('zoomed')

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (LoginForm, Dashboard, BenhNhanForm, BacSiForm, PhongKhamForm,
                  LichKhamForm, TraCuuForm, BaoCaoForm):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("LoginForm")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        if hasattr(frame, 'refresh'):
            frame.refresh()

if __name__ == "__main__":
    app = HospitalPython()
    app.mainloop()