"""
This module handles authentication-related operations,
such as generating access and lam_moi mas,
signing up a new nguoi_dung, logging out, and lam_moiing mas.
"""

import logging
from datetime import datetime, timedelta

from jose import jwt, JWTError
from fastapi import status, HTTPException, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config.config import settings
from models.nguoi_dung import NguoiDung
from schemas.ma_lam_moi import MaLamMoiSchema, MaLamMoiCreate, MaLamMoiUpdateDB
from schemas.nguoi_dung import NguoiDungCreate
from schemas.auth import DangNhapSchema, DangKySchema, DangKyResponse, DangNhapResponse
from services.crud.nguoi_dung import crud_nguoi_dung
from services.crud.ma_lam_moi import crud_ma_lam_moi
from utils.security import ma_hoa_mat_khau, xac_thuc_mat_khau

# Constants
ALGORITHM = "HS256"
GENERIC_ERROR_MSG = "Something went wrong"
logger = logging.getLogger(__name__)


def tao_ma_xac_thuc(nguoi_dung: NguoiDung) -> str:
    """
    Create an access ma for a given nguoi_dung.
    """
    try:
        expire = datetime.now() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        return jwt.encode(
            {
                "nguoi_dung_id": str(nguoi_dung.id),
                "thoi_gian_het_han": expire.isoformat(),
            },
            key=settings.SECRET_KEY,
            algorithm=ALGORITHM,
        )
    except Exception as e:
        logger.error("Error while creating access ma: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create access ma",
        )


def tao_ma_lam_moi(nguoi_dung: NguoiDung) -> str:
    """
    Create a lam_moi ma for a given nguoi_dung.
    """
    try:
        expire = datetime.now() + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
        return jwt.encode(
            {
                "nguoi_dung_id": str(nguoi_dung.id),
                "thoi_gian_het_han": expire.isoformat(),
            },
            key=settings.SECRET_KEY,
            algorithm=ALGORITHM,
        )
    except Exception as e:
        logger.error("Error while creating lam_moi ma: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create lam_moi ma",
        )


async def vo_hieu_hoa_toan_bo_ma_lam_moi_bang_nguoi_dung_id(
    session: AsyncSession, nguoi_dung_id: str
) -> None:
    """
    Deactivate all lam_moi mas associated with a nguoi_dung.
    """
    try:
        ma_lam_mois_of_nguoi_dung = await crud_ma_lam_moi.get_multi(
            session, nguoi_dung_id=nguoi_dung_id
        )
        for rt in ma_lam_mois_of_nguoi_dung:
            if rt.con_hieu_luc:
                rt.da_thu_hoi = True
                rt.thoi_gian_thu_hoi = datetime.now()
                await crud_ma_lam_moi.update(
                    session, db_obj=rt, obj_in=MaLamMoiUpdateDB(**rt.dict())
                )
    except Exception as e:
        logger.error("Error while deactivating lam_moi mas: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate lam_moi mas",
        )


def giai_ma_ma(ma: str) -> dict:
    """
    Decode a JWT ma.
    """
    try:
        return jwt.decode(ma, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        logger.error("Error while decoding ma: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid ma"
        )


async def dang_nhap_service(
    session: AsyncSession, dang_nhap_schema: DangNhapSchema
) -> DangNhapResponse:
    """
    Authenticate a nguoi_dung using login credentials.
    """
    try:
        nguoi_dung = await crud_nguoi_dung.get(session, email=dang_nhap_schema.email)
        if (
            nguoi_dung is None
            or not nguoi_dung.mat_khau_ma_hoa
            or not xac_thuc_mat_khau(
                dang_nhap_schema.mat_khau, nguoi_dung.mat_khau_ma_hoa
            )
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or mat_khau",
            )

        await vo_hieu_hoa_toan_bo_ma_lam_moi_bang_nguoi_dung_id(
            session, str(nguoi_dung.id)
        )
        return await tao_ma_xac_thuc_cho_nguoi_dung(session, nguoi_dung)

    except Exception as e:
        logger.error("Error during authentication: %s", e)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=GENERIC_ERROR_MSG
        )


async def tao_ma_xac_thuc_cho_nguoi_dung(
    session: AsyncSession, nguoi_dung: NguoiDung
) -> DangNhapResponse:
    """
    Generate and return access and lam_moi mas for a nguoi_dung.
    """
    try:
        ma_xac_thuc = tao_ma_xac_thuc(nguoi_dung)
        ma_lam_moi = tao_ma_lam_moi(nguoi_dung)
        ma_xac_thuc_data = giai_ma_ma(ma_xac_thuc)

        ma_lam_moi_data = {
            "ma": ma_lam_moi,
            "thoi_gian_het_han": giai_ma_ma(ma_lam_moi)["thoi_gian_het_han"],
            "nguoi_dung_id": nguoi_dung.id,
        }
        await crud_ma_lam_moi.create(session, MaLamMoiCreate(**ma_lam_moi_data))

        return DangNhapResponse(
            ma_xac_thuc=ma_xac_thuc,
            ma_lam_moi=ma_lam_moi,
            thoi_gian_het_han=ma_xac_thuc_data["thoi_gian_het_han"],
            loai_ma="bearer",
        )
    except Exception as e:
        logger.error("Error while generating mas for nguoi_dung: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate mas",
        )


async def lam_moi_ma_xac_thuc_service(
    session: AsyncSession, ma_lam_moi_schema: MaLamMoiSchema
) -> DangNhapResponse:
    """
    Refresh access and refresh tokens using a valid refresh token.
    """
    try:
        # Attempt to decode the refresh token
        try:
            ma_lam_moi_data = giai_ma_ma(ma_lam_moi_schema.ma_lam_moi)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        # Retrieve the refresh token from the database
        ma_lam_moi_in_db = await crud_ma_lam_moi.get(
            session, ma=ma_lam_moi_schema.ma_lam_moi
        )
        if not ma_lam_moi_in_db:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        # Check if the token has been revoked
        if ma_lam_moi_in_db.da_thu_hoi:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This token has been revoked",
            )

        # Retrieve the user associated with the token
        nguoi_dung = await crud_nguoi_dung.get(
            session, id=ma_lam_moi_data.get("nguoi_dung_id")
        )
        if not nguoi_dung:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Revoke the existing refresh token before issuing a new one
        await thu_hoi_ma_lam_moi(session, ma_lam_moi_in_db)

        # Generate and return new access and refresh tokens for the user
        return await tao_ma_xac_thuc_cho_nguoi_dung(session, nguoi_dung)

    except HTTPException as http_exc:
        # Re-raise HTTP exceptions to handle known errors gracefully
        raise http_exc
    except Exception as e:
        # Log unexpected errors in detail for debugging purposes
        logger.error("Unexpected error in lam_moi_ma_xac_thuc_service: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred. Please try again later.",
        )


async def thu_hoi_ma_lam_moi(
    session: AsyncSession, ma_lam_moi: MaLamMoiUpdateDB
) -> None:
    """
    Revoke the given lam_moi ma.
    """
    try:
        ma_lam_moi.da_thu_hoi = True
        ma_lam_moi.thoi_gian_thu_hoi = datetime.now()
        await crud_ma_lam_moi.update(
            session, db_obj=ma_lam_moi, obj_in=MaLamMoiUpdateDB(**ma_lam_moi.dict())
        )
    except Exception as e:
        logger.error("Error while revoking lam_moi ma: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to thu_hoi lam_moi ma",
        )


async def dang_ky_service(
    session: AsyncSession, dang_ky: DangKySchema
) -> DangKyResponse:
    """
    Sign up a new user.
    """
    try:
        # Check if a user with the provided email already exists
        existing_user = await crud_nguoi_dung.get(session, email=dang_ky.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists",
            )

        # Prepare new user data
        new_user_data = {
            "ten_nguoi_dung": dang_ky.ten_nguoi_dung,
            "email": dang_ky.email,
            "mat_khau": dang_ky.mat_khau,  # Ensure hashing if not done in the model
            "quyen": "nguoi_dung",
            "anh_dai_dien": dang_ky.anh_dai_dien,
            "gioi_tinh": dang_ky.gioi_tinh,
            "ngay_sinh": dang_ky.ngay_sinh,
            "trang_thai": "hoat_dong",
        }

        # Create a new user entry in the database
        nguoi_dung_create = await crud_nguoi_dung.create(
            session, NguoiDungCreate(**new_user_data)
        )
        nguoi_dung_create_with_out_password = nguoi_dung_create.dict()
        nguoi_dung_create_with_out_password.pop("mat_khau_ma_hoa")
        return DangKyResponse(**nguoi_dung_create_with_out_password)

    except HTTPException as http_exc:
        # Re-raise known HTTP exceptions
        raise http_exc
    except Exception as e:
        # Log unexpected errors for diagnostics
        logger.error("Unexpected error during user registration: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user. Please try again later.",
        )


async def dang_xuat_service(session: AsyncSession, nguoi_dung_id: str) -> Response:
    """
    Log out a nguoi_dung by deactivating all lam_moi mas.
    """
    try:
        await vo_hieu_hoa_toan_bo_ma_lam_moi_bang_nguoi_dung_id(session, nguoi_dung_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"detail": "Logged out successfully"},
        )
    except Exception as e:
        logger.error("Error while logging out: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=GENERIC_ERROR_MSG
        )
