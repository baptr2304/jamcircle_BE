"""
This module defines the Pydantic schemas for authentication-related operations.
It includes schemas for nguoi_dung login, signup, and response after login.
"""

from pydantic import BaseModel, EmailStr, UUID4, Field
from typing import Optional
from datetime import datetime


class DangNhapSchema(BaseModel):
    """
    Schema for nguoi_dung login. It contains the nguoi_dung's email and mat_khau.

    Attributes:
        email (EmailStr): The nguoi_dung's email address.
        mat_khau (str): The nguoi_dung's mat_khau.
    """

    email: EmailStr
    mat_khau: str


class DangKySchema(BaseModel):
    """
    Schema for nguoi_dung signup. It contains the nguoi_dung's email and mat_khau.

    Attributes:
        email (EmailStr): The nguoi_dung's email address.
        mat_khau (str): The nguoi_dung's mat_khau.
    """

    ten_nguoi_dung: str
    email: EmailStr
    mat_khau: str
    gioi_tinh: Optional[str] = None
    ngay_sinh: Optional[datetime] = None
    anh_dai_dien: Optional[str] = None
    thoi_gian_tao: datetime = Field(default_factory=datetime.now)


class DangNhapResponse(BaseModel):
    """
    Schema for the response after a successful login.

    Attributes:
        access_token (str): The access token for the nguoi_dung.
        ma_lam_moi (str): The refresh token for the nguoi_dung.
        expires_at (int): The timestamp when the access token expires.
        token_type (str): The type of token (default: "bearer").
    """

    ma_xac_thuc: str
    ma_lam_moi: str
    loai_ma: str


class DangKyResponse(BaseModel):
    """
    Schema for the response after a successful signup.

    Attributes:
        phan_hoi (str): The response message after a successful signup.
    """

    id: UUID4
    ten_nguoi_dung: str
    email: EmailStr
    anh_dai_dien: Optional[str] = None
    gioi_tinh: Optional[str] = None
    ngay_sinh: Optional[datetime] = None
    quyen: Optional[str] = "nguoi_dung"
    trang_thai: Optional[str] = "hoat_dong"
    thoi_gian_tao: Optional[datetime] = None
    thoi_gian_cap_nhat: Optional[datetime] = None
    thoi_gian_xoa: Optional[datetime] = None
