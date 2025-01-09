from fastapi import APIRouter, Depends, Request, Query, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import boto3
from botocore.exceptions import NoCredentialsError
import json
import tempfile
import os
from config.config import settings
from schemas.nguoi_dung import NguoiDungCreate, NguoiDungUpdateDB
from schemas.bai_hat import BaiHatCreate, BaiHatUpdateDB
from api.deps import get_session, get_nguoi_dung_hien_tai
from services.crud.nguoi_dung import crud_nguoi_dung
from services.crud.bai_hat import crud_bai_hat
from services.crud.thanh_vien_phong import crud_thanh_vien_phong
from services.crud.phong_nghe_nhac import crud_phong_nghe_nhac
from models.tin_nhan import TinNhan
from schemas.tin_nhan import TinNhanCreate, TinNhanUpdateDB
from services.crud.tin_nhan import crud_tin_nhan
from openai import OpenAI
import openai

router = APIRouter(prefix="/tin_nhan", tags=["Tin Nhan"])

@router.get("/phong_nghe_nhac/{phong_nghe_nhac_id}")
async def xem_tin_nhan(
    phong_nghe_nhac_id: str,
    nguoi_dung_hien_tai: NguoiDungCreate = Depends(get_nguoi_dung_hien_tai),
    session: AsyncSession = Depends(get_session),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
):
    """
    Endpoint to search for songs by name.
    """
    try:
        phong_nghe_nhac = await crud_phong_nghe_nhac.get(session, id=phong_nghe_nhac_id)
        if not phong_nghe_nhac:
            raise HTTPException(status_code=404, detail="Phong nghe nhac not found")
        
        thanh_vien_phong = await crud_thanh_vien_phong.get(session, phong_nghe_nhac_id=phong_nghe_nhac_id, nguoi_dung_id=nguoi_dung_hien_tai['id'])
        if not thanh_vien_phong:
            raise HTTPException(status_code=403, detail="You are not a member of this room")
        
        tin_nhans = await crud_tin_nhan.get_multi(
            session, phong_nghe_nhac_id=phong_nghe_nhac_id, offset=offset, limit=limit
        )
        
        if not tin_nhans:
            return []
        return tin_nhans
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# tim kiem tin nhan
@router.get("/phong_nghe_nhac/{phong_nghe_nhac_id}/tim_kiem")
async def tim_kiem_tin_nhan(
    request: Request,
    phong_nghe_nhac_id: str,
    nguoi_dung_hien_tai: NguoiDungCreate = Depends(get_nguoi_dung_hien_tai),
    session: AsyncSession = Depends(get_session),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
):
    """
    Endpoint to search for songs by name.
    """
    try:
        filters = {
            key: value
            for key, value in request.query_params.items()
            if key not in ["offset", "limit"]
        }

        phong_nghe_nhac = await crud_phong_nghe_nhac.get(session, id=phong_nghe_nhac_id)
        if not phong_nghe_nhac:
            raise HTTPException(status_code=404, detail="Phong nghe nhac not found")
        
        thanh_vien_phong = await crud_thanh_vien_phong.get(session, phong_nghe_nhac_id=phong_nghe_nhac_id, nguoi_dung_id=nguoi_dung_hien_tai['id'])
        if not thanh_vien_phong:
            raise HTTPException(status_code=403, detail="You are not a member of this room")
        
        tin_nhans = await crud_tin_nhan.search(
            session, offset=offset, limit=limit, **filters
        )
        
        # remove tin nhans that are not in the room
        tin_nhans = [tin_nhan for tin_nhan in tin_nhans if str(tin_nhan.phong_nghe_nhac_id) == phong_nghe_nhac_id]
        
        if not tin_nhans:
            return []
        
        return tin_nhans
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
        