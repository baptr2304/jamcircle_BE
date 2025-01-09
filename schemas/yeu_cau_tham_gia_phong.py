from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, UUID4, Field

class YeuCauThamGiaPhongBase(BaseModel):
    id: UUID4
    trang_thai: Optional[str] = "cho_duyet"
    nguoi_dung_id: UUID4
    phong_nghe_nhac_id: UUID4
    
    
class YeuCauThamGiaPhongCreate(BaseModel):
    trang_thai: Optional[str] = "cho_duyet"
    nguoi_dung_id: UUID4
    phong_nghe_nhac_id: UUID4
    thoi_gian_tao: Optional[datetime] = datetime.now()
    
    
class YeuCauThamGiaPhongOut(YeuCauThamGiaPhongBase):
    thoi_gian_tao: datetime
    thoi_gian_cap_nhat: datetime
    class Config(object):
        from_attributes = True
        
        
class YeuCauThamGiaPhongInDB(YeuCauThamGiaPhongOut):
    """
    Schema for inputting YeuCauThamGiaPhong information to the database.
    """
    pass


class YeuCauThamGiaPhongUpdateDB(BaseModel):
    """
    Schema for updating a YeuCauThamGiaPhong in the database.

    Attributes:
        trang_thai (Optional[str]): The current trang_thai of the yeu_cau_tham_gia_phong, defaults to "cho_duyet".
    """

    trang_thai: Optional[str] = "cho_duyet"
    thoi_gian_cap_nhat: Optional[datetime] = Field(default_factory=datetime.now)
    pass