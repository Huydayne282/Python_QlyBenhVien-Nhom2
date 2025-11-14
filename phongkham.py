# phongkham.py
import tkinter as tk
from tkinter import ttk, messagebox
from database import execute_query, get_next_id, rows_to_list

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