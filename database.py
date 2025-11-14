# database.py
import pyodbc
from tkinter import messagebox
from datetime import datetime, timedelta

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