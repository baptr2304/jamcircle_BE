"""
This module initializes all the database models used in the FastAPI application.

Importing this module ensures that all the models are properly registered and accessible.
It includes models such as NguoiDung, Room, Child, NapSession, NapSessionChild, and FaceDirectionLog.
"""

from models.bai_hat import BaiHat
from models.danh_sach_phat_bai_hat import DanhSachPhatBaiHat
from models.danh_sach_phat import DanhSachPhat
from models.nguoi_dung import NguoiDung, MaLamMoi
from models.phong_nghe_nhac import PhongNgheNhac
from models.thanh_vien_phong import ThanhVienPhong
from models.tin_nhan import TinNhan
from models.yeu_cau_tham_gia_phong import YeuCauThamGiaPhong
