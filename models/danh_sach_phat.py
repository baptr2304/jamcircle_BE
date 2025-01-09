from uuid import uuid4
import datetime as _dt

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from models.base import Base


class DanhSachPhat(Base):
    """
    DanhSachPhat model representing fines related to specific songs.

    Attributes:
        id (UUID): The unique identifier for the song fine record.
        ten_danh_sach_phat (String): The name of the playlist.
        loai (String): The type of the playlist (default: "yeu_thich").
        anh (String): The image of the playlist.
        thoi_gian_ra_mat (DateTime): The release date of the playlist.
        thoi_gian_tao (DateTime): The timestamp when the playlist was created.
        thoi_gian_cap_nhat (DateTime): The timestamp when the playlist was last updated.
        thoi_gian_xoa (DateTime): The timestamp when the playlist was deleted.
        nguoi_dung_id (UUID): The ID of the user who created the playlist.

    Relationships:
        danh_sach_phat_bai_hats: The songs in the playlist.
        nguoi_dung: The songs in the playlist.
        phong_nghe_nhacs: The songs in the playlist.
    """

    __tablename__ = "danh_sach_phat"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    ten_danh_sach_phat = Column(String, nullable=False)
    loai = Column(String, default="yeu_thich")
    anh = Column(String)
    thoi_gian_ra_mat = Column(DateTime)
    thoi_gian_tao = Column(DateTime, default=_dt.datetime.now())
    thoi_gian_cap_nhat = Column(DateTime, default=_dt.datetime.now())
    thoi_gian_xoa = Column(DateTime)
    nguoi_dung_id = Column(UUID(as_uuid=True), ForeignKey("nguoi_dung.id"), nullable=True)

    danh_sach_phat_bai_hats = relationship(
        "DanhSachPhatBaiHat", back_populates="danh_sach_phat"
    )
    nguoi_dung = relationship("NguoiDung", back_populates="danh_sach_phats")
    phong_nghe_nhacs = relationship("PhongNgheNhac", back_populates="danh_sach_phat")
