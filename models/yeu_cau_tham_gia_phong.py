from uuid import uuid4
import datetime as _dt

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from models.base import Base


class YeuCauThamGiaPhong(Base):
    """
    YeuCauThamGiaPhong model representing fines related to specific songs.

    Attributes:
        id (UUID): The unique identifier for the song fine record.
        trang_thai (String): The type of the playlist (default: "cho_duyet").
        thoi_gian_tao (DateTime): The timestamp when the playlist was created.
        thoi_gian_cap_nhat (DateTime): The timestamp when the playlist was last updated.
        nguoi_dung_id (UUID): The ID of the user who created the playlist.
        phong_nghe_nhac_id (UUID): The ID of the user who created the playlist.

    Relationships:
        nguoi_dung: The songs in the playlist.
        phong_nghe_nhac: The songs in the playlist.
    """

    __tablename__ = "yeu_cau_tham_gia_phong"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    trang_thai = Column(String, default="cho_duyet")
    thoi_gian_tao = Column(DateTime, default=_dt.datetime.now())
    thoi_gian_cap_nhat = Column(DateTime, default=_dt.datetime.now())
    nguoi_dung_id = Column(UUID(as_uuid=True), ForeignKey("nguoi_dung.id"))
    phong_nghe_nhac_id = Column(UUID(as_uuid=True), ForeignKey("phong_nghe_nhac.id"))

    nguoi_dung = relationship("NguoiDung", back_populates="yeu_cau_tham_gia_phongs")
    phong_nghe_nhac = relationship(
        "PhongNgheNhac", back_populates="yeu_cau_tham_gia_phongs"
    )
