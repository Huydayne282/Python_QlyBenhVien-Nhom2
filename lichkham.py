# lichkham.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import execute_query, get_next_id, rows_to_list
from utils import kiem_tra_trung_lich

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

        # Mã BN
        tk.Label(form_frame, text="Mã Bệnh nhân:", font=("Arial", 11, "bold"),
                 bg="white", fg="#333").grid(row=0, column=0, padx=10, pady=12, sticky="w")
        e_bn = tk.Entry(form_frame, width=35, font=("Arial", 11))
        e_bn.grid(row=0, column=1, padx=10, pady=12)
        lbl_bn_info = tk.Label(form_frame, text="", font=("Arial", 9), bg="white", fg="#0066cc")
        lbl_bn_info.grid(row=1, column=1, sticky="w", padx=10)

        def show_bn_list():
            bn_data = execute_query("SELECT MaBenhNhan, HoTen, SoDienThoai FROM BenhNhan ORDER BY MaBenhNhan", fetch=True)
            self.show_list_window(dialog, "Danh sách bệnh nhân", bn_data, ["Mã", "Họ tên", "SĐT"], e_bn, lbl_bn_info, lambda v: f"✓ {v[1]} - SĐT: {v[2]}")

        # Mã BS
        tk.Label(form_frame, text="Mã Bác sĩ:", font=("Arial", 11, "bold"),
                 bg="white", fg="#333").grid(row=2, column=0, padx=10, pady=12, sticky="w")
        e_bs = tk.Entry(form_frame, width=35, font=("Arial", 11))
        e_bs.grid(row=2, column=1, padx=10, pady=12)
        lbl_bs_info = tk.Label(form_frame, text="", font=("Arial", 9), bg="white", fg="#0066cc")
        lbl_bs_info.grid(row=3, column=1, sticky="w", padx=10)

        def show_bs_list():
            bs_data = execute_query("SELECT MaBacSi, HoTen, ChuyenKhoa FROM BacSi ORDER BY MaBacSi", fetch=True)
            self.show_list_window(dialog, "Danh sách bác sĩ", bs_data, ["Mã", "Họ tên", "Chuyên khoa"], e_bs, lbl_bs_info, lambda v: f"✓ {v[1]} - {v[2]}")

        # Mã Phòng
        tk.Label(form_frame, text="Mã Phòng:", font=("Arial", 11, "bold"),
                 bg="white", fg="#333").grid(row=4, column=0, padx=10, pady=12, sticky="w")
        e_phong = tk.Entry(form_frame, width=35, font=("Arial", 11))
        e_phong.grid(row=4, column=1, padx=10, pady=12)
        lbl_phong_info = tk.Label(form_frame, text="", font=("Arial", 9), bg="white", fg="#0066cc")
        lbl_phong_info.grid(row=5, column=1, sticky="w", padx=10)

        def show_phong_list():
            phong_data = execute_query("SELECT MaPhong, TenPhong, ChuyenKhoa FROM PhongKham ORDER BY MaPhong", fetch=True)
            self.show_list_window(dialog, "Danh sách phòng khám", phong_data, ["Mã", "Tên phòng", "Chuyên khoa"], e_phong, lbl_phong_info, lambda v: f"✓ {v[1]} - {v[2]}")

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

        # Nút chọn danh sách
        tk.Button(form_frame, text="...", command=show_bn_list, width=3).grid(row=0, column=2, padx=5)
        tk.Button(form_frame, text="...", command=show_bs_list, width=3).grid(row=2, column=2, padx=5)
        tk.Button(form_frame, text="...", command=show_phong_list, width=3).grid(row=4, column=2, padx=5)

        # Kiểm tra
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
                info_text = f"Đã có thể đặt lịch!\n\n"
                info_text += f"• Bác sĩ {bs}: {count_bs}/18 ca trong ngày\n"
                info_text += f"• Phòng {phong}: {count_phong}/18 ca trong ngày\n"
                info_text += f"• Thời gian: {time} (Trống)"
                check_label.config(text=info_text, fg="green")
            else:
                check_label.config(text=f"Không thể đặt: {msg}", fg="red")

        def save():
            bn = e_bn.get().strip()
            bs = e_bs.get().strip()
            phong = e_phong.get().strip()
            time = e_time.get().strip()
            status = status_var.get()

            if not all([bn, bs, phong, time]):
                return messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")

            try:
                datetime.strptime(time, "%Y-%m-%d %H:%M")
            except ValueError:
                return messagebox.showerror("Lỗi", "Định dạng thời gian không đúng! Vui lòng nhập theo format: YYYY-MM-DD HH:MM")

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

    def show_list_window(self, parent, title, data, cols, entry, label, format_func):
        list_window = tk.Toplevel(parent)
        list_window.title(title)
        list_window.geometry("700x450")

        tree_frame = tk.Frame(list_window)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=15)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=200, anchor="center")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        for row in data:
            tree.insert("", "end", values=row)

        def chon():
            sel = tree.selection()
            if sel:
                values = tree.item(sel[0], "values")
                entry.delete(0, tk.END)
                entry.insert(0, values[0])
                label.config(text=format_func(values))
                list_window.destroy()

        btn_frame = tk.Frame(list_window)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Chọn", command=chon, bg="#007acc", fg="white",
                  font=("Arial", 11, "bold"), width=15).pack(pady=10)

    def sua_lich(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Chọn", "Vui lòng chọn lịch cần sửa!")
        values = self.tree.item(sel[0], "values")
        ma_lich, ma_bn, ma_bs, ma_phong, ngay_gio, trang_thai = values
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

        tk.Label(form_frame, text="Mã Bệnh nhân:", font=("Arial", 11, "bold"),
                 bg="white").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        e_bn = tk.Entry(form_frame, width=30, font=("Arial", 11))
        e_bn.grid(row=0, column=1, padx=10, pady=10)
        e_bn.insert(0, ma_bn)

        tk.Label(form_frame, text="Mã Bác sĩ:", font=("Arial", 11, "bold"),
                 bg="white").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        e_bs = tk.Entry(form_frame, width=30, font=("Arial", 11))
        e_bs.grid(row=1, column=1, padx=10, pady=10)
        e_bs.insert(0, ma_bs)

        tk.Label(form_frame, text="Mã Phòng:", font=("Arial", 11, "bold"),
                 bg="white").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        e_phong = tk.Entry(form_frame, width=30, font=("Arial", 11))
        e_phong.grid(row=2, column=1, padx=10, pady=10)
        e_phong.insert(0, ma_phong)

        tk.Label(form_frame, text="Ngày giờ:", font=("Arial", 11, "bold"),
                 bg="white").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        e_time = tk.Entry(form_frame, width=30, font=("Arial", 11))
        e_time.grid(row=3, column=1, padx=10, pady=10)
        ngay_gio_simple = str(ngay_gio).split('.')[0]
        e_time.insert(0, ngay_gio_simple)
        tk.Label(form_frame, text="(VD: 2025-11-15 09:30)",
                 font=("Arial", 9, "italic"), bg="white", fg="#666").grid(row=4, column=1, sticky="w", padx=10)

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

            try:
                datetime.strptime(time, "%Y-%m-%d %H:%M")
            except ValueError:
                return messagebox.showerror("Lỗi", "Định dạng thời gian không đúng! Vui lòng nhập theo format: YYYY-MM-DD HH:MM")

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