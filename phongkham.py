# phongkham.py
import tkinter as tk
from tkinter import ttk, messagebox
from database import execute_query, get_next_id, rows_to_list, execute_transaction


class PhongKhamForm(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f5f5f5")

        header = tk.Frame(self, bg="#f39c12", height=80)
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="QUẢN LÝ PHÒNG KHÁM",
                 font=("Arial", 24, "bold"), bg="#f39c12", fg="white").pack(pady=20)

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
        cols = ("Mã Phòng", "Tên Phòng", "Chuyên Khoa", "Tình Trạng")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=20)

        # ĐẶT TIÊU ĐỀ TIẾNG VIỆT CHO CÁC CỘT
        column_headings = {
            "Mã Phòng": "Mã Phòng",
            "Tên Phòng": "Tên Phòng",
            "Chuyên Khoa": "Chuyên Khoa",
            "Tình Trạng": "Tình Trạng"
        }

        col_widths = [100, 200, 200, 150]
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
            data = rows_to_list(
                execute_query("SELECT MaPhong, TenPhong, ChuyenKhoa, TinhTrang FROM PHONGKHAM ORDER BY MaPhong ASC",
                              fetch=True))
            for row in data:
                self.tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tải dữ liệu: {str(e)}")

    def tim_kiem(self, event=None):
        """Tìm kiếm phòng khám theo từ khóa"""
        try:
            keyword = self.search_var.get().strip()
            if not keyword:
                self.refresh()
                return

            for i in self.tree.get_children():
                self.tree.delete(i)

            query = """
                    SELECT * \
                    FROM PHONGKHAM
                    WHERE TenPhong LIKE ? \
                       OR ChuyenKhoa LIKE ? \
                       OR TìnhTrang LIKE ?
                    ORDER BY MaPhong ASC \
                    """
            params = (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
            data = rows_to_list(execute_query(query, params, fetch=True))

            if not data:
                messagebox.showinfo("Thông báo", "Không tìm thấy phòng khám nào phù hợp.")

            for row in data:
                self.tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tìm kiếm: {str(e)}")

    def xoa_tim_kiem(self):
        """Xóa kết quả tìm kiếm và hiển thị toàn bộ dữ liệu"""
        self.search_var.set("")
        self.refresh()

    def them(self):
        """Mở dialog thêm phòng khám mới"""
        self.open_dialog("Thêm phòng khám", True)

    def sua(self):
        """Mở dialog sửa thông tin phòng khám"""
        try:
            sel = self.tree.selection()
            if not sel:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn phòng khám cần sửa!")
                return
            values = self.tree.item(sel[0], "values")
            self.open_dialog("Sửa phòng khám", False, values)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi mở form sửa: {str(e)}")

    def xoa(self):
        """Xóa phòng khám và tất cả lịch khám liên quan"""
        try:
            sel = self.tree.selection()
            if not sel:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn phòng khám cần xóa!")
                return

            ma = self.tree.item(sel[0], "values")[0]
            ten_phong = self.tree.item(sel[0], "values")[1]

            # Đếm số lịch khám sẽ bị ảnh hưởng
            count_result = execute_query(
                "SELECT COUNT(*) FROM LichKham WHERE MaPhong=?", (ma,), fetch=True
            )
            so_lich_kham = count_result[0][0] if count_result and count_result[0][0] else 0

            # Hiển thị cảnh báo chi tiết
            if so_lich_kham > 0:
                confirm_msg = (
                    f"Bạn có chắc chắn muốn xóa phòng '{ten_phong}' (Mã: {ma})?\n\n"
                    f"⚠️  CẢNH BÁO QUAN TRỌNG:\n"
                    f"• Tất cả {so_lich_kham} lịch khám liên quan đến phòng này sẽ bị xóa\n"
                    f"• Hành động này không thể hoàn tác!"
                )
            else:
                confirm_msg = f"Bạn có chắc chắn muốn xóa phòng '{ten_phong}' (Mã: {ma})?"

            if not messagebox.askyesno("XÁC NHẬN XÓA", confirm_msg, icon="warning"):
                return

            # Thực hiện xóa trong transaction
            queries = [
                ("DELETE FROM LichKham WHERE MaPhong = ?", (ma,)),  # Xóa lịch khám trước
                ("DELETE FROM PHONGKHAM WHERE MaPhong = ?", (ma,))  # Xóa phòng sau
            ]

            results = execute_transaction(queries)

            # Thông báo thành công
            success_msg = f"Đã xóa phòng '{ten_phong}' thành công!"
            if so_lich_kham > 0:
                success_msg += f"\nĐã xóa {so_lich_kham} lịch khám liên quan."

            messagebox.showinfo("Thành công", success_msg)
            self.refresh()

        except Exception as e:
            error_msg = f"Lỗi khi xóa phòng khám: {str(e)}"
            # Hiển thị thông báo lỗi chi tiết hơn
            if "foreign key" in str(e).lower():
                error_msg += "\n\nCó thể vẫn còn dữ liệu liên quan chưa được xóa hết."
            messagebox.showerror("Lỗi", error_msg)

    # ========== VALIDATION FUNCTIONS ==========
    def validate_ten_phong(self, value):
        """Kiểm tra tên phòng không được trống"""
        return len(value.strip()) >= 2  # Ít nhất 2 ký tự

    def validate_chuyen_khoa(self, value):
        """Kiểm tra chuyên khoa không được chứa số"""
        if any(char.isdigit() for char in value):
            return False
        return len(value.strip()) >= 3  # Ít nhất 3 ký tự

    def validate_ten_phong_trung(self, ten_phong, ma_hien_tai=None):
        """Kiểm tra tên phòng không được trùng"""
        try:
            if ma_hien_tai:  # Trường hợp sửa
                query = "SELECT COUNT(*) FROM PHONGKHAM WHERE TenPhong=? AND MaPhong!=?"
                params = (ten_phong, ma_hien_tai)
            else:  # Trường hợp thêm
                query = "SELECT COUNT(*) FROM PHONGKHAM WHERE TenPhong=?"
                params = (ten_phong,)

            result = execute_query(query, params, fetch=True)
            return result[0][0] == 0  # Trả về True nếu không trùng
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi kiểm tra tên phòng: {str(e)}")
            return False

    def open_dialog(self, title, is_add, data=None):
        """Mở dialog thêm/sửa phòng khám"""
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("500x500")
        dialog.configure(bg="#f0f0f0")
        dialog.resizable(False, False)
        dialog.transient(self)  # Luôn hiển thị trên cửa sổ chính
        dialog.grab_set()  # Modal dialog

        main_frame = tk.Frame(dialog, bg="white", relief="solid", bd=2)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(main_frame, text=title.upper(), font=("Arial", 16, "bold"),
                 bg="white", fg="#f39c12").pack(pady=15)

        form_frame = tk.Frame(main_frame, bg="white")
        form_frame.pack(padx=30, pady=10)

        labels = ["Tên phòng:", "Chuyên khoa:", "Tình trạng:"]
        entries = []
        error_labels = []

        # Tạo combobox cho chuyên khoa
        chuyen_khoa_combo = ttk.Combobox(form_frame,
                                         values=[
                                             "Tim mạch", "Nội tổng quát", "Ngoại khoa", "Sản phụ khoa",
                                             "Nhi khoa", "Tai Mũi Họng", "Răng Hàm Mặt", "Da liễu",
                                             "Thần kinh", "Xương khớp", "Mắt", "Tiêu hóa", "Cấp cứu"
                                         ],
                                         state="readonly", font=("Arial", 11), width=32
                                         )
        chuyen_khoa_combo.set("Nội tổng quát")

        # Tạo combobox cho tình trạng
        tinh_trang_combo = ttk.Combobox(form_frame,
                                        values=["Còn trống", "Đang sử dụng", "Đang bảo trì", "Tạm đóng"],
                                        state="readonly", font=("Arial", 11), width=32
                                        )
        tinh_trang_combo.set("Còn trống")

        for i, txt in enumerate(labels):
            tk.Label(form_frame, text=txt, font=("Arial", 11, "bold"),
                     bg="white").grid(row=i * 2, column=0, padx=10, pady=12, sticky="w")

            # Tạo label lỗi
            error_label = tk.Label(form_frame, text="", font=("Arial", 8),
                                   bg="white", fg="red")
            error_label.grid(row=i * 2 + 1, column=1, sticky="w")
            error_labels.append(error_label)

            if txt == "Chuyên khoa:":
                chuyen_khoa_combo.grid(row=i * 2, column=1, padx=10, pady=12, sticky="w")
                entries.append(chuyen_khoa_combo)
            elif txt == "Tình trạng:":
                tinh_trang_combo.grid(row=i * 2, column=1, padx=10, pady=12, sticky="w")
                entries.append(tinh_trang_combo)
            else:
                e = tk.Entry(form_frame, width=35, font=("Arial", 11))
                e.grid(row=i * 2, column=1, padx=10, pady=12, sticky="w")
                entries.append(e)

        # Điền dữ liệu nếu là sửa
        if not is_add and data:
            entries[0].insert(0, data[1])  # Tên phòng
            chuyen_khoa_combo.set(data[2])  # Chuyên khoa
            tinh_trang_combo.set(data[3])  # Tình trạng

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
                    if label_text == "Tên phòng:":
                        if not self.validate_ten_phong(value):
                            error_labels[i].config(text="Tên phòng phải có ít nhất 2 ký tự!")
                            has_error = True
                        else:
                            # Kiểm tra trùng tên phòng
                            ma_hien_tai = data[0] if not is_add else None
                            if not self.validate_ten_phong_trung(value, ma_hien_tai):
                                error_labels[i].config(text="Tên phòng này đã tồn tại!")
                                has_error = True

                    elif label_text == "Chuyên khoa:":
                        if not self.validate_chuyen_khoa(value):
                            error_labels[i].config(text="Chuyên khoa không được chứa số và phải có ít nhất 3 ký tự!")
                            has_error = True

                    vals.append(value)

                if has_error:
                    return

                # Nếu không có lỗi, tiến hành lưu
                if is_add:
                    ma = get_next_id("PHONGKHAM", "MaPhong")
                    execute_query(
                        "INSERT INTO PHONGKHAM (MaPhong, TenPhong, ChuyenKhoa, TinhTrang) VALUES (?, ?, ?, ?)",
                        (ma, *vals))
                    messagebox.showinfo("Thành công", f"Đã thêm phòng mã {ma} thành công!")
                else:
                    ma = data[0]  # Mã phòng từ cột đầu tiên
                    execute_query("UPDATE PHONGKHAM SET TenPhong=?, ChuyenKhoa=?, TinhTrang=? WHERE MaPhong=?",
                                  (vals[0], vals[1], vals[2], ma))
                    messagebox.showinfo("Thành công", f"Đã cập nhật phòng mã {ma} thành công!")

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

        # Bind phím Escape để hủy
        dialog.bind('<Escape>', lambda e: dialog.destroy())
