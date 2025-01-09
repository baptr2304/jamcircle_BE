"""
This module defines the database models for NguoiDung and MaLamMoi entities.
It includes definitions for attributes, relationships,
and methods to interact with nguoi_dung accounts and their associated refresh tokens.
"""

from uuid import uuid4
import datetime as _dt

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from models.base import Base


class NguoiDung(Base):
    """
    NguoiDung model representing the nguoi_dungs in the system.

    Attributes:
        id (UUID): The unique identifier for the nguoi_dung.
        ten_nguoi_dung (String): The name of the nguoi_dung.
        email (String): The email address of the nguoi_dung.
        mat_khau_ma_hoa (String): The hashed password of the nguoi_dung.
        quyen (String): The role of the nguoi_dung (default: "nguoi_dung").
        anh_dai_dien (String): The URL of the nguoi_dung's profile picture.
        trang_thai (String): The status of the nguoi_dung (default: "hoat_dong").
        thoi_gian_tao (DateTime): The timestamp when the nguoi_dung was created.
        thoi_gian_cap_nhat (DateTime): The timestamp when the nguoi_dung was last updated.
        thoi_gian_xoa (DateTime): The timestamp when the nguoi_dung was deleted.

    Relationships:
        ma_lam_mois: The list of refresh tokens issued to the nguoi_dung.
        bai_hats: The songs uploaded by the nguoi_dung.
        danh_sach_phats: The playlists created by the nguoi_dung.
        yeu_cau_tham_gia_phongs: The requests to join playlists.
        thanh_vien_phongs: The playlists the nguoi_dung is a member of.
    """

    __tablename__ = "nguoi_dung"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    ten_nguoi_dung = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    gioi_tinh = Column(String, nullable=True)
    ngay_sinh = Column(DateTime, nullable=True)
    mat_khau_ma_hoa = Column(String)
    quyen = Column(String, default="nguoi_dung")
    anh_dai_dien = Column(String, nullable=True)
    trang_thai = Column(String, default="hoat_dong")
    thoi_gian_tao = Column(DateTime, default=_dt.datetime.now())
    thoi_gian_cap_nhat = Column(DateTime, default=_dt.datetime.now())
    thoi_gian_xoa = Column(DateTime, nullable=True)

    ma_lam_mois = relationship("MaLamMoi", back_populates="nguoi_dung")
    bai_hats = relationship("BaiHat", back_populates="nguoi_dung")
    danh_sach_phats = relationship("DanhSachPhat", back_populates="nguoi_dung")
    yeu_cau_tham_gia_phongs = relationship(
        "YeuCauThamGiaPhong", back_populates="nguoi_dung"
    )
    thanh_vien_phongs = relationship("ThanhVienPhong", back_populates="nguoi_dung")


class MaLamMoi(Base):
    """
    MaLamMoi model for managing nguoi_dung sessions with refresh tokens.

    Attributes:
        id (UUID): The unique identifier for the refresh token.
        token (String): The refresh token, which must be unique.
        thoi_gian_het_han (DateTime): The timestamp when the token expires.
        thoi_gian_tao (DateTime): The timestamp when the token was created.
        thoi_gian_thu_hoi (DateTime): The timestamp when the token was revoked, if applicable.
        nguoi_dung_id (UUID): The ID of the nguoi_dung associated with this token.
        da_thu_hoi (Boolean): Flag indicating if the token has been revoked.

    Relationships:
        nguoi_dung: The nguoi_dung to whom the refresh token is associated.

    Properties:
        da_het_han (bool): Indicates if the token has expired.
        con_hieu_luc (bool): Indicates if the token is still valid (not expired or revoked).
    """

    __tablename__ = "ma_lam_moi"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    ma = Column(String, unique=True, index=True, nullable=False)
    thoi_gian_het_han = Column(DateTime, nullable=False)
    thoi_gian_tao = Column(DateTime, default=_dt.datetime.now())
    thoi_gian_thu_hoi = Column(DateTime, nullable=True)
    da_thu_hoi = Column(Boolean, default=False)
    nguoi_dung_id = Column(
        UUID(as_uuid=True),
        ForeignKey("nguoi_dung.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationship
    nguoi_dung = relationship("NguoiDung", back_populates="ma_lam_mois")

    @property
    def da_het_han(self) -> bool:
        """Check if the refresh token has expired."""
        result = False
        if self.thoi_gian_het_han is None:
            return result
        try:
            result = _dt.datetime.now() > self.thoi_gian_het_han
            return result
        except Exception as e:
            print(e)
            return result

    @property
    def con_hieu_luc(self) -> bool:
        """Check if the refresh token is still valid (not expired and not revoked)."""
        return not self.da_het_han and not self.da_thu_hoi
