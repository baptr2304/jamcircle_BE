"""
This module defines CRUD operations for the DanhSachPhat model.
It utilizes the base CRUD functionality provided by CRUDBase to
create, update, and read DanhSachPhat entities.
"""

from models.danh_sach_phat import DanhSachPhat
from schemas.danh_sach_phat import DanhSachPhatCreate, DanhSachPhatUpdateDB
from services.crud.base import CRUDBase

CRUDDanhSachPhat = CRUDBase[DanhSachPhat, DanhSachPhatCreate, DanhSachPhatUpdateDB]
crud_danh_sach_phat = CRUDDanhSachPhat(DanhSachPhat)
