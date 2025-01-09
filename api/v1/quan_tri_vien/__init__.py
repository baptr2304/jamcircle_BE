from fastapi import APIRouter
from api.v1.quan_tri_vien.nguoi_dung import router as nguoi_dung_router

router = APIRouter(prefix="/quan_tri_vien")

router.include_router(nguoi_dung_router)
