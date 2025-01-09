from fastapi import APIRouter, Depends, Request, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.nguoi_dung import NguoiDungCreate, NguoiDungUpdateDB
from api.deps import get_session, kiem_tra_quyen_quan_tri

from services.crud.nguoi_dung import crud_nguoi_dung

router = APIRouter(prefix="/nguoi_dung", tags=["Quan ly nguoi dung"])


@router.get("")
async def xem_danh_sach_nguoi_dung(
    kiem_tra_quyen: dict = Depends(kiem_tra_quyen_quan_tri),
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to get nguoi_dung information.
    """
    try:
        result = await crud_nguoi_dung.get_multi(session)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.get("/tim_kiem")
async def tim_kiem_nguoi_dung(
    request: Request,
    kiem_tra_quyen: dict = Depends(kiem_tra_quyen_quan_tri),
    session: AsyncSession = Depends(get_session),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
):
    """
    Endpoint to search for nguoi_dung accounts by name.
    """
    filters = {
        key: value
        for key, value in request.query_params.items()
        if key not in ["offset", "limit"]
    }
    try:
        result = await crud_nguoi_dung.search(
            session, offset=offset, limit=limit, **filters
        )
        if not result:
            return []
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{id}")
async def xem_chi_tiet_nguoi_dung(
    id: str,
    kiem_tra_quyen: dict = Depends(kiem_tra_quyen_quan_tri),
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to get detailed information about a specific nguoi_dung account.
    """
    try:
        result = await crud_nguoi_dung.get(session, id=id)
        if not result:
            raise HTTPException(status_code=404, detail="Nguoi dung khong ton tai")
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("")
async def tao_nguoi_dung(
    nguoi_dung_create_data: NguoiDungCreate,
    kiem_tra_quyen: dict = Depends(kiem_tra_quyen_quan_tri),
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to create a new nguoi_dung account.
    """
    try:
        result = await crud_nguoi_dung.create(session, nguoi_dung_create_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{id_nguoi_dung}")
async def cap_nhat_nguoi_dung(
    id_nguoi_dung: str,
    nguoi_dung_update_data: NguoiDungUpdateDB,
    kiem_tra_quyen: dict = Depends(kiem_tra_quyen_quan_tri),
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to update a nguoi_dung account.
    """
    try:
        nguoi_dung_in_db = await crud_nguoi_dung.get(session, id=id_nguoi_dung)

        if not nguoi_dung_in_db:
            raise HTTPException(status_code=404, detail="Nguoi dung khong ton tai")

        if nguoi_dung_update_data.email:
            nguoi_dung_with_same_email = await crud_nguoi_dung.get(
                session, email=nguoi_dung_update_data.email
            )
            if (
                nguoi_dung_with_same_email
                and str(nguoi_dung_with_same_email.id) != id_nguoi_dung
            ):
                raise HTTPException(status_code=400, detail="Email da ton tai")

        nguoi_dung_updated = await crud_nguoi_dung.update(
            session, obj_in=nguoi_dung_update_data, db_obj=nguoi_dung_in_db
        )
        nguoi_dung_updated_with_out_password = nguoi_dung_updated.dict()
        nguoi_dung_updated_with_out_password.pop("mat_khau_ma_hoa")

        raise HTTPException(status_code=200, detail="Cap nhat thanh cong")
    except Exception as e:
        return {"error": str(e)}
