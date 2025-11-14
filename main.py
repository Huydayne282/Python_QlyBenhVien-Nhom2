# main.py
import tkinter as tk
from login import LoginForm
from dashboard import Dashboard
from benhnhan import BenhNhanForm
from bacsi import BacSiForm
from phongkham import PhongKhamForm
from lichkham import LichKhamForm
from tracuu import TraCuuForm
from baocao import BaoCaoForm

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