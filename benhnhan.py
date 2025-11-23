# benhnhan.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import re
from database import execute_query, get_next_id, rows_to_list, execute_transaction


class BenhNhanForm(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f5f5f5")

        header = tk.Frame(self, bg="#3498db", height=80)
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="QUẢN LÝ BỆNH NHÂN",
                 font=("Arial", 24, "bold"), bg="#3498db", fg="white").pack(pady=20)

        # Frame chứa các nút chức năng
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

        # Frame tìm kiếm
        search_frame = tk.Frame(self, bg="#f5f5f5")
        search_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(search_frame, text="Tìm kiếm:", font=("Arial", 11, "bold"),
                 bg="#f5f5f5").pack(side="left", padx=5)

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                width=40, font=("Arial", 11))
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", self.tim_kiem)

        tk.Button(search_frame, text="Xóa tìm kiếm", command=self.xoa_tim_kiem,
                  bg="#6c757d", fg="white", font=("Arial", 10)).pack(side="left", padx=5)

        # Frame chứa bảng dữ liệu
        tree_frame = tk.Frame(self, bg="white", relief="solid", bd=2)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # TÊN CỘT HIỂN THỊ (tiếng Việt có dấu)
        cols = ("Mã BN", "Họ Tên", "Ngày Sinh", "Giới Tính", "Địa Chỉ", "Số ĐT", "Trạng Thái")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=20)

        # ĐẶT TIÊU ĐỀ TIẾNG VIỆT CHO CÁC CỘT
        column_headings = {
            "Mã BN": "Mã Bệnh Nhân",
            "Họ Tên": "Họ Tên",
            "Ngày Sinh": "Ngày Sinh",
            "Giới Tính": "Giới Tính",
            "Địa Chỉ": "Địa Chỉ",
            "Số ĐT": "Số Điện Thoại",
            "Trạng Thái": "Trạng Thái"
        }

        col_widths = [80, 150, 100, 80, 150, 100, 100]
        for col, width in zip(cols, col_widths):
            self.tree.heading(col, text=column_headings[col], command=lambda c=col: self.sort_column(c, False))
            self.tree.column(col, width=width, anchor="center")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.refresh()

    def sort_column(self, col, reverse):
        """Sắp xếp cột trong treeview"""
        try:
            l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
            try:
                l.sort(key=lambda t: int(t[0]), reverse=reverse)
            except ValueError:
                l.sort(reverse=reverse)
            for index, (val, k) in enumerate(l):
                self.tree.move(k, '', index)
            self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi sắp xếp: {str(e)}")

    def refresh(self):
        """Làm mới dữ liệu treeview"""
        try:
            for i in self.tree.get_children():
                self.tree.delete(i)

            data = rows_to_list(execute_query("SELECT * FROM BENHNHAN ORDER BY MaBenhNhan ASC", fetch=True))
            for row in data:
                self.tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tải dữ liệu: {str(e)}")

    def tim_kiem(self, event=None):
        """Tìm kiếm bệnh nhân theo từ khóa"""
        try:
            keyword = self.search_var.get().strip()
            if not keyword:
                self.refresh()
                return

            for i in self.tree.get_children():
                self.tree.delete(i)

            query = """
                    SELECT * \
                    FROM BENHNHAN
                    WHERE HoTen LIKE ? \
                       OR SoDienThoai LIKE ? \
                       OR DiaChi LIKE ? \
                       OR TrangThaiBenhNhan LIKE ?
                    ORDER BY MaBenhNhan ASC \
                    """
            params = (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
            data = rows_to_list(execute_query(query, params, fetch=True))

            if not data:
                messagebox.showinfo("Thông báo", "Không tìm thấy bệnh nhân nào phù hợp.")

            for row in data:
                self.tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tìm kiếm: {str(e)}")

    def xoa_tim_kiem(self):
        """Xóa kết quả tìm kiếm và hiển thị toàn bộ dữ liệu"""
        self.search_var.set("")
        self.refresh()

    def them(self):
        """Mở dialog thêm bệnh nhân mới"""
        self.open_dialog("Thêm bệnh nhân", True)

    def sua(self):
        """Mở dialog sửa thông tin bệnh nhân"""
        try:
            sel = self.tree.selection()
            if not sel:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn bệnh nhân cần sửa!")
                return
            values = self.tree.item(sel[0], "values")
            self.open_dialog("Sửa bệnh nhân", False, values)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi mở form sửa: {str(e)}")

    def xoa(self):
        """Xóa bệnh nhân và tất cả lịch khám liên quan"""
        try:
            sel = self.tree.selection()
            if not sel:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn bệnh nhân cần xóa!")
                return

            ma = self.tree.item(sel[0], "values")[0]
            ho_ten = self.tree.item(sel[0], "values")[1]

            # Đếm số lịch khám sẽ bị ảnh hưởng
            count_result = execute_query(
                "SELECT COUNT(*) FROM LichKham WHERE MaBenhNhan=?", (ma,), fetch=True
            )
            so_lich_kham = count_result[0][0] if count_result and count_result[0][0] else 0

            # Hiển thị cảnh báo chi tiết
            if so_lich_kham > 0:
                confirm_msg = (
                    f"Bạn có chắc chắn muốn xóa bệnh nhân '{ho_ten}' (Mã: {ma})?\n\n"
                    f"⚠️  CẢNH BÁO QUAN TRỌNG:\n"
                    f"• Tất cả {so_lich_kham} lịch khám liên quan đến bệnh nhân này sẽ bị xóa\n"
                    f"• Hành động này không thể hoàn tác!"
                )
            else:
                confirm_msg = f"Bạn có chắc chắn muốn xóa bệnh nhân '{ho_ten}' (Mã: {ma})?"

            if not messagebox.askyesno("XÁC NHẬN XÓA", confirm_msg, icon="warning"):
                return

            # Thực hiện xóa trong transaction
            queries = [
                ("DELETE FROM LichKham WHERE MaBenhNhan = ?", (ma,)),  # Xóa lịch khám trước
                ("DELETE FROM BENHNHAN WHERE MaBenhNhan = ?", (ma,))   # Xóa bệnh nhân sau
            ]

            results = execute_transaction(queries)

            # Thông báo thành công
            success_msg = f"Đã xóa bệnh nhân '{ho_ten}' thành công!"
            if so_lich_kham > 0:
                success_msg += f"\nĐã xóa {so_lich_kham} lịch khám liên quan."

            messagebox.showinfo("Thành công", success_msg)
            self.refresh()

        except Exception as e:
            error_msg = f"Lỗi khi xóa bệnh nhân: {str(e)}"
            # Hiển thị thông báo lỗi chi tiết hơn
            if "foreign key" in str(e).lower():
                error_msg += "\n\nCó thể vẫn còn dữ liệu liên quan chưa được xóa hết."
            messagebox.showerror("Lỗi", error_msg)

    # ========== VALIDATION FUNCTIONS ==========
    def validate_ho_ten(self, value):
        """Kiểm tra họ tên không được chứa số"""
        if any(char.isdigit() for char in value):
            return False
        return len(value.strip()) >= 2  # Ít nhất 2 ký tự

    def validate_ngay_sinh(self, value):
        """Kiểm tra ngày sinh không được trong tương lai và đúng định dạng dd-mm-yyyy"""
        try:
            # Kiểm tra định dạng dd-mm-yyyy
            if not re.match(r'^\d{2}-\d{2}-\d{4}$', value):
                return False

            # Tách ngày, tháng, năm
            day, month, year = map(int, value.split('-'))

            # Kiểm tra tính hợp lệ của ngày tháng
            if month < 1 or month > 12:
                return False
            if day < 1 or day > 31:
                return False

            # Kiểm tra số ngày trong tháng
            if month in [4, 6, 9, 11] and day > 30:
                return False
            if month == 2:
                # Kiểm tra năm nhuận
                if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                    if day > 29:
                        return False
                else:
                    if day > 28:
                        return False

            # Chuyển đổi sang datetime object
            ngay_sinh = datetime(year, month, day)
            hom_nay = datetime.now()

            # Kiểm tra không được trong tương lai
            if ngay_sinh > hom_nay:
                return False

            # Kiểm tra tuổi hợp lý (không quá 150 tuổi)
            min_age = datetime.now().replace(year=datetime.now().year - 150)
            if ngay_sinh < min_age:
                return False

            return True
        except (ValueError, Exception):
            return False

    def validate_dia_chi(self, value):
        """Kiểm tra địa chỉ không được chỉ chứa số"""
        if value.isdigit():
            return False
        return len(value.strip()) >= 5  # Ít nhất 5 ký tự

    def validate_so_dien_thoai(self, value):
        """Kiểm tra số điện thoại Việt Nam hợp lệ"""
        # Xóa khoảng trắng và dấu gạch ngang
        cleaned_value = re.sub(r'[\s\-]', '', value)

        # Kiểm tra chỉ chứa số
        if not cleaned_value.isdigit():
            return False

        # Kiểm tra độ dài (10-11 số)
        if len(cleaned_value) not in [10, 11]:
            return False

        # Kiểm tra đầu số Việt Nam
        valid_prefixes = ['09', '03', '07', '08', '05', '84']
        if not any(cleaned_value.startswith(prefix) for prefix in valid_prefixes):
            return False

        return True

    def format_ngay_sinh_for_database(self, value):
        """Chuyển đổi từ dd-mm-yyyy sang yyyy-mm-dd để lưu database"""
        try:
            if '-' in value:
                parts = value.split('-')
                if len(parts) == 3:
                    if len(parts[2]) == 4:  # Định dạng dd-mm-yyyy
                        return f"{parts[2]}-{parts[1]}-{parts[0]}"
            return value
        except:
            return value

    def format_ngay_sinh_for_display(self, value):
        """Chuyển đổi từ yyyy-mm-dd sang dd-mm-yyyy để hiển thị"""
        try:
            if '-' in value:
                parts = value.split('-')
                if len(parts) == 3:
                    if len(parts[0]) == 4:  # Định dạng yyyy-mm-dd
                        return f"{parts[2]}-{parts[1]}-{parts[0]}"
            return value
        except:
            return value

    def open_dialog(self, title, is_add, data=None):
        """Mở dialog thêm/sửa bệnh nhân"""
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("500x650")
        dialog.configure(bg="#f0f0f0")
        dialog.resizable(False, False)
        dialog.transient(self)  # Luôn hiển thị trên cửa sổ chính
        dialog.grab_set()  # Modal dialog

        main_frame = tk.Frame(dialog, bg="white", relief="solid", bd=2)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(main_frame, text=title.upper(), font=("Arial", 16, "bold"),
                 bg="white", fg="#3498db").pack(pady=15)

        form_frame = tk.Frame(main_frame, bg="white")
        form_frame.pack(padx=30, pady=10)

        labels = ["Họ tên:", "Ngày sinh (dd-mm-yyyy):", "Giới tính:", "Địa chỉ:", "Số điện thoại:", "Trạng thái:"]
        entries = []
        error_labels = []

        # Tạo combobox cho giới tính
        gioi_tinh_combo = ttk.Combobox(form_frame, values=["Nam", "Nữ"],
                                       state="readonly", font=("Arial", 11), width=32)
        gioi_tinh_combo.set("Nam")  # Giá trị mặc định

        # Tạo combobox cho trạng thái
        trang_thai_combo = ttk.Combobox(form_frame,
                                        values=["Đã khám", "Chưa khám", "Đang điều trị"],
                                        state="readonly", font=("Arial", 11), width=32)
        trang_thai_combo.set("Chưa khám")  # Giá trị mặc định

        for i, l in enumerate(labels):
            tk.Label(form_frame, text=l, font=("Arial", 11, "bold"),
                     bg="white").grid(row=i * 2, column=0, padx=10, pady=8, sticky="w")

            # Tạo label lỗi
            error_label = tk.Label(form_frame, text="", font=("Arial", 8),
                                   bg="white", fg="red")
            error_label.grid(row=i * 2 + 1, column=1, sticky="w")
            error_labels.append(error_label)

            if l == "Giới tính:":
                gioi_tinh_combo.grid(row=i * 2, column=1, padx=10, pady=8, sticky="w")
                entries.append(gioi_tinh_combo)
            elif l == "Trạng thái:":
                trang_thai_combo.grid(row=i * 2, column=1, padx=10, pady=8, sticky="w")
                entries.append(trang_thai_combo)
            else:
                e = tk.Entry(form_frame, width=35, font=("Arial", 11))
                e.grid(row=i * 2, column=1, padx=10, pady=8, sticky="w")
                entries.append(e)

        # Thêm hướng dẫn định dạng ngày sinh
        tk.Label(form_frame, text="(dd-mm-yyyy)", font=("Arial", 9, "italic"),
                 bg="white", fg="#666").grid(row=1, column=2, sticky="w")

        # Thêm hướng dẫn số điện thoại
        tk.Label(form_frame, text="(VD: 0912345678)", font=("Arial", 9, "italic"),
                 bg="white", fg="#666").grid(row=4, column=2, sticky="w")

        # Điền dữ liệu nếu là sửa
        if not is_add and data:
            entries[0].insert(0, data[1])  # Họ tên
            # Định dạng lại ngày sinh từ yyyy-mm-dd sang dd-mm-yyyy để hiển thị
            ngay_sinh_display = self.format_ngay_sinh_for_display(data[2])
            entries[1].insert(0, ngay_sinh_display)  # Ngày sinh
            gioi_tinh_combo.set(data[3])  # Giới tính
            entries[3].insert(0, data[4])  # Địa chỉ
            entries[4].insert(0, data[5])  # Số điện thoại
            trang_thai_combo.set(data[6])  # Trạng thái

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
                    if label_text == "Họ tên:":
                        if not self.validate_ho_ten(value):
                            error_labels[i].config(text="Họ tên không được chứa số và phải có ít nhất 2 ký tự!")
                            has_error = True

                    elif label_text == "Ngày sinh:":
                        if not self.validate_ngay_sinh(value):
                            error_labels[i].config(
                                text="Ngày sinh không hợp lệ! Định dạng: dd-mm-yyyy và không được trong tương lai.")
                            has_error = True
                        else:
                            # Chuyển đổi sang định dạng database trước khi lưu
                            value = self.format_ngay_sinh_for_database(value)

                    elif label_text == "Địa chỉ:":
                        if not self.validate_dia_chi(value):
                            error_labels[i].config(
                                text="Địa chỉ không hợp lệ! Phải có ít nhất 5 ký tự và không chỉ chứa số.")
                            has_error = True

                    elif label_text == "Số điện thoại:":
                        if not self.validate_so_dien_thoai(value):
                            error_labels[i].config(
                                text="Số điện thoại không hợp lệ! Phải là số điện thoại Việt Nam (10-11 số).")
                            has_error = True

                    vals.append(value)

                if has_error:
                    return

                # Nếu không có lỗi, tiến hành lưu
                if is_add:
                    ma = get_next_id("BENHNHAN", "MaBenhNhan")
                    execute_query("INSERT INTO BENHNHAN VALUES (?, ?, ?, ?, ?, ?, ?)", (ma, *vals))
                    messagebox.showinfo("Thành công", f"Đã thêm bệnh nhân mã {ma} thành công!")
                else:
                    ma = data[0]  # Mã bệnh nhân từ cột đầu tiên
                    execute_query(
                        "UPDATE BENHNHAN SET HoTen=?, NgaySinh=?, GioiTinh=?, DiaChi=?, SoDienThoai=?, TrangThaiBenhNhan=? WHERE MaBenhNhan=?",
                        (*vals, ma))
                    messagebox.showinfo("Thành công", f"Đã cập nhật bệnh nhân mã {ma} thành công!")

                self.refresh()
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
