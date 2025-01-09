"""
This module defines the Pydantic schemas for managing NguoiDung entities.
It includes schemas for creating, updating, and outputting NguoiDung information.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, UUID4, Field


class NguoiDungBase(BaseModel):
    """
    Base schema for NguoiDung. It includes fields shared across different nguoi_dung-related schemas.

    Attributes:
        email (EmailStr): The nguoi_dung's email address.
        trang_thai (Optional[str]): The current trang_thai of the nguoi_dung, defaults to "active".
    """

    ten_nguoi_dung: str
    email: EmailStr
    mat_khau: str
    quyen: Optional[str] = "nguoi_dung"
    anh_dai_dien: Optional[str] = None
    trang_thai: Optional[str] = "active"


class NguoiDungCreate(BaseModel):
    """
    Schema for creating a new NguoiDung.

    Attributes:
        email (EmailStr): The nguoi_dung's email address.
        mat_khau (str): The nguoi_dung's mat_khau.
        trang_thai (Optional[str]): The current trang_thai of the nguoi_dung, defaults to "active".
    """

    ten_nguoi_dung: str
    email: EmailStr
    gioi_tinh: Optional[str] = None
    ngay_sinh: Optional[datetime] = None
    mat_khau: str
    quyen: Optional[str] = "nguoi_dung"
    anh_dai_dien: Optional[str] = None
    trang_thai: Optional[str] = "active"
    thoi_gian_tao: datetime = Field(default_factory=datetime.now)


class NguoiDungOut(NguoiDungBase):
    """
    Schema for outputting NguoiDung information.

    Attributes:
        id (UUID4): The unique identifier of the nguoi_dung.
        thoi_gian_tao (datetime): The timestamp when the nguoi_dung account was created.
        thoi_gian_cap_nhat (datetime): The timestamp when the nguoi_dung account was last updated.
        thoi_gian_xoa (Optional[datetime]): The timestamp when the nguoi_dung account was deleted, if applicable.
    """

    id: UUID4
    thoi_gian_tao: datetime
    thoi_gian_cap_nhat: datetime
    thoi_gian_xoa: Optional[datetime] = None

    class Config(object):
        """
        Pydantic configuration for FaceDirectionLogOut schema
        """

        from_attributes = True


class NguoiDungInDB(NguoiDungBase):
    """
    Schema for representing a NguoiDung as stored in the database.

    Attributes:
        mat_khau (str): The hashed mat_khau of the nguoi_dung.
    """

    mat_khau: str


class NguoiDungUpdateDB(BaseModel):
    """
    Schema for updating NguoiDung information in the database.

    Attributes:
        email (Optional[EmailStr]): The updated email address of the nguoi_dung.
        mat_khau (Optional[str]): The updated mat_khau for the nguoi_dung.
        trang_thai (Optional[str]): The updated trang_thai of the nguoi_dung.
        thoi_gian_cap_nhat (Optional[datetime]): The timestamp of when the nguoi_dung was last updated, defaults to current time.
    """

    ten_nguoi_dung: Optional[str] = None
    email: Optional[EmailStr] = None
    gioi_tinh: Optional[str] = None
    ngay_sinh: Optional[datetime] = None
    mat_khau: Optional[str] = None
    quyen: Optional[str] = None
    anh_dai_dien: Optional[str] = None
    trang_thai: Optional[str] = None
    thoi_gian_cap_nhat: Optional[datetime] = Field(default_factory=datetime.now)
    
class DoiMatKhau(BaseModel):
    mat_khau_cu: str
    mat_khau_moi: str