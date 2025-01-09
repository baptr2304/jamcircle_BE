"""
This module provides common dependencies for the FastAPI application,
such as retrieving the current nguoi_dung,
validating tokens, and establishing a database session.
"""

from fastapi import Depends, HTTPException, Request, WebSocket
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from config.config import settings
from config.database.database import AsyncSessionLocal
from services.auth.security import ALGORITHM
from services.crud.nguoi_dung import crud_nguoi_dung
from schemas.ma_xac_thuc import ThongTinMaSchema


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


def get_ma_from_header(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return auth_header.split(" ")[1]

# websockets
def get_ma_from_websocket(websocket: WebSocket) -> str:
    auth_header = websocket.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        # get from query params
        query_params = websocket.query_params
        if "access_token" in query_params:
            return query_params["access_token"]
        return None
    return auth_header.split(" ")[1]


def get_thong_tin_ma(ma: str = Depends(get_ma_from_header)) -> ThongTinMaSchema:
    try:
        if ma is None:
            raise HTTPException(status_code=401, detail="Invalid or missing token")
        thong_tin = jwt.decode(ma, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return ThongTinMaSchema(**thong_tin)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(status_code=403, detail="Could not validate credentials")

# websockets
def get_thong_tin_ma_websocket(ma: str = Depends(get_ma_from_websocket)) -> ThongTinMaSchema:
    try:
        if ma is None:
            return None
        thong_tin = jwt.decode(ma, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return ThongTinMaSchema(**thong_tin)
    except (jwt.JWTError, ValidationError):
        return None

async def get_nguoi_dung_hien_tai(
    thong_tin_ma_xac_thuc: ThongTinMaSchema = Depends(get_thong_tin_ma),
    session: AsyncSession = Depends(get_session),
):
    print('thong_tin_ma_xac_thuc', thong_tin_ma_xac_thuc)
    nguoi_dung = await crud_nguoi_dung.get(
        session, id=thong_tin_ma_xac_thuc.nguoi_dung_id
    )
    if nguoi_dung is None:
        raise HTTPException(status_code=404, detail="NguoiDung not found")
    if nguoi_dung.trang_thai != "hoat_dong":
        raise HTTPException(status_code=400, detail="Inactive nguoi_dung")
    nguoi_dung_with_out_password = nguoi_dung.dict()
    nguoi_dung_with_out_password.pop("mat_khau_ma_hoa")
    return nguoi_dung_with_out_password

# websockets
async def get_nguoi_dung_hien_tai_websocket(
    thong_tin_ma_xac_thuc: ThongTinMaSchema = Depends(get_thong_tin_ma_websocket),
    session: AsyncSession = Depends(get_session)
):
    if thong_tin_ma_xac_thuc is None:
        return None
    nguoi_dung = await crud_nguoi_dung.get(
        session, id=thong_tin_ma_xac_thuc.nguoi_dung_id
    )
    
    if nguoi_dung is None:
        return None
    if nguoi_dung.trang_thai != "hoat_dong":
        return None
    nguoi_dung_with_out_password = nguoi_dung.dict()
    nguoi_dung_with_out_password.pop("mat_khau_ma_hoa")
    return nguoi_dung_with_out_password

async def kiem_tra_quyen_quan_tri(nguoi_dung: dict = Depends(get_nguoi_dung_hien_tai)):
    if nguoi_dung["quyen"] != "quan_tri_vien":
        raise HTTPException(status_code=403, detail="Permission denied")
    return nguoi_dung
