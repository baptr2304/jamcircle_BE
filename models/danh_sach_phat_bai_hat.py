from uuid import uuid4
import datetime as _dt

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from models.base import Base


class DanhSachPhatBaiHat(Base):
    """
    DanhSachPhatBaiHat model representing fines related to specific songs.

    Attributes:
        id (UUID): The unique identifier for the song fine record.
        so_thu_tu (Integer): The order of the song in the playlist.
        thoi_gian_tao (DateTime): The timestamp when the fine record was created.
        thoi_gian_cap_nhat (DateTime): The timestamp when the fine record was last updated.
        thoi_gian_xoa (DateTime): The timestamp when the fine record was deleted.
        bai_hat_id (UUID): The ID of the song associated with this fine record.
        danh_sach_phat_id (UUID): The ID of the playlist associated with this fine record.

    Relationships:
        bai_hat: The song associated with this fine record.
        danh_sach_phat: The playlist associated with this fine record.
    """

    __tablename__ = "danh_sach_phat_bai_hat"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    so_thu_tu = Column(Integer, nullable=False)
    thoi_gian_tao = Column(DateTime, default=_dt.datetime.now())
    thoi_gian_cap_nhat = Column(DateTime, default=_dt.datetime.now())
    thoi_gian_xoa = Column(DateTime)
    bai_hat_id = Column(UUID(as_uuid=True), ForeignKey("bai_hat.id"))
    danh_sach_phat_id = Column(UUID(as_uuid=True), ForeignKey("danh_sach_phat.id"))

    bai_hat = relationship("BaiHat", back_populates="danh_sach_phat_bai_hats")
    danh_sach_phat = relationship(
        "DanhSachPhat", back_populates="danh_sach_phat_bai_hats"
    )
