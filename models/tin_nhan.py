from uuid import uuid4
import datetime as _dt

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from models.base import Base


class TinNhan(Base):
    """
    TinNhan model representing fines related to specific songs.

    Attributes:
        id (UUID): The unique identifier for the song fine record.
        noi_dung (String): The content of the message.
        tin_nhan_tra_loi_id (UUID): The ID of the message to which this message is a reply.
        thoi_gian_tao (DateTime): The timestamp when the message was created.
        thoi_gian_cap_nhat (DateTime): The timestamp when the message was last updated.
        thoi_gian_xoa (DateTime): The timestamp when the message was deleted.
        thanh_vien_phong_id (UUID): The ID of the user who created the message.
        phong_nghe_nhac_id (UUID): The ID of the playlist associated with this message.

    Relationships:
        phong_nghe_nhac: The playlist associated with this message.
        thanh_vien_phong: The user who created the message.
    """

    __tablename__ = "tin_nhan"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    noi_dung = Column(String, nullable=False)
    tin_nhan_tra_loi_id = Column(UUID(as_uuid=True), ForeignKey("tin_nhan.id"))
    thoi_gian_tao = Column(DateTime, default=_dt.datetime.now())
    thoi_gian_cap_nhat = Column(DateTime, default=_dt.datetime.now())
    thoi_gian_xoa = Column(DateTime)
    thanh_vien_phong_id = Column(UUID(as_uuid=True), ForeignKey("thanh_vien_phong.id"))
    phong_nghe_nhac_id = Column(UUID(as_uuid=True), ForeignKey("phong_nghe_nhac.id"))

    phong_nghe_nhac = relationship("PhongNgheNhac", back_populates="tin_nhans")
    thanh_vien_phong = relationship("ThanhVienPhong", back_populates="tin_nhans")
