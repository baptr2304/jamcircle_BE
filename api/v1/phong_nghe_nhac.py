from fastapi import APIRouter, Depends, Request, Query, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.phong_nghe_nhac import PhongNgheNhacCreate, PhongNgheNhacUpdateDB
from schemas.danh_sach_phat import DanhSachPhatCreate, DanhSachPhatUpdateDB
from schemas.thanh_vien_phong import ThanhVienPhongCreate, ThanhVienPhongUpdateDB
from schemas.yeu_cau_tham_gia_phong import YeuCauThamGiaPhongCreate, YeuCauThamGiaPhongUpdateDB
from schemas.danh_sach_phat_bai_hat import DanhSachPhatBaiHatCreate, DanhSachPhatBaiHatUpdateDB
from schemas.yeu_cau_tham_gia_phong import YeuCauThamGiaPhongCreate, YeuCauThamGiaPhongUpdateDB
from api.deps import get_session, get_nguoi_dung_hien_tai

from services.crud.nguoi_dung import crud_nguoi_dung
from services.crud.phong_nghe_nhac import crud_phong_nghe_nhac
from services.crud.danh_sach_phat import crud_danh_sach_phat
from services.crud.thanh_vien_phong import crud_thanh_vien_phong
from services.crud.danh_sach_phat_bai_hat import crud_danh_sach_phat_bai_hat
from services.crud.yeu_cau_tham_gia_phong import crud_yeu_cau_tham_gia_phong

router = APIRouter(prefix="/phong_nghe_nhac", tags=["Phong nghe nhac"])


@router.post("")
async def tao_phong_nghe_nhac(
    phong_nghe_nhac_data: PhongNgheNhacCreate,
    nguoi_dung_hien_tai: dict = Depends(get_nguoi_dung_hien_tai),
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to create a new PhongNgheNhac.
    """
    try:
        # create danh_sach_phat if it does not exist in phong_nghe_nhac_data
        if not phong_nghe_nhac_data.danh_sach_phat_id:
            danh_sach_phat_new = {
                "ten_danh_sach_phat": phong_nghe_nhac_data.ten_phong,
                "loai": "phong_nghe_nhac",
                "nguoi_dung_id": nguoi_dung_hien_tai.get("id")
            }
            danh_sach_phat_created = await crud_danh_sach_phat.create(session, obj_in=DanhSachPhatCreate(**danh_sach_phat_new))
        else:
            # check if danh_sach_phat_id exists
            danh_sach_phat = await crud_danh_sach_phat.get(session, id=phong_nghe_nhac_data.danh_sach_phat_id)
            if not danh_sach_phat:
                raise HTTPException(status_code=404, detail="Danh sach phat khong ton tai")
            
            # copy danh_sach_phat to new danh_sach_phat
            danh_sach_phat_new = {
                "ten_danh_sach_phat": phong_nghe_nhac_data.ten_phong,
                "loai": "phong_nghe_nhac",
                "nguoi_dung_id": nguoi_dung_hien_tai.get("id")
            }
            danh_sach_phat_created = await crud_danh_sach_phat.create(session, obj_in=DanhSachPhatCreate(**danh_sach_phat_new))
            # copy danh_sach_phat's bai_hats to new danh_sach_phat
            danh_sach_phat_bai_hats = await crud_danh_sach_phat_bai_hat.get_multi(session, danh_sach_phat_id=danh_sach_phat.id)
            
            for danh_sach_phat_bai_hat in danh_sach_phat_bai_hats:
                danh_sach_phat_bai_hat_new = {
                    "bai_hat_id": danh_sach_phat_bai_hat.bai_hat_id,
                    "danh_sach_phat_id": danh_sach_phat_created.id,
                    "so_thu_tu": danh_sach_phat_bai_hat.so_thu_tu
                }
                await crud_danh_sach_phat_bai_hat.create(session, obj_in=DanhSachPhatBaiHatCreate(**danh_sach_phat_bai_hat_new))
                
        # create phong_nghe_nhac
        phong_nghe_nhac_new = {
            "ten_phong": phong_nghe_nhac_data.ten_phong,
            "danh_sach_phat_id": danh_sach_phat_created.id
        }
        phong_nghe_nhac_created = await crud_phong_nghe_nhac.create(session, obj_in=PhongNgheNhacCreate(**phong_nghe_nhac_new))
        
        # create thanh_vien_phong
        thanh_vien_phong_new = {
            "phong_nghe_nhac_id": phong_nghe_nhac_created.id,
            "nguoi_dung_id": nguoi_dung_hien_tai.get("id"),
            "quyen": "chu_phong"
        }
        
        thanh_vien_phong_created = await crud_thanh_vien_phong.create(session, obj_in=ThanhVienPhongCreate(**thanh_vien_phong_new))
        
        if not phong_nghe_nhac_created:
            raise HTTPException(status_code=400, detail="Tao phong nghe nhac khong thanh cong")
            
        
        result = {
            "phong_nghe_nhac": {
                "id": str(phong_nghe_nhac_created.id),
                "ten_phong": phong_nghe_nhac_created.ten_phong,
                "trang_thai_phat": phong_nghe_nhac_created.trang_thai_phat,
                "thoi_gian_hien_tai_bai_hat": phong_nghe_nhac_created.thoi_gian_hien_tai_bai_hat,
                "so_thu_tu_bai_hat_dang_phat": phong_nghe_nhac_created.so_thu_tu_bai_hat_dang_phat,
                "danh_sach_phat_id": str(phong_nghe_nhac_created.danh_sach_phat_id),
                "thoi_gian_tao": str(phong_nghe_nhac_created.thoi_gian_tao),
            },
            "thanh_vien_phong": [{
                "id": str(thanh_vien_phong_created.id),
                "phong_nghe_nhac_id": str(thanh_vien_phong_created.phong_nghe_nhac_id),
                "nguoi_dung_id": str(thanh_vien_phong_created.nguoi_dung_id),
                "quyen": thanh_vien_phong_created.quyen,
                "trang_thai": thanh_vien_phong_created.trang_thai,
                "thoi_gian_tao": str(thanh_vien_phong_created.thoi_gian_tao)
            }]
        }
        
        return JSONResponse(status_code=200, content=result)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
@router.get("")
async def xem_danh_sach_phong_nghe_nhac(
    nguoi_dung_hien_tai: dict = Depends(get_nguoi_dung_hien_tai),
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to get list of PhongNgheNhac.
    """
    try:
        print(nguoi_dung_hien_tai)
        thanh_vien_phongs = await crud_thanh_vien_phong.get_multi(session, nguoi_dung_id=nguoi_dung_hien_tai.get("id"), trang_thai="HoatDong")
        print('thanh_vien_phongs len:', len(thanh_vien_phongs))
        phong_nghe_nhacs = []
        if not thanh_vien_phongs:
            return JSONResponse(status_code=200, content=phong_nghe_nhacs)
        
        for thanh_vien_phong in thanh_vien_phongs:
            phong_nghe_nhac = await crud_phong_nghe_nhac.get(session, id=thanh_vien_phong.phong_nghe_nhac_id)
            phong_nghe_nhacs.append({
                "id": str(phong_nghe_nhac.id),
                "ten_phong": phong_nghe_nhac.ten_phong,
                "trang_thai_phat": phong_nghe_nhac.trang_thai_phat,
                "thoi_gian_hien_tai_bai_hat": phong_nghe_nhac.thoi_gian_hien_tai_bai_hat,
                "so_thu_tu_bai_hat_dang_phat": phong_nghe_nhac.so_thu_tu_bai_hat_dang_phat,
                "danh_sach_phat_id": str(phong_nghe_nhac.danh_sach_phat_id),
                "thoi_gian_tao": str(phong_nghe_nhac.thoi_gian_tao)
            })
        return JSONResponse(status_code=200, content=phong_nghe_nhacs)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{phong_nghe_nhac_id}")
async def xem_thong_tin_phong_nghe_nhac(
    phong_nghe_nhac_id: str,
    nguoi_dung_hien_tai: dict = Depends(get_nguoi_dung_hien_tai),
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to get PhongNgheNhac information.
    """
    try:
        phong_nghe_nhac = await crud_phong_nghe_nhac.get(session, id=phong_nghe_nhac_id)
        if not phong_nghe_nhac:
            raise HTTPException(status_code=404, detail="Phong nghe nhac khong ton tai")
        result = {
            "id": str(phong_nghe_nhac.id),
            "ten_phong": phong_nghe_nhac.ten_phong,
            "trang_thai_phat": phong_nghe_nhac.trang_thai_phat,
            "thoi_gian_hien_tai_bai_hat": phong_nghe_nhac.thoi_gian_hien_tai_bai_hat,
            "so_thu_tu_bai_hat_dang_phat": phong_nghe_nhac.so_thu_tu_bai_hat_dang_phat,
            "danh_sach_phat_id": str(phong_nghe_nhac.danh_sach_phat_id),
            "thoi_gian_tao": str(phong_nghe_nhac.thoi_gian_tao)
        }
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# cap nhat thong tin phong nghe nhac
@router.put("/cap_nhat_phong_nghe_nhac")
async def cap_nhat_phong_nghe_nhac(
    phong_nghe_nhac_id: str,
    phong_nghe_nhac_update_data: PhongNgheNhacUpdateDB,
    nguoi_dung_hien_tai: dict = Depends(get_nguoi_dung_hien_tai),
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to update PhongNgheNhac information.
    """
    try:
        phong_nghe_nhac = await crud_phong_nghe_nhac.get(session, id=phong_nghe_nhac_id)
        if not phong_nghe_nhac:
            raise HTTPException(status_code=404, detail="Phong nghe nhac khong ton tai")
        
        thanh_vien_phong = await crud_thanh_vien_phong.get(session, phong_nghe_nhac_id=phong_nghe_nhac.id, nguoi_dung_id=nguoi_dung_hien_tai.get("id"))
        if not thanh_vien_phong:
            raise HTTPException(status_code=400, detail="Ban khong phai la thanh vien cua phong")
        
        if thanh_vien_phong.quyen != "chu_phong" and thanh_vien_phong.quyen != "quan_ly":
            raise HTTPException(status_code=400, detail="Ban khong phai chu phong hoac quan ly")
        
        phong_nghe_nhac_updated = await crud_phong_nghe_nhac.update(
            session, obj_in=phong_nghe_nhac_update_data, db_obj=phong_nghe_nhac
        )
        
        result = {
            "id": str(phong_nghe_nhac_updated.id),
            "ten_phong": phong_nghe_nhac_updated.ten_phong,
            "trang_thai_phat": phong_nghe_nhac_updated.trang_thai_phat,
            "thoi_gian_hien_tai_bai_hat": phong_nghe_nhac_updated.thoi_gian_hien_tai_bai_hat,
            "so_thu_tu_bai_hat_dang_phat": phong_nghe_nhac_updated.so_thu_tu_bai_hat_dang_phat,
            "danh_sach_phat_id": str(phong_nghe_nhac_updated.danh_sach_phat_id),
            "thoi_gian_tao": str(phong_nghe_nhac_updated.thoi_gian_tao)
        }
        
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# yeu cau tham gia phong
@router.get("/yeu_cau_tham_gia_phong/{phong_nghe_nhac_id}")
async def yeu_cau_tham_gia_phong(
    phong_nghe_nhac_id: str,
    session: AsyncSession = Depends(get_session),
    nguoi_dung_hien_tai: dict = Depends(get_nguoi_dung_hien_tai),
):
    """
    Endpoint to request to join a PhongNgheNhac.
    """
    try:
        
        # check if the user is already a member of the room
        thanh_vien_phong = await crud_thanh_vien_phong.get(session, phong_nghe_nhac_id=phong_nghe_nhac_id, nguoi_dung_id=nguoi_dung_hien_tai.get("id"))
        if thanh_vien_phong:
            raise HTTPException(status_code=400, detail="Ban da la thanh vien cua phong")
        
        yeu_cau_tham_gia_phong_in_db = await crud_yeu_cau_tham_gia_phong.get(session, phong_nghe_nhac_id=phong_nghe_nhac_id, nguoi_dung_id=nguoi_dung_hien_tai.get("id"))
        if yeu_cau_tham_gia_phong_in_db:
            if yeu_cau_tham_gia_phong_in_db.trang_thai == "chap_nhan":
                raise HTTPException(status_code=400, detail="Ban da tham gia phong")
            if yeu_cau_tham_gia_phong_in_db.trang_thai == "cho_duyet":
                raise HTTPException(status_code=400, detail="Yeu cau tham gia phong cua ban dang cho duyet")
        
        yeu_cau_tham_gia_phong_new = {
            "trang_thai": "cho_duyet",
            "phong_nghe_nhac_id": phong_nghe_nhac_id,
            "nguoi_dung_id": nguoi_dung_hien_tai.get("id")
        }
        
        yeu_cau_tham_gia_phong_created = await crud_yeu_cau_tham_gia_phong.create(session, obj_in=YeuCauThamGiaPhongCreate(**yeu_cau_tham_gia_phong_new))
        response_data = {
            "id": str(yeu_cau_tham_gia_phong_created.id),
            "trang_thai": yeu_cau_tham_gia_phong_created.trang_thai,
            "phong_nghe_nhac_id": str(yeu_cau_tham_gia_phong_created.phong_nghe_nhac_id),
            "nguoi_dung_id": str(yeu_cau_tham_gia_phong_created.nguoi_dung_id),
            "thoi_gian_tao": str(yeu_cau_tham_gia_phong_created.thoi_gian_tao)
        }
        
        return JSONResponse(status_code=200, content=response_data) 
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
async def yeu_cau_tham_gia_phong_ws(
    phong_nghe_nhac_id: str,
    nguoi_dung_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Endpoint to request to join a PhongNgheNhac.
    """
    try:
        
        # check if the user is already a member of the room
        thanh_vien_phong = await crud_thanh_vien_phong.get(session, phong_nghe_nhac_id=phong_nghe_nhac_id, nguoi_dung_id=nguoi_dung_id)
        if thanh_vien_phong:
            return {
                "success": False,
                "message": "Ban da la thanh vien cua phong"
            }
        
        yeu_cau_tham_gia_phong_in_db = await crud_yeu_cau_tham_gia_phong.get(session, phong_nghe_nhac_id=phong_nghe_nhac_id, nguoi_dung_id=nguoi_dung_id)
        if yeu_cau_tham_gia_phong_in_db:
            if yeu_cau_tham_gia_phong_in_db.trang_thai == "chap_nhan":
                return {
                    "success": False,
                    "message": "Ban da tham gia phong"
                }
            if yeu_cau_tham_gia_phong_in_db.trang_thai == "cho_duyet":
                return {
                    "success": False,
                    "message": "Yeu cau tham gia phong cua ban dang cho duyet"
                }
        
        yeu_cau_tham_gia_phong_new = {
            "trang_thai": "cho_duyet",
            "phong_nghe_nhac_id": phong_nghe_nhac_id,
            "nguoi_dung_id": nguoi_dung_id
        }
        
        yeu_cau_tham_gia_phong_created = await crud_yeu_cau_tham_gia_phong.create(session, obj_in=YeuCauThamGiaPhongCreate(**yeu_cau_tham_gia_phong_new))
        response_data = {
            "id": str(yeu_cau_tham_gia_phong_created.id),
            "trang_thai": yeu_cau_tham_gia_phong_created.trang_thai,
            "phong_nghe_nhac_id": str(yeu_cau_tham_gia_phong_created.phong_nghe_nhac_id),
            "nguoi_dung_id": str(yeu_cau_tham_gia_phong_created.nguoi_dung_id),
            "thoi_gian_tao": str(yeu_cau_tham_gia_phong_created.thoi_gian_tao)
        }
        
        return {
            "success": True,
            "data": response_data
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

    
    
# list yeu cau tham gia phong
@router.get("/xem_yeu_cau_tham_gia_phong/{phong_nghe_nhac_id}")
async def xem_yeu_cau_tham_gia_phong(
    phong_nghe_nhac_id: str,
    session: AsyncSession = Depends(get_session),
    nguoi_dung_hien_tai: dict = Depends(get_nguoi_dung_hien_tai),
):
    """
    Endpoint to get list of request to join a PhongNgheNhac.
    """
    try:
        thanh_vien_phong = await crud_thanh_vien_phong.get(session, phong_nghe_nhac_id=phong_nghe_nhac_id, nguoi_dung_id=nguoi_dung_hien_tai.get("id"))
        if not thanh_vien_phong:
            raise HTTPException(status_code=400, detail="Ban khong phai la thanh vien cua phong")
        
        if thanh_vien_phong.quyen != "chu_phong" and thanh_vien_phong.quyen != "quan_ly":
            raise HTTPException(status_code=400, detail="Ban khong co quyen xem danh sach yeu cau tham gia phong")
        
        yeu_cau_tham_gia_phongs = await crud_yeu_cau_tham_gia_phong.get_multi(session, phong_nghe_nhac_id=phong_nghe_nhac_id)
        
        # add nguoi_dung information to yeu_cau_tham_gia_phongs
        result = []
        
        for yeu_cau_tham_gia_phong in yeu_cau_tham_gia_phongs:
            if yeu_cau_tham_gia_phong.trang_thai == "chap_nhan" or yeu_cau_tham_gia_phong.trang_thai == "tu_choi" or yeu_cau_tham_gia_phong.trang_thai == "da_roi" or yeu_cau_tham_gia_phong.trang_thai == "da_xoa":
                continue
            nguoi_dung = await crud_nguoi_dung.get(session, id=yeu_cau_tham_gia_phong.nguoi_dung_id)

            result.append({
                "id": str(yeu_cau_tham_gia_phong.id),
                "nguoi_dung_id": str(nguoi_dung.id),
                "ho_ten": nguoi_dung.ten_nguoi_dung,
                "anh_dai_dien": nguoi_dung.anh_dai_dien,
                "trang_thai": yeu_cau_tham_gia_phong.trang_thai,
                "phong_nghe_nhac_id": str(yeu_cau_tham_gia_phong.phong_nghe_nhac_id),
                "thoi_gian_tao": str(yeu_cau_tham_gia_phong.thoi_gian_tao)
            })
            
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
# accept yeu cau tham gia phong
@router.put("/cap_nhat_yeu_cau_tham_gia_phong")
async def cap_nhat_yeu_cau_tham_gia_phong( 
    yeu_cau_tham_gia_phong_id: str,
    chap_nhan: bool = True,
    session: AsyncSession = Depends(get_session),
    nguoi_dung_hien_tai: dict = Depends(get_nguoi_dung_hien_tai),
):
    """
    Endpoint to accept a request to join a PhongNgheNhac.
    """
    try:
        yeu_cau_tham_gia_phong = await crud_yeu_cau_tham_gia_phong.get(session, id=yeu_cau_tham_gia_phong_id)
        if not yeu_cau_tham_gia_phong:
            raise HTTPException(status_code=404, detail="Yeu cau tham gia phong khong ton tai")
        
        phong_nghe_nhac = await crud_phong_nghe_nhac.get(session, id=yeu_cau_tham_gia_phong.phong_nghe_nhac_id)
        if not phong_nghe_nhac:
            raise HTTPException(status_code=404, detail="Phong nghe nhac khong ton tai")
        
        thanh_vien_phong = await crud_thanh_vien_phong.get(session, phong_nghe_nhac_id=phong_nghe_nhac.id, nguoi_dung_id=nguoi_dung_hien_tai.get("id"))
        if not thanh_vien_phong:
            raise HTTPException(status_code=400, detail="Ban khong phai la thanh vien cua phong")
        
        if thanh_vien_phong.quyen != "chu_phong" and thanh_vien_phong.quyen != "quan_ly":
            raise HTTPException(status_code=400, detail="Ban khong phai chu phong")
        
        if chap_nhan:
            # create thanh_vien_phong
            thanh_vien_phong_new = {
                "phong_nghe_nhac_id": phong_nghe_nhac.id,
                "nguoi_dung_id": yeu_cau_tham_gia_phong.nguoi_dung_id,
                "quyen": "thanh_vien"
            }
            await crud_thanh_vien_phong.create(session, obj_in=ThanhVienPhongCreate(**thanh_vien_phong_new))
        
        yeu_cau_tham_gia_phong_updated = await crud_yeu_cau_tham_gia_phong.update(
            session,
            obj_in=YeuCauThamGiaPhongUpdateDB(trang_thai="chap_nhan" if chap_nhan else "tu_choi"),
            db_obj=yeu_cau_tham_gia_phong
        )
        
        result = {
            "id": str(yeu_cau_tham_gia_phong_updated.id),
            "trang_thai": yeu_cau_tham_gia_phong_updated.trang_thai,
            "phong_nghe_nhac_id": str(yeu_cau_tham_gia_phong_updated.phong_nghe_nhac_id),
            "nguoi_dung_id": str(yeu_cau_tham_gia_phong_updated.nguoi_dung_id),
            "thoi_gian_tao": str(yeu_cau_tham_gia_phong_updated.thoi_gian_tao)
        }
        
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
async def cap_nhat_yeu_cau_tham_gia_phong_ws( 
    nguoi_dung_id: str,
    yeu_cau_tham_gia_phong_id: str,
    chap_nhan: bool = True,
    session: AsyncSession = Depends(get_session)
):
    """
    Endpoint to accept a request to join a PhongNgheNhac.
    """
    try:
        yeu_cau_tham_gia_phong = await crud_yeu_cau_tham_gia_phong.get(session, id=yeu_cau_tham_gia_phong_id)
        if not yeu_cau_tham_gia_phong:
            return {
                "success": False,
                "message": "Yeu cau tham gia phong khong ton tai"
            }
        
        phong_nghe_nhac = await crud_phong_nghe_nhac.get(session, id=yeu_cau_tham_gia_phong.phong_nghe_nhac_id)
        if not phong_nghe_nhac:
            return {
                "success": False,
                "message": "Phong nghe nhac khong ton tai"
            }
        
        thanh_vien_phong = await crud_thanh_vien_phong.get(session, phong_nghe_nhac_id=phong_nghe_nhac.id, nguoi_dung_id=nguoi_dung_id)
        if not thanh_vien_phong:
            return {
                "success": False,
                "message": "Ban khong phai la thanh vien cua phong"
            }
        
        if thanh_vien_phong.quyen != "chu_phong" and thanh_vien_phong.quyen != "quan_ly":
            return {
                "success": False,
                "message": "Ban khong phai chu phong"
            }
        
        if chap_nhan:
            # create thanh_vien_phong
            thanh_vien_phong_new = {
                "phong_nghe_nhac_id": phong_nghe_nhac.id,
                "nguoi_dung_id": yeu_cau_tham_gia_phong.nguoi_dung_id,
                "quyen": "thanh_vien"
            }
            await crud_thanh_vien_phong.create(session, obj_in=ThanhVienPhongCreate(**thanh_vien_phong_new))
        
        yeu_cau_tham_gia_phong_updated = await crud_yeu_cau_tham_gia_phong.update(
            session,
            obj_in=YeuCauThamGiaPhongUpdateDB(trang_thai="chap_nhan" if chap_nhan else "tu_choi"),
            db_obj=yeu_cau_tham_gia_phong
        )
        
        result = {
            "id": str(yeu_cau_tham_gia_phong_updated.id),
            "trang_thai": yeu_cau_tham_gia_phong_updated.trang_thai,
            "phong_nghe_nhac_id": str(yeu_cau_tham_gia_phong_updated.phong_nghe_nhac_id),
            "nguoi_dung_id": str(yeu_cau_tham_gia_phong_updated.nguoi_dung_id),
            "thoi_gian_tao": str(yeu_cau_tham_gia_phong_updated.thoi_gian_tao)
        }
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }   
    
    
# xem thanh vien phong
@router.get("/thanh_vien_phong/{phong_nghe_nhac_id}")
async def xem_thanh_vien_phong(
    phong_nghe_nhac_id: str,
    session: AsyncSession = Depends(get_session),
    nguoi_dung_hien_tai: dict = Depends(get_nguoi_dung_hien_tai),
):
    """
    Endpoint to get list of members in a PhongNgheNhac.
    """
    try:
        thanh_vien_phongs = await crud_thanh_vien_phong.get_multi(session, phong_nghe_nhac_id=phong_nghe_nhac_id)
        if not thanh_vien_phongs:
            raise HTTPException(status_code=404, detail="Phong nghe nhac khong ton tai")
        
        if not any([thanh_vien_phong.nguoi_dung_id == nguoi_dung_hien_tai.get("id") for thanh_vien_phong in thanh_vien_phongs]):
            raise HTTPException(status_code=400, detail="Ban khong phai la thanh vien cua phong")
        
        result = []
        for thanh_vien_phong in thanh_vien_phongs:
            nguoi_dung = await crud_nguoi_dung.get(session, id=thanh_vien_phong.nguoi_dung_id)
            
            result.append({
                "id": str(thanh_vien_phong.id),
                "nguoi_dung_id": str(nguoi_dung.id),
                "ho_ten": nguoi_dung.ten_nguoi_dung,
                "anh_dai_dien": nguoi_dung.anh_dai_dien,
                "trang_thai": thanh_vien_phong.trang_thai,
                "quyen": thanh_vien_phong.quyen,
                "phong_nghe_nhac_id": str(thanh_vien_phong.phong_nghe_nhac_id),
            })
            
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

# xoa thanh vien phong
@router.delete("/xoa_thanh_vien_phong")
async def xoa_thanh_vien_phong(
    thanh_vien_phong_id: str,
    session: AsyncSession = Depends(get_session),
    nguoi_dung_hien_tai: dict = Depends(get_nguoi_dung_hien_tai),
):
    """
    Endpoint to remove a member from a PhongNgheNhac.
    """
    try:
        # Fetch the ThanhVienPhong instance
        thanh_vien_phong = await crud_thanh_vien_phong.get(session, id=thanh_vien_phong_id)
        if not thanh_vien_phong:
            raise HTTPException(status_code=404, detail="Thanh vien phong khong ton tai")
        
        phong_nghe_nhac = await crud_phong_nghe_nhac.get(session, id=thanh_vien_phong.phong_nghe_nhac_id)
        if not phong_nghe_nhac:
            raise HTTPException(status_code=404, detail="Phong nghe nhac khong ton tai")
        
         # Verify user is a member of the PhongNgheNhac
        thanh_vien_phong_nguoi_dung = await crud_thanh_vien_phong.get(
            session, phong_nghe_nhac_id=phong_nghe_nhac.id, nguoi_dung_id=nguoi_dung_hien_tai.get("id")
        )
        if not thanh_vien_phong_nguoi_dung:
            raise HTTPException(status_code=400, detail="Ban khong phai la thanh vien cua phong")
        
        if thanh_vien_phong_nguoi_dung.quyen != "chu_phong" and thanh_vien_phong_nguoi_dung.quyen != "quan_ly":
            raise HTTPException(status_code=400, detail="Ban khong co quyen xoa thanh vien phong")
        
        if thanh_vien_phong.id == thanh_vien_phong_nguoi_dung.id:
            raise HTTPException(status_code=400, detail="Ban khong the xoa chinh minh khoi phong")
        
        # Delete the ThanhVienPhong instance
        thanh_vien_phong_deleted = await crud_thanh_vien_phong.delete(session, id=thanh_vien_phong_id)
        yeu_cau_tham_gia_phong_db = await crud_yeu_cau_tham_gia_phong.get(session, phong_nghe_nhac_id=phong_nghe_nhac.id, nguoi_dung_id=thanh_vien_phong.nguoi_dung_id)
        # cap nhat yeu cau tham gia phong
        yeu_cau_tham_gia_phong = await crud_yeu_cau_tham_gia_phong.update(
            session,
            obj_in=YeuCauThamGiaPhongUpdateDB(trang_thai="da_xoa"),
            db_obj=yeu_cau_tham_gia_phong_db
        )
        return JSONResponse(status_code=200, content={"message": "Xoa thanh vien phong thanh cong"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
async def xoa_thanh_vien_phong_ws(
    nguoi_dung_id: str,
    thanh_vien_phong_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to remove a member from a PhongNgheNhac.
    """
    try:
        # Fetch the ThanhVienPhong instance
        thanh_vien_phong = await crud_thanh_vien_phong.get(session, id=thanh_vien_phong_id)
        if not thanh_vien_phong:
            return {
                "success": False,
                "message": "Thanh vien phong khong ton tai"
            }
        
        phong_nghe_nhac = await crud_phong_nghe_nhac.get(session, id=thanh_vien_phong.phong_nghe_nhac_id)
        if not phong_nghe_nhac:
            return {
                "success": False,
                "message": "Phong nghe nhac khong ton tai"
            }
        
         # Verify user is a member of the PhongNgheNhac
        thanh_vien_phong_nguoi_dung = await crud_thanh_vien_phong.get(
            session, phong_nghe_nhac_id=phong_nghe_nhac.id, nguoi_dung_id=nguoi_dung_id
        )
        if not thanh_vien_phong_nguoi_dung:
            return {
                "success": False,
                "message": "Ban khong phai la thanh vien cua phong"
            }
        
        if thanh_vien_phong_nguoi_dung.quyen != "chu_phong" and thanh_vien_phong_nguoi_dung.quyen != "quan_ly":
            return {
                "success": False,
                "message": "Ban khong co quyen xoa thanh vien phong"
            }
        
        if thanh_vien_phong.id == thanh_vien_phong_nguoi_dung.id:
            return {
                "success": False,
                "message": "Ban khong the xoa chinh minh khoi phong"
            }
        
        # Delete the ThanhVienPhong instance
        thanh_vien_phong_deleted = await crud_thanh_vien_phong.delete(session, id=thanh_vien_phong_id)
        yeu_cau_tham_gia_phong_db = await crud_yeu_cau_tham_gia_phong.get(session, phong_nghe_nhac_id=phong_nghe_nhac.id, nguoi_dung_id=thanh_vien_phong.nguoi_dung_id)
        # cap nhat yeu cau tham gia phong
        yeu_cau_tham_gia_phong = await crud_yeu_cau_tham_gia_phong.update(
            session,
            obj_in=YeuCauThamGiaPhongUpdateDB(trang_thai="da_xoa"),
            db_obj=yeu_cau_tham_gia_phong_db
        )
        return {
            "success": True,
            "message": "Xoa thanh vien phong thanh cong"
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }
    
    
# roi phong
@router.delete("/roi_phong")
async def roi_phong(
    phong_nghe_nhac_id: str,
    session: AsyncSession = Depends(get_session),
    nguoi_dung_hien_tai: dict = Depends(get_nguoi_dung_hien_tai),
):
    """
    Endpoint to leave a PhongNgheNhac.
    """
    try:
        # Fetch the ThanhVienPhong instance
        phong_nghe_nhac = await crud_phong_nghe_nhac.get(session, id=phong_nghe_nhac_id)
        if not phong_nghe_nhac:
            raise HTTPException(status_code=404, detail="Phong nghe nhac khong ton tai")
        
        thanh_vien_phong = await crud_thanh_vien_phong.get(session, phong_nghe_nhac_id=phong_nghe_nhac_id, nguoi_dung_id=nguoi_dung_hien_tai.get("id"))
        if not thanh_vien_phong:
            raise HTTPException(status_code=404, detail="Ban khong phai la thanh vien cua phong")
        
        if thanh_vien_phong.quyen == "chu_phong":
            # chu phong can chuyen quyen cho thanh vien khac truoc khi roi phong
            quan_lys = await crud_thanh_vien_phong.get_multi(session, phong_nghe_nhac_id=phong_nghe_nhac_id, quyen="quan_ly")
            if not quan_lys:
                thanh_vien_phongs = await crud_thanh_vien_phong.get_multi(session, phong_nghe_nhac_id=phong_nghe_nhac_id, quyen="thanh_vien")
                if not thanh_vien_phongs:
                    await crud_thanh_vien_phong.delete(session, id=thanh_vien_phong.id)
                    await crud_phong_nghe_nhac.delete(session, id=phong_nghe_nhac_id)
                    return JSONResponse(status_code=200, content={"message": "Roi phong thanh cong"})
                else:
                    thanh_vien_phong_updated = {
                        "phong_nghe_nhac_id": phong_nghe_nhac_id,
                        "nguoi_dung_id": thanh_vien_phongs[0].nguoi_dung_id,
                        "quyen": "chu_phong"
                    }
                    await crud_thanh_vien_phong.update(session, obj_in=ThanhVienPhongUpdateDB(**thanh_vien_phong_updated), db_obj=thanh_vien_phongs[0])
            else:
                thanh_vien_phong_updated = {
                    "phong_nghe_nhac_id": phong_nghe_nhac_id,
                    "nguoi_dung_id": quan_lys[0].nguoi_dung_id,
                    "quyen": "chu_phong"
                }
                await crud_thanh_vien_phong.update(session, obj_in=ThanhVienPhongUpdateDB(**thanh_vien_phong_updated), db_obj=quan_lys[0])
        
        # Delete the ThanhVienPhong instance
        thanh_vien_phong_deleted = await crud_thanh_vien_phong.delete(session, id=thanh_vien_phong.id)
        
        # cap nhat yeu cau tham gia phong
        yeu_cau_tham_gia_phong_db = await crud_yeu_cau_tham_gia_phong.get(session, phong_nghe_nhac_id=phong_nghe_nhac.id, nguoi_dung_id=nguoi_dung_hien_tai.get("id"))
        if yeu_cau_tham_gia_phong_db:
            yeu_cau_tham_gia_phong = await crud_yeu_cau_tham_gia_phong.update(
                session,
                obj_in=YeuCauThamGiaPhongUpdateDB(trang_thai="da_roi"),
                db_obj=yeu_cau_tham_gia_phong_db
            )
        return JSONResponse(status_code=200, content={"message": "Roi phong thanh cong"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
async def roi_phong_ws(
    nguoi_dung_id: str,
    phong_nghe_nhac_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Endpoint to leave a PhongNgheNhac.
    """
    try:
        # Fetch the ThanhVienPhong instance
        phong_nghe_nhac = await crud_phong_nghe_nhac.get(session, id=phong_nghe_nhac_id)
        if not phong_nghe_nhac:
            return {
                "success": False,
                "message": "Phong nghe nhac khong ton tai"
            }
        
        thanh_vien_phong = await crud_thanh_vien_phong.get(session, phong_nghe_nhac_id=phong_nghe_nhac_id, nguoi_dung_id=nguoi_dung_id)
        if not thanh_vien_phong:
            return {
                "success": False,
                "message": "Ban khong phai la thanh vien cua phong"
            }
        
        if thanh_vien_phong.quyen == "chu_phong":
            # chu phong can chuyen quyen cho thanh vien khac truoc khi roi phong
            quan_lys = await crud_thanh_vien_phong.get_multi(session, phong_nghe_nhac_id=phong_nghe_nhac_id, quyen="quan_ly")
            if not quan_lys:
                thanh_vien_phongs = await crud_thanh_vien_phong.get_multi(session, phong_nghe_nhac_id=phong_nghe_nhac_id, quyen="thanh_vien")
                if not thanh_vien_phongs:
                    await crud_thanh_vien_phong.delete(session, id=thanh_vien_phong.id)
                    await crud_phong_nghe_nhac.delete(session, id=phong_nghe_nhac_id)
                    return {
                        "success": True,
                        "message": "Roi phong thanh cong"
                    }
                else:
                    thanh_vien_phong_updated = {
                        "phong_nghe_nhac_id": phong_nghe_nhac_id,
                        "nguoi_dung_id": thanh_vien_phongs[0].nguoi_dung_id,
                        "quyen": "chu_phong"
                    }
                    await crud_thanh_vien_phong.update(session, obj_in=ThanhVienPhongUpdateDB(**thanh_vien_phong_updated), db_obj=thanh_vien_phongs[0])
            else:
                thanh_vien_phong_updated = {
                    "phong_nghe_nhac_id": phong_nghe_nhac_id,
                    "nguoi_dung_id": quan_lys[0].nguoi_dung_id,
                    "quyen": "chu_phong"
                }
                await crud_thanh_vien_phong.update(session, obj_in=ThanhVienPhongUpdateDB(**thanh_vien_phong_updated), db_obj=quan_lys[0])
        
        # Delete the ThanhVienPhong instance
        thanh_vien_phong_deleted = await crud_thanh_vien_phong.delete(session, id=thanh_vien_phong.id)
        
        # cap nhat yeu cau tham gia phong
        yeu_cau_tham_gia_phong_db = await crud_yeu_cau_tham_gia_phong.get(session, phong_nghe_nhac_id=phong_nghe_nhac.id, nguoi_dung_id=nguoi_dung_id)
        if yeu_cau_tham_gia_phong_db:
            yeu_cau_tham_gia_phong = await crud_yeu_cau_tham_gia_phong.update(
                session,
                obj_in=YeuCauThamGiaPhongUpdateDB(trang_thai="da_roi"),
                db_obj=yeu_cau_tham_gia_phong_db
            )
        return {
            "success": True,
            "message": "Roi phong thanh cong"
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }
    
    
# cap nhap quyen thanh vien phong
@router.put("/cap_nhat_quyen_thanh_vien_phong")
async def cap_nhat_quyen_thanh_vien_phong(
    thanh_vien_phong_id: str,
    quyen: str,
    session: AsyncSession = Depends(get_session),
    nguoi_dung_hien_tai: dict = Depends(get_nguoi_dung_hien_tai),
):
    """
    Endpoint to update a member's role in a PhongNgheNhac.
    """
    try:
        # Fetch the ThanhVienPhong instance
        thanh_vien_phong = await crud_thanh_vien_phong.get(session, id=thanh_vien_phong_id)
        if not thanh_vien_phong:
            raise HTTPException(status_code=404, detail="Thanh vien phong khong ton tai")
        
        phong_nghe_nhac = await crud_phong_nghe_nhac.get(session, id=thanh_vien_phong.phong_nghe_nhac_id)
        if not phong_nghe_nhac:
            raise HTTPException(status_code=404, detail="Phong nghe nhac khong ton tai")
        
        # Verify user is a member of the PhongNgheNhac
        thanh_vien_phong_nguoi_dung = await crud_thanh_vien_phong.get(
            session, phong_nghe_nhac_id=phong_nghe_nhac.id, nguoi_dung_id=nguoi_dung_hien_tai.get("id")
        )
        
        if thanh_vien_phong.id == thanh_vien_phong_nguoi_dung.id:
            raise HTTPException(status_code=400, detail="Ban khong the cap nhat quyen cua chinh minh")
        
        if not thanh_vien_phong_nguoi_dung:
            raise HTTPException(status_code=400, detail="Ban khong phai la thanh vien cua phong")
        
        if thanh_vien_phong_nguoi_dung.quyen != "chu_phong" and thanh_vien_phong_nguoi_dung.quyen != "quan_ly":
            raise HTTPException(status_code=400, detail="Ban khong co quyen cap nhat quyen thanh vien phong")
        
        if thanh_vien_phong_nguoi_dung.quyen == "quan_ly" and quyen == "chu_phong":
            raise HTTPException(status_code=400, detail="Quan ly co quyen cap nhat quyen thanh vien phong len chu phong")
        
        # Update the ThanhVienPhong instance
        thanh_vien_phong_data = {
            "phong_nghe_nhac_id": phong_nghe_nhac.id,
            "nguoi_dung_id": thanh_vien_phong.nguoi_dung_id,
            "quyen": quyen
        }
        thanh_vien_phong_updated = await crud_thanh_vien_phong.update(
            session, obj_in=ThanhVienPhongUpdateDB(**thanh_vien_phong_data), db_obj=thanh_vien_phong
        )
        
        result = {
            "id": str(thanh_vien_phong_updated.id),
            "phong_nghe_nhac_id": str(thanh_vien_phong_updated.phong_nghe_nhac_id),
            "nguoi_dung_id": str(thanh_vien_phong_updated.nguoi_dung_id),
            "quyen": thanh_vien_phong_updated.quyen,
            "trang_thai": thanh_vien_phong_updated.trang_thai,
            "thoi_gian_tao": str(thanh_vien_phong_updated.thoi_gian_tao),
            "thoi_gian_cap_nhat": str(thanh_vien_phong_updated.thoi_gian_cap_nhat)
        }
        
        return JSONResponse(status_code=200, content=result)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
async def cap_nhat_quyen_thanh_vien_phong_ws(
    nguoi_dung_id: str,
    thanh_vien_phong_id: str,
    quyen: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to update a member's role in a PhongNgheNhac.
    """
    try:
        # Fetch the ThanhVienPhong instance
        thanh_vien_phong = await crud_thanh_vien_phong.get(session, id=thanh_vien_phong_id)
        if not thanh_vien_phong:
            return {
                "success": False,
                "message": "Thanh vien phong khong ton tai"
            }
        
        phong_nghe_nhac = await crud_phong_nghe_nhac.get(session, id=thanh_vien_phong.phong_nghe_nhac_id)
        if not phong_nghe_nhac:
            return {
                "success": False,
                "message": "Phong nghe nhac khong ton tai"
            }
        
        # Verify user is a member of the PhongNgheNhac
        thanh_vien_phong_nguoi_dung = await crud_thanh_vien_phong.get(
            session, phong_nghe_nhac_id=phong_nghe_nhac.id, nguoi_dung_id=nguoi_dung_id
        )
        
        if thanh_vien_phong.id == thanh_vien_phong_nguoi_dung.id:
            return {
                "success": False,
                "message": "Ban khong the cap nhat quyen cua chinh minh"
            }
        
        if not thanh_vien_phong_nguoi_dung:
            return {
                "success": False,
                "message": "Ban khong phai la thanh vien cua phong"
            }            
        
        if thanh_vien_phong_nguoi_dung.quyen != "chu_phong" and thanh_vien_phong_nguoi_dung.quyen != "quan_ly":
            return {
                "success": False,
                "message": "Ban khong co quyen cap nhat quyen thanh vien phong"
            }
        
        if thanh_vien_phong_nguoi_dung.quyen == "quan_ly" and quyen == "chu_phong":
            return {
                "success": False,
                "message": "Quan ly co quyen cap nhat quyen thanh vien phong len chu phong"
            }
        
        # Update the ThanhVienPhong instance
        thanh_vien_phong_data = {
            "phong_nghe_nhac_id": phong_nghe_nhac.id,
            "nguoi_dung_id": thanh_vien_phong.nguoi_dung_id,
            "quyen": quyen
        }
        thanh_vien_phong_updated = await crud_thanh_vien_phong.update(
            session, obj_in=ThanhVienPhongUpdateDB(**thanh_vien_phong_data), db_obj=thanh_vien_phong
        )
        
        result = {
            "id": str(thanh_vien_phong_updated.id),
            "phong_nghe_nhac_id": str(thanh_vien_phong_updated.phong_nghe_nhac_id),
            "nguoi_dung_id": str(thanh_vien_phong_updated.nguoi_dung_id),
            "quyen": thanh_vien_phong_updated.quyen,
            "trang_thai": thanh_vien_phong_updated.trang_thai,
            "thoi_gian_tao": str(thanh_vien_phong_updated.thoi_gian_tao),
            "thoi_gian_cap_nhat": str(thanh_vien_phong_updated.thoi_gian_cap_nhat)
        }
        
        return {
            "success": True,
            "data": result
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }
    