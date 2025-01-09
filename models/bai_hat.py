from uuid import uuid4
import datetime as _dt

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from models.base import Base


class BaiHat(Base):
    """
    BaiHat model representing songs in the system.

    Attributes:
        id (UUID): The unique identifier for the song.
        ten_bai_hat (String): The name of the song.
        anh (String): The URL of the song's cover image.
        ten_ca_si (String): The name of the artist.
        the_loai (String): The genre of the song.
        mo_ta (String): A brief description or lyrics snippet of the song.
        loi_bai_hat (Text): The full lyrics of the song.
        thoi_luong (Integer): The length of the song in seconds.
        lien_ket (String): The URL of the song.
        trang_thai (String): The status of the song (default: "hoat_dong").
        quyen_rieng_tu (String): The privacy setting of the song (default: "cong_khai").
        thoi_gian_tao (DateTime): The timestamp when the song was created.
        thoi_gian_cap_nhat (DateTime): The timestamp when the song was last updated.
        thoi_gian_xoa (DateTime): The timestamp when the song was deleted.
        nguoi_dung_id (UUID): The ID of the user who created the song.
    Relationships:
        danh_sach_phat_bai_hats: The playlists containing this song.
        nguoi_dung: The user who created the song.
    """

    __tablename__ = "bai_hat"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    ten_bai_hat = Column(String, nullable=False)
    anh = Column(String, nullable=True)
    ten_ca_si = Column(String, nullable=True)
    the_loai = Column(String, nullable=True)
    mo_ta = Column(String, nullable=True)
    loi_bai_hat = Column(Text, nullable=True)
    thoi_luong = Column(Integer, nullable=True)
    lien_ket = Column(String, nullable=True)
    trang_thai = Column(String, default="hoat_dong")
    quyen_rieng_tu = Column(String, default="cong_khai")
    thoi_gian_tao = Column(DateTime, default=_dt.datetime.now())
    thoi_gian_cap_nhat = Column(DateTime, default=_dt.datetime.now(), nullable=True)
    thoi_gian_xoa = Column(DateTime, nullable=True)

    nguoi_dung_id = Column(UUID(as_uuid=True), ForeignKey("nguoi_dung.id"), nullable=True)

    # Define the relationship with DanhSachPhatBaiHat
    danh_sach_phat_bai_hats = relationship(
        "DanhSachPhatBaiHat", back_populates="bai_hat"
    )

    # Define the relationship with NguoiDung through DanhSachPhatBaiHat
    nguoi_dung = relationship("NguoiDung", back_populates="bai_hats")
