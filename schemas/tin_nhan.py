from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, UUID4, Field


class TinNhanBase(BaseModel):
    """
    Base schema for TinNhan. It includes fields shared across different tin_nhan-related schemas.
    """
    
    noi_dung: str
    tin_nhan_tra_loi_id: Optional[UUID4] = None
    thanh_vien_phong_id: UUID4 = None
    phong_nghe_nhac_id: UUID4 = None
    
class TinNhanCreate(TinNhanBase):
    thoi_gian_tao: Optional[datetime] = datetime.now()
    pass

class TinNhanOut(TinNhanBase):
    """
    Schema for outputting TinNhan information.
    """
    
    id: UUID4
    thoi_gian_tao: datetime
    thoi_gian_cap_nhat: datetime
    thoi_gian_xoa: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        
class TinNhanInDB(BaseModel):
    """
    Schema for updating TinNhan information in the database.
    """
    
    noi_dung: Optional[str] = None
    tin_nhan_tra_loi_id: Optional[UUID4] = None
    thanh_vien_phong_id: Optional[UUID4] = None
    phong_nghe_nhac_id: Optional[UUID4] = None
    thoi_gian_cap_nhat: Optional[datetime] = datetime.now()
    thoi_gian_xoa: Optional[datetime] = None

class TinNhanUpdateDB(BaseModel):
    """
    Schema for updating TinNhan information in the database.
    """
    
    noi_dung: Optional[str] = None
    tin_nhan_tra_loi_id: Optional[UUID4] = None
    thanh_vien_phong_id: Optional[UUID4] = None
    phong_nghe_nhac_id: Optional[UUID4] = None
    thoi_gian_cap_nhat: Optional[datetime] = datetime.now()
    thoi_gian_xoa: Optional[datetime] = None
    pass