from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, UUID4, Field

class ThanhVienPhongBase(BaseModel):
    """
    Base schema for ThanhVienPhong. It includes fields shared across different thanh_vien_phong-related schemas.

    Attributes:
        id_phong (UUID4): The unique identifier of the phong.
        id_nguoi_dung (UUID4): The unique identifier of the nguoi_dung.
        trang_thai (Optional[str]): The current trang_thai of the thanh_vien_phong, defaults to "active".
    """

    id: UUID4
    trang_thai: Optional[str] = "HoatDong"
    quyen: Optional[str] = "ThanhVien"
    nguoi_dung_id: UUID4
    phong_nghe_nhac_id: UUID4
    

class ThanhVienPhongCreate(BaseModel):
    """
    Schema for creating a new ThanhVienPhong.

    Attributes:
        id_phong (UUID4): The unique identifier of the phong.
        id_nguoi_dung (UUID4): The unique identifier of the nguoi_dung.
        trang_thai (Optional[str]): The current trang_thai of the thanh_vien_phong, defaults to "active".
    """

    trang_thai: Optional[str] = "HoatDong"
    quyen: Optional[str] = "ThanhVien"
    nguoi_dung_id: UUID4
    phong_nghe_nhac_id: UUID4
    thoi_gian_tao: Optional[datetime] = datetime.now()
    
    
class ThanhVienPhongOut(ThanhVienPhongBase):
    """
    Schema for outputting ThanhVienPhong information.

    Attributes:
        thoi_gian_tao (datetime): The timestamp when the thanh_vien_phong account was created.
        thoi_gian_cap_nhat (datetime): The timestamp when the thanh_vien_phong account was last updated.
        thoi_gian_xoa (Optional[datetime]): The timestamp when the thanh_vien_phong account was deleted, if applicable.
    """

    thoi_gian_tao: datetime
    thoi_gian_cap_nhat: datetime
    thoi_gian_xoa: Optional[datetime] = None

    class Config(object):
        """
        Config class for ThanhVienPhongOut schema.
        """
        from_attributes = True
        

class ThanhVienPhongInDB(BaseModel):
    """
    Schema for updating a ThanhVienPhong in the database.

    Attributes:
        trang_thai (Optional[str]): The current trang_thai of the thanh_vien_phong, defaults to "active".
    """

    trang_thai: Optional[str] = "HoatDong"
    quyen: Optional[str] = "ThanhVien"
    nguoi_dung_id: UUID4
    phong_nghe_nhac_id: UUID4
    pass


class ThanhVienPhongUpdateDB(BaseModel):
    """
    Schema for updating a ThanhVienPhong in the database.

    Attributes:
        trang_thai (Optional[str]): The current trang_thai of the thanh_vien_phong, defaults to "active".
    """

    trang_thai: Optional[str] = "HoatDong"
    quyen: Optional[str] = "ThanhVien"
    nguoi_dung_id: UUID4
    phong_nghe_nhac_id: UUID4
    thoi_gian_cap_nhat: Optional[datetime] = datetime.now()