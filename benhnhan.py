# benhnhan.py
import tkinter as tk
from tkinter import ttk, messagebox
from database import execute_query, get_next_id, rows_to_list

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