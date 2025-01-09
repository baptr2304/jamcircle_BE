from models.tin_nhan import TinNhan
from schemas.tin_nhan import TinNhanCreate, TinNhanUpdateDB
from services.crud.base import CRUDBase

CRUDTinNhan = CRUDBase[TinNhan, TinNhanCreate, TinNhanUpdateDB]
crud_tin_nhan = CRUDTinNhan(TinNhan)
