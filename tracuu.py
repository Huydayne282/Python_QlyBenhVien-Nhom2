# tracuu.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import execute_query, rows_to_list

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
