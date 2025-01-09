"""
This module defines CRUD operations for the DanhSachPhatBaiHat model.
It utilizes the base CRUD functionality provided by CRUDBase to
create, update, and read DanhSachPhatBaiHat entities.
"""

from models.danh_sach_phat_bai_hat import DanhSachPhatBaiHat
from schemas.danh_sach_phat_bai_hat import DanhSachPhatBaiHatCreate, DanhSachPhatBaiHatUpdateDB
from services.crud.base import CRUDBase

CRUDDanhSachPhatBaiHat = CRUDBase[DanhSachPhatBaiHat, DanhSachPhatBaiHatCreate, DanhSachPhatBaiHatUpdateDB]
crud_danh_sach_phat_bai_hat = CRUDDanhSachPhatBaiHat(DanhSachPhatBaiHat)
