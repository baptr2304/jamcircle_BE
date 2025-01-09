from models.thanh_vien_phong import ThanhVienPhong
from schemas.thanh_vien_phong import ThanhVienPhongCreate, ThanhVienPhongUpdateDB
from services.crud.base import CRUDBase

CRUDThanhVienPhong = CRUDBase[ThanhVienPhong, ThanhVienPhongCreate, ThanhVienPhongUpdateDB]
crud_thanh_vien_phong = CRUDThanhVienPhong(ThanhVienPhong)
