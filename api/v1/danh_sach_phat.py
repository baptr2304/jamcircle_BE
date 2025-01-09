from fastapi import APIRouter, Depends, Request, Query, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import boto3
from botocore.exceptions import NoCredentialsError
import json

from config.config import settings
from schemas.nguoi_dung import NguoiDungCreate, NguoiDungUpdateDB
from schemas.bai_hat import BaiHatCreate, BaiHatUpdateDB
from schemas.danh_sach_phat import DanhSachPhatCreate, DanhSachPhatUpdateDB
from schemas.danh_sach_phat_bai_hat import DanhSachPhatBaiHatCreate, DanhSachPhatBaiHatUpdateDB
from api.deps import get_session, get_nguoi_dung_hien_tai
from services.crud.nguoi_dung import crud_nguoi_dung
from services.crud.bai_hat import crud_bai_hat
from services.crud.danh_sach_phat import crud_danh_sach_phat
from services.crud.danh_sach_phat_bai_hat import crud_danh_sach_phat_bai_hat


router = APIRouter(prefix="/danh_sach_phat", tags=["Danh sach phat"])


@router.get("")
async def xem_danh_sach_phat(
    session: AsyncSession = Depends(get_session),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
):
    """
    Endpoint to get all playlists.
    """
    try:
        danh_sach_phats = await crud_danh_sach_phat.get_multi(session, offset=offset, limit=limit)

        # remove the danh_sach_phat have loai = "phong_nghe_nhac"
        danh_sach_phats = [dsph for dsph in danh_sach_phats if dsph.loai != "phong_nghe_nhac"]
        
        # sort by ten_danh_sach_phat a to z
        danh_sach_phats = sorted(danh_sach_phats, key=lambda x: x.ten_danh_sach_phat)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return danh_sach_phats


@router.get("/tim_kiem")
async def tim_kiem_danh_sach_phat(
    request: Request,
    session: AsyncSession = Depends(get_session),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
):
    """
    Endpoint to search for playlists by name.
    """
    filters = {
        key: value
        for key, value in request.query_params.items()
        if key not in ["offset", "limit"]
    }
    try:
        danh_sach_phats = await crud_danh_sach_phat.search(session, offset=offset, limit=limit, **filters)
        if not danh_sach_phats:
            return []
        # remove the danh_sach_phat have loai = "phong_nghe_nhac"
        danh_sach_phats  = [dsph for dsph in danh_sach_phats if dsph.loai != "phong_nghe_nhac"]
        return danh_sach_phats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/nguoi_dung")
async def xem_danh_sach_phat_cua_nguoi_dung(
    loai: str,
    nguoi_dung_hien_tai: dict = Depends(get_nguoi_dung_hien_tai),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to get playlists of a user.
    """
    try:
        danh_sach_phats = await crud_danh_sach_phat.get_multi(session, nguoi_dung_id=nguoi_dung_hien_tai.get("id"), loai=loai, offset=offset, limit=limit)
        if not danh_sach_phats:
            return []
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return danh_sach_phats

@router.get("/{id}")
async def xem_chi_tiet_danh_sach_phat(
    id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to get playlist details by ID.
    """
    try:
        danh_sach_phat = await crud_danh_sach_phat.get(session, id=id)
        if not danh_sach_phat:
            raise HTTPException(status_code=404, detail="Danh sach phat not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return danh_sach_phat


@router.get("/{id}/bai_hat")
async def xem_danh_sach_bai_hat_trong_danh_sach_phat(
    id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to get the songs in a playlist.
    """
    try:
        danh_sach_phat = await crud_danh_sach_phat.get(session, id=id)
        if not danh_sach_phat:
            raise HTTPException(status_code=404, detail="Danh sach phat not found")
        
        danh_sach_phat_bai_hat = await crud_danh_sach_phat_bai_hat.get_multi(session, danh_sach_phat_id=id)
        if not danh_sach_phat_bai_hat:
            return []
        
        # sort by so_thu_tu
        danh_sach_phat_bai_hat = sorted(danh_sach_phat_bai_hat, key=lambda x: x.so_thu_tu)
        
        danh_sach_bai_hat = []
        for dsphbh in danh_sach_phat_bai_hat:
            bai_hat = await crud_bai_hat.get(session, id=dsphbh.bai_hat_id)
            if bai_hat:
                bai_hat_dict = bai_hat.dict()
                bai_hat_dict["so_thu_tu"] = dsphbh.so_thu_tu
                danh_sach_bai_hat.append(bai_hat_dict)
                
        return danh_sach_bai_hat
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("")
async def tao_danh_sach_phat(
    danh_sach_phat_create_data: DanhSachPhatCreate,
    nguoi_dung_hien_tai: dict = Depends(get_nguoi_dung_hien_tai),
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to create a playlist.
    """
    try:
        danh_sach_phat_create_data.nguoi_dung_id = nguoi_dung_hien_tai.get("id")
        danh_sach_phat = await crud_danh_sach_phat.create(session, danh_sach_phat_create_data)
        
    except Exception as e:  
        raise HTTPException(status_code=400, detail=str(e))
    if not danh_sach_phat:
        raise HTTPException(status_code=400, detail="Failed to create playlist")
    return danh_sach_phat

@router.put("/{id}")
async def cap_nhat_danh_sach_phat(
    id: str,
    danh_sach_phat_update_data: DanhSachPhatUpdateDB,
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to update playlist information.
    """
    try:
        danh_sach_phat_create_db = await crud_danh_sach_phat.get(session, id=id)
        if not danh_sach_phat_create_db:
            raise HTTPException(status_code=404, detail="Danh sach phat not found")
        
        danh_sach_phat_update_db = await crud_danh_sach_phat.update(session, obj_in=danh_sach_phat_update_data, db_obj=danh_sach_phat_create_db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return danh_sach_phat_update_db


# them bai hat vao danh sach phat
@router.post("/{danh_sach_phat_id}/bai_hat/{bai_hat_id}")
async def them_bai_hat_vao_danh_sach_phat(
    danh_sach_phat_id: str,
    bai_hat_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to add a song to a playlist.
    """
    try:
        danh_sach_phat = await crud_danh_sach_phat.get(session, id=danh_sach_phat_id)
        if not danh_sach_phat:
            raise HTTPException(status_code=404, detail="Danh sach phat not found")
        
        bai_hat = await crud_bai_hat.get(session, id=bai_hat_id)
        if not bai_hat:
            raise HTTPException(status_code=404, detail="Bai hat not found")
        
        # get the number of songs in the playlist
        danh_sach_phat_bai_hat = await crud_danh_sach_phat_bai_hat.get_multi(session, danh_sach_phat_id=danh_sach_phat_id)
        so_thu_tu = len(danh_sach_phat_bai_hat) + 1
        danh_sach_phat_bai_hat_create_data = {
            "danh_sach_phat_id": danh_sach_phat_id,
            "bai_hat_id": bai_hat_id,
            "so_thu_tu": so_thu_tu
        }
        
        
        danh_sach_phat_bai_hat = await crud_danh_sach_phat_bai_hat.create(session, obj_in=DanhSachPhatBaiHatCreate(**danh_sach_phat_bai_hat_create_data))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return danh_sach_phat_bai_hat


# cap nhat so thu tu cua bai hat trong danh sach phat
@router.put("/{danh_sach_phat_id}/bai_hat/{bai_hat_id}")
async def cap_nhat_so_thu_tu_cua_bai_hat_trong_danh_sach_phat(
    danh_sach_phat_id: str,
    bai_hat_id: str,
    so_thu_tu_cu: int,
    so_thu_tu_moi: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Endpoint to update the order of a song in a playlist.
    """
    try:
        danh_sach_phat = await crud_danh_sach_phat.get(session, id=danh_sach_phat_id)
        if not danh_sach_phat:
            raise HTTPException(status_code=404, detail="Danh sach phat not found")
        
        bai_hat = await crud_bai_hat.get(session, id=bai_hat_id)
        if not bai_hat:
            raise HTTPException(status_code=404, detail="Bai hat not found")
        
        danh_sach_phat_bai_hat = await crud_danh_sach_phat_bai_hat.get_multi(session, danh_sach_phat_id=danh_sach_phat_id)
        if not danh_sach_phat_bai_hat:
            raise HTTPException(status_code=404, detail="Bai hat not found in playlist")
        
        # sort danh_sach_phat_bai_hat by so_thu_tu
        danh_sach_phat_bai_hat = sorted(danh_sach_phat_bai_hat, key=lambda x: x.so_thu_tu)
        if so_thu_tu_moi < so_thu_tu_cu:
            for dsphbh in danh_sach_phat_bai_hat:
                if dsphbh.so_thu_tu >= so_thu_tu_moi and dsphbh.so_thu_tu <= so_thu_tu_cu:
                    if dsphbh.so_thu_tu == so_thu_tu_cu:
                        dsphbh_update = {
                            "so_thu_tu": so_thu_tu_moi
                        }
                        dsphbh_update_data = DanhSachPhatBaiHatUpdateDB(**dsphbh_update)
                        bai_hat_update_db = await crud_danh_sach_phat_bai_hat.update(session, obj_in=dsphbh_update_data, db_obj=dsphbh)
                    else:
                        dsphbh_update = {
                            "so_thu_tu": dsphbh.so_thu_tu + 1
                        }
                        dsphbh_update_data = DanhSachPhatBaiHatUpdateDB(**dsphbh_update)
                        await crud_danh_sach_phat_bai_hat.update(session, obj_in=dsphbh_update_data, db_obj=dsphbh)
                        print("Updated so_thu_tu: ", dsphbh.so_thu_tu)
        elif so_thu_tu_moi > so_thu_tu_cu:
            for dsphbh in danh_sach_phat_bai_hat:
                if dsphbh.so_thu_tu >= so_thu_tu_cu and dsphbh.so_thu_tu <= so_thu_tu_moi:
                    if dsphbh.so_thu_tu == so_thu_tu_cu:
                        dsphbh_update = {
                            "so_thu_tu": so_thu_tu_moi
                        }
                        dsphbh_update_data = DanhSachPhatBaiHatUpdateDB(**dsphbh_update)
                        bai_hat_update_db = await crud_danh_sach_phat_bai_hat.update(session, obj_in=dsphbh_update_data, db_obj=dsphbh)
                    else:
                        print("Updated so_thu_tu: ", dsphbh.so_thu_tu)
                        dsphbh_update = {
                            "so_thu_tu": dsphbh.so_thu_tu - 1
                        }
                        dsphbh_update_data = DanhSachPhatBaiHatUpdateDB(**dsphbh_update)
                        await crud_danh_sach_phat_bai_hat.update(session, obj_in=dsphbh_update_data, db_obj=dsphbh)
                    
        return bai_hat_update_db
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# xoa bai hat khoi danh sach phat
@router.delete("/{danh_sach_phat_id}/bai_hat")
async def xoa_bai_hat_khoi_danh_sach_phat(
    danh_sach_phat_id: str,
    so_thu_tu: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to remove a song from a playlist.
    """
    try:
        danh_sach_phat = await crud_danh_sach_phat.get(session, id=danh_sach_phat_id)
        if not danh_sach_phat:
            raise HTTPException(status_code=404, detail="Danh sach phat not found")
        
        
        # cap nhat so thu tu cua cac bai hat con lai
        danh_sach_phat_bai_hats = await crud_danh_sach_phat_bai_hat.get_multi(session, danh_sach_phat_id=danh_sach_phat_id)
        
        # sort danh_sach_phat_bai_hat by so_thu_tu
        danh_sach_phat_bai_hats = sorted(danh_sach_phat_bai_hats, key=lambda x: x.so_thu_tu)
        for dsphbh in danh_sach_phat_bai_hats:
            if dsphbh.so_thu_tu > so_thu_tu:
                dsphbh_update = {
                    "so_thu_tu": dsphbh.so_thu_tu - 1
                }
                dsphbh_update_data = DanhSachPhatBaiHatUpdateDB(**dsphbh_update)
                await crud_danh_sach_phat_bai_hat.update(session, obj_in=dsphbh_update_data, db_obj=dsphbh)
        
        danh_sach_phat_bai_hat = await crud_danh_sach_phat_bai_hat.get(session, danh_sach_phat_id=danh_sach_phat_id, so_thu_tu=so_thu_tu)
        if not danh_sach_phat_bai_hat:
            raise HTTPException(status_code=404, detail="Bai hat not found in playlist")
        
        result = await crud_danh_sach_phat_bai_hat.delete(session, db_obj=danh_sach_phat_bai_hat)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to remove song from playlist")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Successfully removed song from playlist"}


# xoa danh sach phat
@router.delete("/{id}")
async def xoa_danh_sach_phat(
    id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to remove a playlist.
    """
    try:
        danh_sach_phat = await crud_danh_sach_phat.get(session, id=id)
        if not danh_sach_phat:
            raise HTTPException(status_code=404, detail="Danh sach phat not found")
        
        # xoa tat ca cac da_sach_phat_bai_hat lien quan
        danh_sach_phat_bai_hat = await crud_danh_sach_phat_bai_hat.get_multi(session, danh_sach_phat_id=id)
        if danh_sach_phat_bai_hat:
            for dsphbh in danh_sach_phat_bai_hat:
                await crud_danh_sach_phat_bai_hat.delete(session, db_obj=dsphbh)
        
        result = await crud_danh_sach_phat.delete(session, db_obj=danh_sach_phat)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to remove playlist")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Successfully removed playlist"}


async def xoa_bai_hat_khoi_danh_sach_phat_ws(
    danh_sach_phat_id: str,
    so_thu_tu: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to remove a song from a playlist.
    """
    try:
        danh_sach_phat = await crud_danh_sach_phat.get(session, id=danh_sach_phat_id)
        if not danh_sach_phat:
            return {"message": "Danh sach phat not found"}
        
        
        # cap nhat so thu tu cua cac bai hat con lai
        danh_sach_phat_bai_hats = await crud_danh_sach_phat_bai_hat.get_multi(session, danh_sach_phat_id=danh_sach_phat_id)
        
        # sort danh_sach_phat_bai_hat by so_thu_tu
        danh_sach_phat_bai_hats = sorted(danh_sach_phat_bai_hats, key=lambda x: x.so_thu_tu)
        for dsphbh in danh_sach_phat_bai_hats:
            if dsphbh.so_thu_tu > so_thu_tu:
                dsphbh_update = {
                    "so_thu_tu": dsphbh.so_thu_tu - 1
                }
                dsphbh_update_data = DanhSachPhatBaiHatUpdateDB(**dsphbh_update)
                await crud_danh_sach_phat_bai_hat.update(session, obj_in=dsphbh_update_data, db_obj=dsphbh)
        
        danh_sach_phat_bai_hat = await crud_danh_sach_phat_bai_hat.get(session, danh_sach_phat_id=danh_sach_phat_id, so_thu_tu=so_thu_tu)
        if not danh_sach_phat_bai_hat:
            return {"message": "Bai hat not found in playlist"}
        
        result = await crud_danh_sach_phat_bai_hat.delete(session, db_obj=danh_sach_phat_bai_hat)
        if not result:
            return {"message": "Failed to remove song from playlist"}
    except Exception as e:
        return {"message": str(e)}
    return 1