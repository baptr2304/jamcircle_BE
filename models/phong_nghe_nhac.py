from uuid import uuid4
import datetime as _dt

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from models.base import Base


class PhongNgheNhac(Base):

    __tablename__ = "phong_nghe_nhac"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    ten_phong = Column(String, nullable=False)
    trang_thai_phat = Column(String)
    thoi_gian_hien_tai_bai_hat = Column(Integer, default=0)
    so_thu_tu_bai_hat_dang_phat = Column(Integer, default=0)
    thoi_gian_tao = Column(DateTime, default=_dt.datetime.now())
    thoi_gian_cap_nhat = Column(DateTime, default=_dt.datetime.now())
    danh_sach_phat_id = Column(UUID(as_uuid=True), ForeignKey("danh_sach_phat.id"))

    danh_sach_phat = relationship("DanhSachPhat", back_populates="phong_nghe_nhacs")
    thanh_vien_phongs = relationship("ThanhVienPhong", back_populates="phong_nghe_nhac")
    tin_nhans = relationship("TinNhan", back_populates="phong_nghe_nhac")
    yeu_cau_tham_gia_phongs = relationship(
        "YeuCauThamGiaPhong", back_populates="phong_nghe_nhac"
    )
