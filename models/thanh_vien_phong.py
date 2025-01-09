from uuid import uuid4
import datetime as _dt

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from models.base import Base


class ThanhVienPhong(Base):
    """
    ThanhVienPhong model representing fines related to specific songs.

    Attributes:
        id (UUID): The unique identifier for the song fine record.
        trang_thai (String): The type of the playlist (default: "HoatDong").
        quyen (String): The type of the playlist (default: "ThanhVien").
        thoi_gian_tao (DateTime): The timestamp when the playlist was created.
        thoi_gian_cap_nhat (DateTime): The timestamp when the playlist was last updated.
        nguoi_dung_id (UUID): The ID of the user who created the playlist.
        phong_nghe_nhac_id (UUID): The ID of the user who created the playlist.

    Relationships:
        nguoi_dung: n
        phong_nghe_nhac: The songs in the playlist.
        tin_nhans: The songs in the playlist.
    """

    __tablename__ = "thanh_vien_phong"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    trang_thai = Column(String, default="HoatDong")
    quyen = Column(String, default="ThanhVien")
    thoi_gian_tao = Column(DateTime, default=_dt.datetime.now())
    thoi_gian_cap_nhat = Column(DateTime, default=_dt.datetime.now())
    nguoi_dung_id = Column(UUID(as_uuid=True), ForeignKey("nguoi_dung.id"))
    phong_nghe_nhac_id = Column(UUID(as_uuid=True), ForeignKey("phong_nghe_nhac.id"))

    nguoi_dung = relationship("NguoiDung", back_populates="thanh_vien_phongs")
    phong_nghe_nhac = relationship("PhongNgheNhac", back_populates="thanh_vien_phongs")
    tin_nhans = relationship("TinNhan", back_populates="thanh_vien_phong")
