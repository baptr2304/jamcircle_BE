    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    # ten_danh_sach_phat = Column(String, nullable=False)
    # loai = Column(String, default="yeu_thich")
    # anh = Column(String)
    # thoi_gian_ra_mat = Column(DateTime)
    # thoi_gian_tao = Column(DateTime, default=_dt.datetime.now())
    # thoi_gian_cap_nhat = Column(DateTime, default=_dt.datetime.now())
    # nguoi_dung_id = Column(UUID(as_uuid=True), ForeignKey("nguoi_dung.id"))
    
"""
This module defines the Pydantic schemas for managing DanhSachPhat entities.
It includes schemas for creating, updating, and outputting DanhSachPhat information.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, UUID4, Field


class DanhSachPhatBase(BaseModel):
    """
    Base schema for DanhSachPhat. It includes fields shared across different danh_sach_phat-related schemas.
    """
    
    ten_danh_sach_phat: str
    loai: Optional[str] = "yeu_thich"
    anh: Optional[str] = None
    thoi_gian_ra_mat: Optional[datetime] = None
    nguoi_dung_id: UUID4 = None
    

class DanhSachPhatCreate(BaseModel):
    """
    Schema for creating a new DanhSachPhat.
    """
    ten_danh_sach_phat: str
    loai: Optional[str] = "yeu_thich"
    anh: Optional[str] = None
    thoi_gian_ra_mat: Optional[datetime] = None
    thoi_gian_tao: Optional[datetime] = datetime.now()
    nguoi_dung_id: UUID4 = None
    pass


class DanhSachPhatOut(DanhSachPhatBase):
    """
    Schema for outputting DanhSachPhat information.
    """
    
    id: UUID4
    thoi_gian_tao: datetime
    thoi_gian_cap_nhat: datetime
    thoi_gian_xoa: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        
        
class DanhSachPhatUpdateDB(BaseModel):
    """
    Schema for updating DanhSachPhat information in the database.
    """
    
    ten_danh_sach_phat: Optional[str] = None
    loai: Optional[str] = None
    anh: Optional[str] = None
    thoi_gian_ra_mat: Optional[datetime] = None
    thoi_gian_cap_nhat: Optional[datetime] = datetime.now()
    thoi_gian_xoa: Optional[datetime] = None
    nguoi_dung_id: Optional[UUID4] = None
    pass

