from fastapi import APIRouter, Depends, Request, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.nguoi_dung import NguoiDungCreate, NguoiDungUpdateDB, DoiMatKhau
from utils.security import xac_thuc_mat_khau
from api.deps import get_session, get_nguoi_dung_hien_tai

from services.crud.nguoi_dung import crud_nguoi_dung

router = APIRouter(prefix="/nguoi_dung", tags=["Nguoi dung"])


@router.get("")
async def xem_thong_tin_ca_nhan(
    nguoi_dung_hien_tai: dict = Depends(get_nguoi_dung_hien_tai),
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to get nguoi_dung information.
    """
    result = nguoi_dung_hien_tai
    return result


@router.put("/doi_mat_khau")
async def doi_mat_khau(
    dmk_data: DoiMatKhau,
    nguoi_dung_hien_tai: dict = Depends(get_nguoi_dung_hien_tai),
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to change password.
    """
    try:
        nguoi_dung_db = await crud_nguoi_dung.get(
            session, id=nguoi_dung_hien_tai.get("id")
        )
        if not nguoi_dung_db:
            raise HTTPException(status_code=404, detail="Nguoi dung khong ton tai")

        if not xac_thuc_mat_khau(plain_password=dmk_data.mat_khau_cu, mat_khau_ma_hoa=nguoi_dung_db.mat_khau_ma_hoa):
            raise HTTPException(status_code=400, detail="Sai mat khau cu")

        nguoi_dung_update_data = {
            "mat_khau": dmk_data.mat_khau_moi
        }
        
        
        
        result = await crud_nguoi_dung.update(session, obj_in=NguoiDungUpdateDB(**nguoi_dung_update_data), db_obj=nguoi_dung_db)

        return {"message": "Doi mat khau thanh cong"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("")
async def cap_nhat_thong_tin_ca_nhan(
    nguoi_dung_update_data: NguoiDungUpdateDB,
    nguoi_dung_hien_tai: dict = Depends(get_nguoi_dung_hien_tai),
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to update nguoi_dung information.
    """
    try:
        # verify that the user is updating their own information
        nguoi_dung_db = await crud_nguoi_dung.get(
            session, id=nguoi_dung_hien_tai.get("id")
        )
        if not nguoi_dung_db:
            raise HTTPException(status_code=404, detail="Nguoi dung khong ton tai")

        if nguoi_dung_update_data.email:
            nguoi_dung_with_same_email = await crud_nguoi_dung.get(
                session, email=nguoi_dung_update_data.email
            )

            if (
                nguoi_dung_with_same_email
                and nguoi_dung_with_same_email.id != nguoi_dung_hien_tai.get("id")
            ):
                raise HTTPException(status_code=400, detail="Email da ton tai")

        if nguoi_dung_db.id != nguoi_dung_hien_tai["id"]:
            raise HTTPException(
                status_code=403, detail="Khong co quyen cap nhat thong tin nguoi dung"
            )

        nguoi_dung_updated = await crud_nguoi_dung.update(
            session, obj_in=nguoi_dung_update_data, db_obj=nguoi_dung_db
        )

        nguoi_dung_updated_with_out_password = nguoi_dung_updated.dict()
        nguoi_dung_updated_with_out_password.pop("mat_khau_ma_hoa")

        return nguoi_dung_updated_with_out_password

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

