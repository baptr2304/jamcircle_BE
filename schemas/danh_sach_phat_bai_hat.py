# id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
#     so_thu_tu = Column(Integer, nullable=False)
#     thoi_gian_tao = Column(DateTime, default=_dt.datetime.now())
#     thoi_gian_cap_nhat = Column(DateTime, default=_dt.datetime.now())
#     thoi_gian_xoa = Column(DateTime)
#     bai_hat_id = Column(UUID(as_uuid=True), ForeignKey("bai_hat.id"))
#     danh_sach_phat_id = Column(UUID(as_uuid=True), ForeignKey("danh_sach_phat.id"))


"""
This module defines the Pydantic schemas for managing DanhSachPhatBaiHat entities.
It includes schemas for creating, updating, and outputting DanhSachPhatBaiHat information.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, UUID4, Field


class DanhSachPhatBaiHatBase(BaseModel):
    """
        Base schema for DanhSachPhatBaiHat. It includes fields shared across different danh_sach_phat_bai_hat-related schemas.
    """
    
    so_thu_tu: int
    bai_hat_id: UUID4
    danh_sach_phat_id: UUID4
    
    
class DanhSachPhatBaiHatCreate(DanhSachPhatBaiHatBase):
    """
        Schema for creating a new DanhSachPhatBaiHat.
    """
    
    thoi_gian_tao: Optional[datetime] = datetime.now()
    pass


class DanhSachPhatBaiHatOut(DanhSachPhatBaiHatBase):
    """
        Schema for outputting DanhSachPhatBaiHat information.
    """
    
    id: UUID4
    thoi_gian_tao: datetime
    thoi_gian_cap_nhat: datetime
    thoi_gian_xoa: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        
        
class DanhSachPhatBaiHatUpdateDB(BaseModel):
    """
        Schema for updating DanhSachPhatBaiHat information in the database.
    """
    
    so_thu_tu: Optional[int] = None
    thoi_gian_cap_nhat: Optional[datetime] = datetime.now()
    thoi_gian_xoa: Optional[datetime] = None
    bai_hat_id: Optional[UUID4] = None
    danh_sach_phat_id: Optional[UUID4] = None
    pass


    
    