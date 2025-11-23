# lichkham.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import execute_query, get_next_id, rows_to_list, execute_transaction
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

    def format_thoi_gian_for_display(self, value):
        """Chuyển đổi từ yyyy-mm-dd hh:mm:ss sang dd-mm-yyyy hh:mm để hiển thị"""
        try:
            if ' ' in value:
                date_part, time_part = value.split(' ')
                if '-' in date_part:
                    parts = date_part.split('-')
                    if len(parts) == 3:
                        if len(parts[0]) == 4:  # Định dạng yyyy-mm-dd
                            # Giữ nguyên phần thời gian, chỉ chuyển đổi ngày tháng
                            time_display = time_part.split(':')[0] + ':' + time_part.split(':')[1]  # Bỏ giây
                            return f"{parts[2]}-{parts[1]}-{parts[0]} {time_display}"
            return value
        except:
            return value

    def format_thoi_gian_for_database(self, value):
        """Chuyển đổi từ dd-mm-yyyy hh:mm sang yyyy-mm-dd hh:mm để lưu database"""
        try:
            if ' ' in value:
                date_part, time_part = value.split(' ')
                if '-' in date_part:
                    parts = date_part.split('-')
                    if len(parts) == 3:
                        if len(parts[2]) == 4:  # Định dạng dd-mm-yyyy
                            return f"{parts[2]}-{parts[1]}-{parts[0]} {time_part}"
            return value
        except:
            return value

    def validate_thoi_gian(self, value):
        """Kiểm tra định dạng thời gian dd-mm-yyyy hh:mm"""
        try:
            if ' ' in value:
                date_part, time_part = value.split(' ')
                # Kiểm tra định dạng ngày dd-mm-yyyy
                if not len(date_part.split('-')) == 3:
                    return False, "Định dạng ngày không đúng (dd-mm-yyyy)"
                day, month, year = map(int, date_part.split('-'))

                # Kiểm tra định dạng thời gian hh:mm
                if not len(time_part.split(':')) == 2:
                    return False, "Định dạng giờ không đúng (hh:mm)"
                hour, minute = map(int, time_part.split(':'))

                # Kiểm tra tính hợp lệ
                if month < 1 or month > 12:
                    return False, "Tháng phải từ 1 đến 12"
                if day < 1 or day > 31:
                    return False, "Ngày phải từ 1 đến 31"
                if hour < 0 or hour > 23:
                    return False, "Giờ phải từ 00 đến 23"
                if minute < 0 or minute > 59:
                    return False, "Phút phải từ 00 đến 59"

                # Kiểm tra số ngày trong tháng
                if month in [4, 6, 9, 11] and day > 30:
                    return False, f"Tháng {month} chỉ có 30 ngày"
                if month == 2:
                    # Kiểm tra năm nhuận
                    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                        if day > 29:
                            return False, "Tháng 2 năm nhuận chỉ có 29 ngày"
                    else:
                        if day > 28:
                            return False, "Tháng 2 chỉ có 28 ngày"

                # Kiểm tra không được trong quá khứ
                ngay_gio = datetime(year, month, day, hour, minute)
                if ngay_gio < datetime.now():
                    return False, "Thời gian không được trong quá khứ"

                return True, "Hợp lệ"
            return False, "Thiếu phần thời gian"
        except ValueError:
            return False, "Định dạng số không đúng"
        except Exception:
            return False, "Định dạng không hợp lệ"

    def refresh(self):
        """Làm mới dữ liệu treeview với kiểm tra tồn tại"""
        for i in self.tree.get_children():
            self.tree.delete(i)

        query = """
                SELECT lk.MaLichKham, \
                       lk.MaBenhNhan, \
                       lk.MaBacSi, \
                       lk.MaPhong, \
                       lk.NgayGioKham, \
                       lk.TrangThai, \
                       COALESCE(bn.HoTen, 'ĐÃ XÓA')    as TenBN, \
                       COALESCE(bs.HoTen, 'ĐÃ XÓA')    as TenBS, \
                       COALESCE(pk.TenPhong, 'ĐÃ XÓA') as TenPhong
                FROM LichKham lk
                         LEFT JOIN BenhNhan bn ON lk.MaBenhNhan = bn.MaBenhNhan
                         LEFT JOIN BacSi bs ON lk.MaBacSi = bs.MaBacSi
                         LEFT JOIN PhongKham pk ON lk.MaPhong = pk.MaPhong
                WHERE 1 = 1 \
                """

        fv = self.filter_var.get()
        if fv == "chua":
            query += " AND lk.TrangThai = N'Chưa khám'"
        elif fv == "da":
            query += " AND lk.TrangThai = N'Đã khám'"
        elif fv == "huy":
            query += " AND lk.TrangThai = N'Đã hủy'"

        query += " ORDER BY lk.MaLichKham ASC"

        data = rows_to_list(execute_query(query, fetch=True))

        for row in data:
            tag = ""
            ma_bn_display = row[1]
            ma_bs_display = row[2]
            ma_phong_display = row[3]
            thoi_gian_display = self.format_thoi_gian_for_display(row[4])

            if row[6] == 'ĐÃ XÓA':
                ma_bn_display = f"{row[1]} (ĐÃ XÓA)"
            if row[7] == 'ĐÃ XÓA':
                ma_bs_display = f"{row[2]} (ĐÃ XÓA)"
            if row[8] == 'ĐÃ XÓA':
                ma_phong_display = f"{row[3]} (ĐÃ XÓA)"

            if row[5] == "Chưa khám":
                tag = "chua_kham"
            elif row[5] == "Đã khám":
                tag = "da_kham"
            elif row[5] == "Đã hủy":
                tag = "da_huy"

            display_values = (row[0], ma_bn_display, ma_bs_display, ma_phong_display, thoi_gian_display, row[5])
            self.tree.insert("", "end", values=display_values, tags=(tag,))

    def dat_lich(self):
        """Mở dialog thêm lịch khám mới"""
        self.open_dialog("Thêm lịch khám", True)

    def sua_lich(self):
        """Mở dialog sửa thông tin lịch khám"""
        try:
            sel = self.tree.selection()
            if not sel:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn lịch khám cần sửa!")
                return
            values = self.tree.item(sel[0], "values")

            # Kiểm tra xem lịch có bị ảnh hưởng bởi xóa không
            if "(ĐÃ XÓA)" in str(values[1]) or "(ĐÃ XÓA)" in str(values[2]) or "(ĐÃ XÓA)" in str(values[3]):
                return messagebox.showwarning("Lỗi",
                                              "Không thể sửa lịch này!\nBệnh nhân, bác sĩ hoặc phòng đã bị xóa.\nVui lòng tạo lịch mới.")

            # KHÔNG cho sửa lịch đã hủy
            if values[5] == "Đã hủy":
                return messagebox.showwarning("Lỗi", "Không thể sửa lịch đã hủy! Hãy tạo lịch mới.")

            self.open_dialog("Sửa lịch khám", False, values)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi mở form sửa: {str(e)}")

    def huy_lich(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Chọn", "Vui lòng chọn lịch cần hủy!")

        values = self.tree.item(sel[0], "values")
        ma, tt = values[0], values[5]

        if tt == "Đã khám":
            return messagebox.showwarning("Lỗi", "Không thể hủy lịch đã khám!")

        if tt == "Đã hủy":
            return messagebox.showwarning("Lỗi", "Lịch này đã được hủy trước đó!")

        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn hủy lịch mã {ma}?"):
            execute_query("UPDATE LichKham SET TrangThai = N'Đã hủy' WHERE MaLichKham = ?", (ma,))
            messagebox.showinfo("Thành công", "Đã hủy lịch!")
            self.refresh()
            self.controller.frames["Dashboard"].refresh()

    def open_dialog(self, title, is_add, data=None):
        """Mở dialog thêm/sửa lịch khám"""
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("500x600")
        dialog.configure(bg="#f0f0f0")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        main_frame = tk.Frame(dialog, bg="white", relief="solid", bd=2)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(main_frame, text=title.upper(), font=("Arial", 16, "bold"),
                 bg="white", fg="#007acc").pack(pady=15)

        form_frame = tk.Frame(main_frame, bg="white")
        form_frame.pack(padx=30, pady=10)

        labels = ["Mã Bệnh nhân:", "Mã Bác sĩ:", "Mã Phòng:", "Ngày giờ (dd-mm-yyyy hh:mm):", "Trạng thái:"]
        entries = []
        error_labels = []

        # Tạo combobox cho trạng thái
        trang_thai_combo = ttk.Combobox(form_frame,
                                        values=["Chưa khám", "Đã khám"],
                                        state="readonly", font=("Arial", 11), width=32)
        trang_thai_combo.set("Chưa khám")

        for i, txt in enumerate(labels):
            tk.Label(form_frame, text=txt, font=("Arial", 11, "bold"),
                     bg="white").grid(row=i * 2, column=0, padx=10, pady=12, sticky="w")

            # Tạo label lỗi
            error_label = tk.Label(form_frame, text="", font=("Arial", 8),
                                   bg="white", fg="red")
            error_label.grid(row=i * 2 + 1, column=1, sticky="w")
            error_labels.append(error_label)

            if txt == "Trạng thái:":
                trang_thai_combo.grid(row=i * 2, column=1, padx=10, pady=12, sticky="w")
                entries.append(trang_thai_combo)
            else:
                e = tk.Entry(form_frame, width=35, font=("Arial", 11))
                e.grid(row=i * 2, column=1, padx=10, pady=12, sticky="w")
                entries.append(e)

        # Thêm hướng dẫn cho thời gian
        tk.Label(form_frame, text="(VD: 15-01-2025 09:30)",
                 font=("Arial", 9, "italic"), bg="white", fg="#666").grid(row=7, column=1, sticky="w", padx=10)

        # Điền dữ liệu nếu là sửa
        if not is_add and data:
            entries[0].insert(0, data[1])  # Mã BN
            entries[1].insert(0, data[2])  # Mã BS
            entries[2].insert(0, data[3])  # Mã Phòng

            # Định dạng lại thời gian từ hiển thị sang nhập
            thoi_gian_nhap = data[4]  # Đã ở định dạng dd-mm-yyyy hh:mm từ refresh
            entries[3].insert(0, thoi_gian_nhap)

            trang_thai_combo.set(data[5])  # Trạng thái

        def validate_and_save():
            """Validate và lưu dữ liệu"""
            try:
                # Clear all error messages
                for error_label in error_labels:
                    error_label.config(text="")

                vals = []
                has_error = False

                # Validate từng trường
                for i, (entry, label_text) in enumerate(zip(entries, labels)):
                    value = entry.get().strip()

                    if not value:
                        error_labels[i].config(text=f"{label_text} không được để trống!")
                        has_error = True
                        continue

                    # Validate cụ thể cho từng trường
                    if label_text == "Ngày giờ (dd-mm-yyyy hh:mm):":
                        is_valid, error_msg = self.validate_thoi_gian(value)
                        if not is_valid:
                            error_labels[i].config(text=error_msg)
                            has_error = True
                        else:
                            # Chuyển đổi sang định dạng database trước khi lưu
                            value = self.format_thoi_gian_for_database(value)

                    vals.append(value)

                if has_error:
                    return

                # Kiểm tra tồn tại các mã
                ma_bn, ma_bs, ma_phong = vals[0], vals[1], vals[2]

                # Kiểm tra bệnh nhân
                bn_check = execute_query("SELECT HoTen FROM BenhNhan WHERE MaBenhNhan=?", (ma_bn,), fetch=True)
                if not bn_check:
                    error_labels[0].config(text="Mã bệnh nhân không tồn tại!")
                    has_error = True

                # Kiểm tra bác sĩ
                bs_check = execute_query("SELECT HoTen FROM BacSi WHERE MaBacSi=?", (ma_bs,), fetch=True)
                if not bs_check:
                    error_labels[1].config(text="Mã bác sĩ không tồn tại!")
                    has_error = True

                # Kiểm tra phòng
                phong_check = execute_query("SELECT TenPhong, TinhTrang FROM PhongKham WHERE MaPhong=?", (ma_phong,),
                                            fetch=True)
                if not phong_check:
                    error_labels[2].config(text="Mã phòng không tồn tại!")
                    has_error = True
                else:
                    ten_phong, tinh_trang = phong_check[0]
                    if tinh_trang != "Còn trống":
                        error_labels[2].config(text=f"Phòng đang {tinh_trang.lower()} - không thể đặt lịch!")
                        has_error = True

                # Kiểm tra trùng lịch
                if not has_error:
                    ma_lich_hien_tai = data[0] if not is_add else None
                    is_valid, msg = kiem_tra_trung_lich(ma_bs, ma_phong, vals[3], ma_lich_hien_tai)
                    if not is_valid:
                        error_labels[3].config(text=msg)
                        has_error = True

                if has_error:
                    return

                # Nếu không có lỗi, tiến hành lưu
                if is_add:
                    ma = get_next_id("LichKham", "MaLichKham")
                    execute_query("INSERT INTO LichKham VALUES (?, ?, ?, ?, ?, ?)",
                                  (ma, vals[0], vals[1], vals[2], vals[3], vals[4]))
                    messagebox.showinfo("Thành công", f"Đã thêm lịch khám mã {ma} thành công!")
                else:
                    ma = data[0]  # Mã lịch từ cột đầu tiên
                    execute_query(
                        "UPDATE LichKham SET MaBenhNhan=?, MaBacSi=?, MaPhong=?, NgayGioKham=?, TrangThai=? WHERE MaLichKham=?",
                        (vals[0], vals[1], vals[2], vals[3], vals[4], ma))
                    messagebox.showinfo("Thành công", f"Đã cập nhật lịch khám mã {ma} thành công!")

                self.refresh()
                self.controller.frames["Dashboard"].refresh()
                dialog.destroy()

            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi lưu dữ liệu: {str(e)}")

        btn_frame = tk.Frame(main_frame, bg="white")
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Lưu", command=validate_and_save, bg="#28a745", fg="white",
                  font=("Arial", 12, "bold"), width=15, height=2).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Hủy", command=dialog.destroy, bg="#6c757d", fg="white",
                  font=("Arial", 12, "bold"), width=15, height=2).pack(side="left", padx=10)

        # Focus vào trường đầu tiên
        entries[0].focus_set()

        # Bind phím Enter để save
        dialog.bind('<Return>', lambda e: validate_and_save())

        # Bind phím Escape để hủy
        dialog.bind('<Escape>', lambda e: dialog.destroy())
