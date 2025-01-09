"""
This module defines CRUD operations for the BaiHat model.
It utilizes the base CRUD functionality provided by CRUDBase to
create, update, and read BaiHat entities.
"""

from models.bai_hat import BaiHat
from schemas.bai_hat import BaiHatCreate, BaiHatUpdateDB
from services.crud.base import CRUDBase

CRUDBaiHat = CRUDBase[BaiHat, BaiHatCreate, BaiHatUpdateDB]
crud_bai_hat = CRUDBaiHat(BaiHat)
