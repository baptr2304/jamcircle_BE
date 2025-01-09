from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, UUID4, Field

class PhongNgheNhacBase(BaseModel):
    id: UUID4
    ten_phong: str
    trang_thai_phat: Optional[str] = "dang_phat"
    thoi_gian_hien_tai_bai_hat: Optional[int] = 0
    so_thu_tu_bai_hat_dang_phat: Optional[int] = 0
    danh_sach_phat_id: UUID4
    
    
class PhongNgheNhacCreate(BaseModel):
    ten_phong: str
    thoi_gian_tao: Optional[datetime] = datetime.now()
    danh_sach_phat_id: Optional[UUID4] = None
    
    
class PhongNgheNhacOut(PhongNgheNhacBase):
    thoi_gian_tao: datetime
    thoi_gian_cap_nhat: datetime
    class Config(object):
        from_attributes = True
        
        
class PhongNgheNhacInDB(PhongNgheNhacOut):
    pass


class PhongNgheNhacUpdateDB(BaseModel):
    ten_phong: Optional[str] = None
    trang_thai_phat: Optional[str] = None
    thoi_gian_hien_tai_bai_hat: Optional[int] = None
    so_thu_tu_bai_hat_dang_phat: Optional[int] = None
    thoi_gian_cap_nhat: Optional[datetime] = Field(default_factory=datetime.now)
    
    