from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.auth import DangNhapSchema, DangKySchema
from schemas.ma_xac_thuc import ThongTinMaSchema
from schemas.ma_lam_moi import MaLamMoiSchema
from api.deps import get_session, get_thong_tin_ma
from services.auth.security import (
    dang_nhap_service,
    dang_ky_service,
    lam_moi_ma_xac_thuc_service,
    dang_xuat_service,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/dang_ky")
async def dang_ky(
    dang_ky_schema: DangKySchema, session: AsyncSession = Depends(get_session)
):
    """
    Endpoint to create a new nguoi_dung account.
    """
    return await dang_ky_service(session, dang_ky_schema)


@router.post("/dang_nhap")
async def dang_nhap(
    dang_nhap_schema: DangNhapSchema, session: AsyncSession = Depends(get_session)
):
    """
    Endpoint to authenticate a nguoi_dung and generate an access token.
    """
    return await dang_nhap_service(session, dang_nhap_schema)


@router.post("/dang_xuat")
async def dang_xuat(
    thong_tin_ma: ThongTinMaSchema = Depends(get_thong_tin_ma),
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to dang_xuat a nguoi_dung by revoking all active lam_moi tokens.
    """
    return await dang_xuat_service(session, thong_tin_ma.nguoi_dung_id)


@router.post("/lam_moi_ma_xac_thuc")
async def lam_moi_ma_xac_thuc(
    ma_lam_moi_schema: MaLamMoiSchema, session: AsyncSession = Depends(get_session)
):
    """
    Endpoint to lam_moi the access token using a lam_moi token.
    """
    return await lam_moi_ma_xac_thuc_service(session, ma_lam_moi_schema)
