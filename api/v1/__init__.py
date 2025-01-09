"""
This module defines the API version 1 router and includes all the necessary routers for version 1 endpoints.
"""

from fastapi import APIRouter
from api.v1.quan_tri_vien import router as quan_tri_vien_router
from api.v1.auth import router as auth_router
from api.v1.nguoi_dung import router as nguoi_dung_router
from api.v1.bai_hat import router as bai_hat_router
from api.v1.danh_sach_phat import router as danh_sach_phat_router
from api.v1.phong_nghe_nhac import router as phong_nghe_nhac_router
from api.v1.common_service import router as common_service_router
from api.v1.websocket import router as websocket_router
from api.v1.tin_nhan import router as tin_nhan_router


router = APIRouter(prefix="/v1")

# Include routers for different API sections
router.include_router(auth_router)
router.include_router(quan_tri_vien_router)
router.include_router(nguoi_dung_router)
router.include_router(bai_hat_router)
router.include_router(danh_sach_phat_router)
router.include_router(phong_nghe_nhac_router)
router.include_router(websocket_router)
router.include_router(common_service_router)
router.include_router(tin_nhan_router)
