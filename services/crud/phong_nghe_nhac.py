from models.phong_nghe_nhac import PhongNgheNhac
from schemas.phong_nghe_nhac import PhongNgheNhacCreate, PhongNgheNhacUpdateDB
from services.crud.base import CRUDBase

CRUDPhongNgheNhac = CRUDBase[PhongNgheNhac, PhongNgheNhacCreate, PhongNgheNhacUpdateDB]
crud_phong_nghe_nhac = CRUDPhongNgheNhac(PhongNgheNhac)
