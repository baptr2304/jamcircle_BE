# id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
#     ten_bai_hat = Column(String, nullable=False)
#     ten_ca_si = Column(String, nullable=False)
#     the_loai = Column(String, nullable=False)
#     mo_ta = Column(String, nullable=True)
#     loi_bai_hat = Column(Text, nullable=True)
#     thoi_luong = Column(Integer, nullable=False)
#     lien_ket = Column(String, nullable=False)
#     trang_thai = Column(String, default="hoat_dong")
#     quyen_rieng_tu = Column(String, default="cong_khai")
#     thoi_gian_tao = Column(DateTime, default=_dt.datetime.now())
#     thoi_gian_cap_nhat = Column(DateTime, default=_dt.datetime.now())
#     thoi_gian_xoa = Column(DateTime, nullable=True)
#     nguoi_dung_id = Column(UUID(as_uuid=True), ForeignKey("nguoi_dung.id"))

"""
This module defines the Pydantic schemas for managing BaiHat entities.
It includes schemas for creating, updating, and outputting BaiHat information.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, UUID4, Field


class BaiHatBase(BaseModel):
    """
    Base schema for BaiHat. It includes fields shared across different bai_hat-related schemas.
    """
    
    ten_bai_hat: str
    anh: Optional[str] = None
    ten_ca_si: str = None
    the_loai: str = None
    mo_ta: Optional[str] = None
    loi_bai_hat: Optional[str] = None
    thoi_luong: int = None
    lien_ket: str = None
    trang_thai: Optional[str] = "hoat_dong"
    quyen_rieng_tu: Optional[str] = "cong_khai"
    nguoi_dung_id: UUID4 = None
    

class BaiHatCreate(BaiHatBase):
    """
    Schema for creating a new BaiHat.
    """
    
    thoi_gian_tao: Optional[datetime] = datetime.now()
    pass


class BaiHatOut(BaiHatBase):
    """
    Schema for outputting BaiHat information.
    """
    
    id: UUID4
    thoi_gian_tao: datetime
    thoi_gian_cap_nhat: datetime
    thoi_gian_xoa: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        

class BaiHatUpdateDB(BaseModel):
    """
    Schema for updating a BaiHat in the database.
    """
    
    ten_bai_hat: Optional[str] = None
    anh: Optional[str] = None
    ten_ca_si: Optional[str] = None
    the_loai: Optional[str] = None
    mo_ta: Optional[str] = None
    loi_bai_hat: Optional[str] = None
    thoi_luong: Optional[int] = None
    lien_ket: Optional[str] = None
    trang_thai: Optional[str] = None
    quyen_rieng_tu: Optional[str] = None
    thoi_gian_cap_nhat: Optional[datetime] = datetime.now()
    nguoi_dung_id: Optional[UUID4] = None
    thoi_gian_xoa: Optional[datetime] = None
    pass