# utils.py
from datetime import datetime, timedelta
from database import execute_query

def kiem_tra_trung_lich(ma_bs, ma_phong, ngay_gio, ma_lich_hien_tai=None):
    try:
        dt = datetime.strptime(ngay_gio, "%Y-%m-%d %H:%M")
        if dt < datetime.now():
            return False, "Không thể đặt lịch trong quá khứ!"
        start_time = dt
        end_time = dt + timedelta(minutes=30)

        query_bs = """
            SELECT COUNT(*) FROM LichKham
            WHERE MaBacSi = ?
            AND TrangThai != N'Đã hủy'
            AND NgayGioKham BETWEEN ? AND ?
        """
        if ma_lich_hien_tai:
            query_bs += " AND MaLichKham != ?"
            result_bs = execute_query(query_bs, (ma_bs, start_time, end_time, ma_lich_hien_tai), fetch=True)
        else:
            result_bs = execute_query(query_bs, (ma_bs, start_time, end_time), fetch=True)

        if result_bs and result_bs[0][0] > 0:
            return False, f"Bác sĩ đã có lịch khám vào thời gian này!\nVui lòng chọn thời gian khác."

        query_phong = """
            SELECT COUNT(*) FROM LichKham
            WHERE MaPhong = ?
            AND TrangThai != N'Đã hủy'
            AND NgayGioKham BETWEEN ? AND ?
        """
        if ma_lich_hien_tai:
            query_phong += " AND MaLichKham != ?"
            result_phong = execute_query(query_phong, (ma_phong, start_time, end_time, ma_lich_hien_tai), fetch=True)
        else:
            result_phong = execute_query(query_phong, (ma_phong, start_time, end_time), fetch=True)

        if result_phong and result_phong[0][0] > 0:
            return False, f"Phòng khám đã có bệnh nhân vào thời gian này!\nVui lòng chọn phòng hoặc thời gian khác."

        date_str = dt.strftime("%Y-%m-%d")
        query_count = """
            SELECT COUNT(*) FROM LichKham
            WHERE MaBacSi = ?
            AND TrangThai != N'Đã hủy'
            AND CAST(NgayGioKham AS DATE) = ?
        """
        result_count = execute_query(query_count, (ma_bs, date_str), fetch=True)
        if result_count and result_count[0][0] >= 18:
            return False, f"Bác sĩ đã đủ 18 ca khám trong ngày {date_str}!\nVui lòng chọn ngày khác."

        query_count_phong = """
            SELECT COUNT(*) FROM LichKham
            WHERE MaPhong = ?
            AND TrangThai != N'Đã hủy'
            AND CAST(NgayGioKham AS DATE) = ?
        """
        result_count_phong = execute_query(query_count_phong, (ma_phong, date_str), fetch=True)
        if result_count_phong and result_count_phong[0][0] >= 18:
            return False, f"Phòng khám đã đủ 18 ca trong ngày {date_str}!\nVui lòng chọn phòng khác."

        return True, "OK"
    except ValueError:
        return False, "Định dạng ngày giờ không đúng! Vui lòng nhập theo format: YYYY-MM-DD HH:MM"
    except Exception as e:
        return False, f"Lỗi kiểm tra: {str(e)}"