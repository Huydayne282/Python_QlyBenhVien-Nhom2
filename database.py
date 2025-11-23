# database.py
import pyodbc
from tkinter import messagebox
from datetime import datetime, timedelta

connection_string = 'Driver={SQL Server};Server=LAPTOP-JINK9QGU;Database=Quanlybenhvienpython;UID=huy;PWD=123;'


def get_conn():
    return pyodbc.connect(connection_string)


def execute_query(query, params=None, fetch=False, commit=True):
    """Thực thi query với hỗ trợ transaction"""
    conn = get_conn()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if fetch:
            result = cursor.fetchall()
            if commit:
                conn.commit()
            return result if result else []
        else:
            if commit:
                conn.commit()
            return cursor.rowcount
    except Exception as e:
        if commit:  # Chỉ rollback nếu đang commit
            conn.rollback()
        messagebox.showerror("Lỗi CSDL", str(e))
        return []
    finally:
        cursor.close()
        conn.close()


def execute_transaction(queries):
    """Thực thi nhiều query trong một transaction"""
    conn = get_conn()
    cursor = conn.cursor()
    try:
        # Tắt autocommit để bắt đầu transaction
        conn.autocommit = False

        results = []
        for query, params in queries:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Nếu là SELECT, lấy kết quả
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                results.append(result if result else [])
            else:
                results.append(cursor.rowcount)

        # Commit transaction
        conn.commit()
        return results

    except Exception as e:
        # Rollback nếu có lỗi
        conn.rollback()
        messagebox.showerror("Lỗi Transaction", str(e))
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
