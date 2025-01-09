"""
This module defines CRUD operations for the MaLamMoi model.
It utilizes the base CRUD functionality provided by CRUDBase to
create, update, and read MaLamMoi entities.
"""

from models.nguoi_dung import MaLamMoi
from schemas.ma_lam_moi import MaLamMoiCreate, MaLamMoiUpdateDB
from services.crud.base import CRUDBase

CRUDMaLamMoi = CRUDBase[MaLamMoi, MaLamMoiCreate, MaLamMoiUpdateDB]
crud_ma_lam_moi = CRUDMaLamMoi(MaLamMoi)
