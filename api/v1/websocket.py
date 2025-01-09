from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List, Dict
from services.websocket.manager import manager as connection_manager

from schemas.bai_hat import BaiHatCreate, BaiHatUpdateDB
from schemas.phong_nghe_nhac import PhongNgheNhacCreate, PhongNgheNhacUpdateDB
from schemas.danh_sach_phat import DanhSachPhatCreate, DanhSachPhatUpdateDB
from schemas.thanh_vien_phong import ThanhVienPhongCreate, ThanhVienPhongUpdateDB
from schemas.danh_sach_phat_bai_hat import DanhSachPhatBaiHatCreate, DanhSachPhatBaiHatUpdateDB
from schemas.tin_nhan import TinNhanCreate, TinNhanUpdateDB

from services.crud.bai_hat import crud_bai_hat
from services.crud.nguoi_dung import crud_nguoi_dung
from services.crud.phong_nghe_nhac import crud_phong_nghe_nhac
from services.crud.danh_sach_phat import crud_danh_sach_phat
from services.crud.thanh_vien_phong import crud_thanh_vien_phong
from services.crud.danh_sach_phat_bai_hat import crud_danh_sach_phat_bai_hat
from services.crud.tin_nhan import crud_tin_nhan
from api.deps import get_session, get_nguoi_dung_hien_tai_websocket
from api.v1.danh_sach_phat import them_bai_hat_vao_danh_sach_phat, cap_nhat_so_thu_tu_cua_bai_hat_trong_danh_sach_phat, xoa_bai_hat_khoi_danh_sach_phat_ws, xem_danh_sach_bai_hat_trong_danh_sach_phat
from api.v1.phong_nghe_nhac import xoa_thanh_vien_phong_ws, roi_phong_ws, cap_nhat_quyen_thanh_vien_phong_ws, yeu_cau_tham_gia_phong_ws, cap_nhat_yeu_cau_tham_gia_phong_ws

router = APIRouter(prefix="/websocket", tags=["WebSocket"])

@router.websocket("/request_to_join_room/{room_id}")
async def request_to_join_room(
    websocket: WebSocket,
    room_id: str,
    nguoi_dung_hien_tai: dict = Depends(get_nguoi_dung_hien_tai_websocket),
    session=Depends(get_session)
):
    if nguoi_dung_hien_tai is None:
        await websocket.close(code=1008)
        return {"message": "Unauthorized"}
    
    result = await yeu_cau_tham_gia_phong_ws(phong_nghe_nhac_id=room_id, nguoi_dung_id=nguoi_dung_hien_tai['id'], session=session)
    
    if not result['success']:
        await websocket.close()
        return result
    
    await connection_manager.connect(room_id, websocket)
    # send message to all members in the room
    print('result', result)
    await connection_manager.broadcast(
        {
            "type": "yeu_cau_tham_gia_phong",
            "action": "yeu_cau_tham_gia_phong",
            "data": {
                "nguoi_dung_id": str(nguoi_dung_hien_tai['id']),
                "yen_cau_tham_gia_id": str(result['data']['id']),
                "anh_dai_dien": nguoi_dung_hien_tai['anh_dai_dien'],
                "ten_nguoi_dung": nguoi_dung_hien_tai['ten_nguoi_dung'],
                "trang_thai": 'cho_duyet'
            }
        },
        room_id
    )
    await connection_manager.disconnect(room_id, websocket)
    return result
    
    

@router.websocket("/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    nguoi_dung_hien_tai: dict = Depends(get_nguoi_dung_hien_tai_websocket),
    session=Depends(get_session)
):
    """
    WebSocket endpoint cho một phòng nhất định
    """
    if nguoi_dung_hien_tai is None:
        await websocket.close(code=1008)
        return {"message": "Unauthorized"}

    phong_nghe_nhac = await crud_phong_nghe_nhac.get(session, id=room_id)
    if phong_nghe_nhac is None:
        await websocket.close()
        return {"message": "Room not found"}
    
    phong_nghe_nhac_dict = {
        "id": str(phong_nghe_nhac.id),
        "ten_phong": phong_nghe_nhac.ten_phong,
        "trang_thai_phat": phong_nghe_nhac.trang_thai_phat,
        "thoi_gian_hien_tai_bai_hat": phong_nghe_nhac.thoi_gian_hien_tai_bai_hat,
        "so_thu_tu_bai_hat_dang_phat": phong_nghe_nhac.so_thu_tu_bai_hat_dang_phat,
        "danh_sach_phat_id": str(phong_nghe_nhac.danh_sach_phat_id),
        "thoi_gian_cap_nhat": str(phong_nghe_nhac.thoi_gian_cap_nhat)
    }

    danh_sach_phat = await crud_danh_sach_phat.get(session, id=phong_nghe_nhac.danh_sach_phat_id)
    
    thanh_vien_phong = await crud_thanh_vien_phong.get(session, phong_nghe_nhac_id=room_id, nguoi_dung_id=nguoi_dung_hien_tai['id'])
    if thanh_vien_phong is None:
        await websocket.close()
        return {"message": "Unauthorized"}
    
    thanh_vien_phong_update_data = {
        'phong_nghe_nhac_id': room_id,
        'nguoi_dung_id': nguoi_dung_hien_tai['id'],
        'trang_thai': 'DangThamGia'
    }
    # update trang thai thanh Dang Tham Gia
    await crud_thanh_vien_phong.update(session, db_obj=thanh_vien_phong, obj_in=ThanhVienPhongUpdateDB(**thanh_vien_phong_update_data))
    
    tat_ca_thanh_vien = await crud_thanh_vien_phong.get_multi(session, phong_nghe_nhac_id=room_id)
    # sort cac_thanh_vien_khac theo trang thai
    tat_ca_thanh_vien = sorted(tat_ca_thanh_vien, key=lambda x: x.trang_thai)
    tat_ca_thanh_vien_data = []
    
    for tv in tat_ca_thanh_vien:
        nguoi_dung = await crud_nguoi_dung.get(session, id=tv.nguoi_dung_id)
        tat_ca_thanh_vien_data.append({
            "id": str(tv.id),
            "ho_ten": nguoi_dung.ten_nguoi_dung,
            "avatar": nguoi_dung.anh_dai_dien,
            "trang_thai": tv.trang_thai,
            "quyen": tv.quyen
        })
    

    try:
        await connection_manager.connect(room_id, websocket)
        # send message to all members in the room
        await connection_manager.broadcast(
            {
                "type": "thanh_vien_phong",
                "action": "tham_gia_phien",
                "data": {
                    "thanh_vien_vua_tham_gia": {
                        "id": str(thanh_vien_phong.id),
                        "ho_ten": nguoi_dung_hien_tai['ten_nguoi_dung'],
                        "avatar": nguoi_dung_hien_tai['anh_dai_dien'],
                        "trang_thai": 'DangThamGia',
                        "quyen": thanh_vien_phong.quyen
                    },
                    "tat_ca_thanh_vien": tat_ca_thanh_vien_data,
                    "phong_nghe_nhac": phong_nghe_nhac_dict
                }
            },
            room_id
        )
        
        while True:
            # receive data from WebSocket
            data = await websocket.receive_json()
            # switch action
            type = data.get('type')
            
            # handle different actions
            if type == 'thanh_vien_phong':
                if data.get('action') == 'roi_phien':
                    # check if the user is current user
                    if data.get('data').get('thanh_vien_vua_roi_phien').get('id') == str(thanh_vien_phong.id):
                        # update trang thai thanh Roi Phien
                        thanh_vien_phong_update_data = {
                            'phong_nghe_nhac_id': room_id,
                            'nguoi_dung_id': nguoi_dung_hien_tai['id'],
                            'trang_thai': 'HoatDong'
                        }
                        await crud_thanh_vien_phong.update(session, db_obj=thanh_vien_phong, obj_in=ThanhVienPhongUpdateDB(**thanh_vien_phong_update_data))
                        tat_ca_thanh_vien = await crud_thanh_vien_phong.get_multi(session, phong_nghe_nhac_id=room_id)
                        # sort cac_thanh_vien_khac theo trang thai
                        tat_ca_thanh_vien = sorted(tat_ca_thanh_vien, key=lambda x: x.trang_thai)
                        tat_ca_thanh_vien_data = []
                        
                        for tv in tat_ca_thanh_vien:
                            nguoi_dung = await crud_nguoi_dung.get(session, id=tv.nguoi_dung_id)
                            tat_ca_thanh_vien_data.append({
                                "id": str(tv.id),
                                "ho_ten": nguoi_dung.ten_nguoi_dung,
                                "avatar": nguoi_dung.anh_dai_dien,
                                "trang_thai": tv.trang_thai,
                                "quyen": tv.quyen
                            })
                        # send message to all members in the room
                        await connection_manager.broadcast({
                            "type": "thanh_vien_phong",
                            "action": "thanh_vien_roi_phien",
                            "data": {
                                "thanh_vien_vua_roi_phien": {
                                    "id": str(thanh_vien_phong.id),
                                    "ho_ten": nguoi_dung_hien_tai['ten_nguoi_dung'],
                                    "avatar": nguoi_dung_hien_tai['anh_dai_dien'],
                                    "trang_thai": 'HoatDong',
                                    "quyen": thanh_vien_phong.quyen
                                },
                                "tat_ca_thanh_vien": tat_ca_thanh_vien_data,
                            }
                        },
                        room_id)
                        # await websocket.close()
                        await connection_manager.disconnect(room_id, websocket)
                    else:
                        pass
                pass
            elif type == 'tin_nhan':
                if data.get('action') == 'gui_tin_nhan':
                    # check if the user is current user
                    if data.get('data').get('thanh_vien_phong_id') == str(thanh_vien_phong.id):
                        tin_nhan_data = {
                            "noi_dung": data.get('data').get('noi_dung'),
                            "tin_nhan_tra_loi_id": data.get('data').get('tin_nhan_tra_loi_id') if data.get('data').get('tin_nhan_tra_loi_id') else None,
                            "thanh_vien_phong_id": thanh_vien_phong.id,
                            "phong_nghe_nhac_id": room_id
                        }
                        # send message to all members in the room
                        tin_nhan_created = await crud_tin_nhan.create(session, obj_in=TinNhanCreate(**tin_nhan_data))
                        await connection_manager.broadcast({
                            "type": "tin_nhan",
                            "action": "nhan_tin_nhan",
                            "data": {
                                "thanh_vien_phong_id": str(thanh_vien_phong.id),
                                "noi_dung": data.get('data').get('noi_dung'),
                                "tin_nhan_tra_loi_id": data.get('data').get('tin_nhan_tra_loi_id') if data.get('data').get('tin_nhan_tra_loi_id') else None,
                                "thoi_gian_tao": str(tin_nhan_created.thoi_gian_tao),
                                "phong_nghe_nhac_id": room_id
                            }
                        }, room_id)

                    else:
                        pass
                pass
            elif type == 'danh_sach_phat':
                if data.get('action') == 'them_bai_hat':
                    if data.get('data').get('thanh_vien_phong_id') == str(thanh_vien_phong.id):
                        bai_hat = await crud_bai_hat.get(session, id=data.get('data').get('bai_hat_id'))

                        await them_bai_hat_vao_danh_sach_phat(str(danh_sach_phat.id), str(bai_hat.id), session)
                        danh_sach_phat_bai_hat_data = await xem_danh_sach_bai_hat_trong_danh_sach_phat(str(danh_sach_phat.id), session)
                        
                        danh_sach_phat_bai_hat_data_dict = []
                        for bai_hat in danh_sach_phat_bai_hat_data:
                            danh_sach_phat_bai_hat_data_dict.append({
                                "id": str(bai_hat['id']),
                                "ten_bai_hat": bai_hat['ten_bai_hat'],
                                "anh": bai_hat['anh'],
                                "ten_ca_si": bai_hat['ten_ca_si'],
                                "the_loai": bai_hat['the_loai'],
                                "mo_ta": bai_hat['mo_ta'],
                                "loi_bai_hat": bai_hat['loi_bai_hat'],
                                "thoi_luong": bai_hat['thoi_luong'],
                                "lien_ket": bai_hat['lien_ket'],
                                "trang_thai": bai_hat['trang_thai'],
                                "quyen_rieng_tu": bai_hat['quyen_rieng_tu'],
                                "thoi_gian_tao": str(bai_hat['thoi_gian_tao']),
                                "thoi_gian_cap_nhat": str(bai_hat['thoi_gian_cap_nhat']),
                                "thoi_gian_xoa": str(bai_hat['thoi_gian_xoa']),
                                "nguoi_dung_id": bai_hat['nguoi_dung_id'],
                                "so_thu_tu": bai_hat['so_thu_tu']
                            })
                        # send message to all members in the room
                        await connection_manager.broadcast({
                            "type": "danh_sach_phat",
                            "action": "cap_nhat_danh_sach_phat",
                            "data": {
                                "danh_sach_phat_bai_hat": danh_sach_phat_bai_hat_data_dict
                            }
                        }, room_id)
                elif data.get('action') == 'xoa_bai_hat':
                    if data.get('data').get('thanh_vien_phong_id') == str(thanh_vien_phong.id):
                        rs = await xoa_bai_hat_khoi_danh_sach_phat_ws(str(danh_sach_phat.id), int(data.get('data').get('so_thu_tu')), session)
                        if rs == 1:
                            danh_sach_phat_bai_hat_data = await xem_danh_sach_bai_hat_trong_danh_sach_phat(str(danh_sach_phat.id), session)
                            # send message to all members in the room
                            danh_sach_phat_bai_hat_data_dict = []
                            for bai_hat in danh_sach_phat_bai_hat_data:
                                danh_sach_phat_bai_hat_data_dict.append({
                                    "id": str(bai_hat['id']),
                                    "ten_bai_hat": bai_hat['ten_bai_hat'],
                                    "anh": bai_hat['anh'],
                                    "ten_ca_si": bai_hat['ten_ca_si'],
                                    "the_loai": bai_hat['the_loai'],
                                    "mo_ta": bai_hat['mo_ta'],
                                    "loi_bai_hat": bai_hat['loi_bai_hat'],
                                    "thoi_luong": bai_hat['thoi_luong'],
                                    "lien_ket": bai_hat['lien_ket'],
                                    "trang_thai": bai_hat['trang_thai'],
                                    "quyen_rieng_tu": bai_hat['quyen_rieng_tu'],
                                    "thoi_gian_tao": str(bai_hat['thoi_gian_tao']),
                                    "thoi_gian_cap_nhat": str(bai_hat['thoi_gian_cap_nhat']),
                                    "thoi_gian_xoa": str(bai_hat['thoi_gian_xoa']),
                                    "nguoi_dung_id": bai_hat['nguoi_dung_id'],
                                    "so_thu_tu": bai_hat['so_thu_tu']
                                })
                            await connection_manager.broadcast({
                                "type": "danh_sach_phat",
                                "action": "cap_nhat_danh_sach_phat",
                                "data": {
                                    "danh_sach_phat_bai_hat": danh_sach_phat_bai_hat_data_dict
                                }
                            }, room_id)
                elif data.get('action') == 'cap_nhat_so_thu_tu':
                    if data.get('data').get('thanh_vien_phong_id') == str(thanh_vien_phong.id):
                        await cap_nhat_so_thu_tu_cua_bai_hat_trong_danh_sach_phat(str(danh_sach_phat.id), str(data.get('data').get('bai_hat_id')), (data.get('data').get('so_thu_tu_cu')), int(data.get('data').get('so_thu_tu_moi')), session)
                        danh_sach_phat_bai_hat_data = await xem_danh_sach_bai_hat_trong_danh_sach_phat(str(danh_sach_phat.id), session)
                        # send message to all members in the room
                        danh_sach_phat_bai_hat_data_dict = []
                        for bai_hat in danh_sach_phat_bai_hat_data:
                            danh_sach_phat_bai_hat_data_dict.append({
                                "id": str(bai_hat['id']),
                                "ten_bai_hat": bai_hat['ten_bai_hat'],
                                "anh": bai_hat['anh'],
                                "ten_ca_si": bai_hat['ten_ca_si'],
                                "the_loai": bai_hat['the_loai'],
                                "mo_ta": bai_hat['mo_ta'],
                                "loi_bai_hat": bai_hat['loi_bai_hat'],
                                "thoi_luong": bai_hat['thoi_luong'],
                                "lien_ket": bai_hat['lien_ket'],
                                "trang_thai": bai_hat['trang_thai'],
                                "quyen_rieng_tu": bai_hat['quyen_rieng_tu'],
                                "thoi_gian_tao": str(bai_hat['thoi_gian_tao']),
                                "thoi_gian_cap_nhat": str(bai_hat['thoi_gian_cap_nhat']),
                                "thoi_gian_xoa": str(bai_hat['thoi_gian_xoa']),
                                "nguoi_dung_id": bai_hat['nguoi_dung_id'],
                                "so_thu_tu": bai_hat['so_thu_tu']
                            })
                        await connection_manager.broadcast({
                            "type": "danh_sach_phat",
                            "action": "cap_nhat_danh_sach_phat",
                            "data": {
                                "danh_sach_phat_bai_hat": danh_sach_phat_bai_hat_data_dict
                            }
                        }, room_id)
            elif type == 'trang_thai_phat':
                if data.get('action') == 'phat_bai_hat':
                    if data.get('data').get('thanh_vien_phong_id') == str(thanh_vien_phong.id):
                        # send message to all members in the room
                        await connection_manager.broadcast({
                            "type": "trang_thai_phat",
                            "action": "cap_nhat_trang_thai_phat",
                            "data": {
                                "thanh_vien_phong_id": str(thanh_vien_phong.id),
                                "trang_thai_phat": 'DangPhat',
                                "bai_hat_id": data.get('data').get('bai_hat_id'),
                                "so_thu_tu": data.get('data').get('so_thu_tu'),
                                "thoi_gian_bat_dau": data.get('data').get('thoi_gian_bat_dau')
                            }
                        }, room_id)
                        
                        phong_nghe_nhac_update_data = {
                            'trang_thai_phat': 'DangPhat',
                            'thoi_gian_hien_tai_bai_hat': data.get('data').get('thoi_gian_bat_dau'),
                            'so_thu_tu_bai_hat_dang_phat': data.get('data').get('so_thu_tu')
                        }
                        await crud_phong_nghe_nhac.update(session, db_obj=phong_nghe_nhac, obj_in=PhongNgheNhacUpdateDB(**phong_nghe_nhac_update_data))
                elif data.get('action') == 'dung_phat':
                    if data.get('data').get('thanh_vien_phong_id') == str(thanh_vien_phong.id):
                        # send message to all members in the room
                        await connection_manager.broadcast({
                            "type": "trang_thai_phat",
                            "action": "cap_nhat_trang_thai_phat",
                            "data": {
                                "thanh_vien_phong_id": str(thanh_vien_phong.id),
                                "trang_thai_phat": 'DungPhat',
                                "bai_hat_id": data.get('data').get('bai_hat_id'),
                                "so_thu_tu": data.get('data').get('so_thu_tu'),
                                "thoi_gian_ket_thuc": data.get('data').get('thoi_gian_ket_thuc')
                            }
                        }, room_id)
                        
                        phong_nghe_nhac_update_data = {
                            'trang_thai_phat': 'DungPhat',
                            'thoi_gian_hien_tai_bai_hat': data.get('data').get('thoi_gian_ket_thuc'),
                            'so_thu_tu_bai_hat_dang_phat': data.get('data').get('so_thu_tu')
                        }
                        await crud_phong_nghe_nhac.update(session, db_obj=phong_nghe_nhac, obj_in=PhongNgheNhacUpdateDB(**phong_nghe_nhac_update_data))
                pass
            elif type == 'yeu_cau_tham_gia_phong':
                if data.get('action') == 'xu_ly_yeu_cau_tham_gia_phong':
                    
                    result = await cap_nhat_yeu_cau_tham_gia_phong_ws(str(nguoi_dung_hien_tai['id']), data.get('data').get('yeu_cau_tham_gia_phong_id'), data.get('data').get('trang_thai'), session)
                    
                    await connection_manager.broadcast({
                        "type": "yeu_cau_tham_gia_phong",
                        "action": "yeu_cau_da_duoc_xu_ly",
                        "data": {
                            "yeu_cau_tham_gia_phong_id": data.get('data').get('yeu_cau_tham_gia_phong_id'),
                            "trang_thai": result['data']['trang_thai']
                        }
                    }, room_id)
                    
                    pass
            elif type == 'cap_nhat_quyen_thanh_vien':
                if data.get('action') == 'cap_nhat_quyen_thanh_vien':
                    result = await cap_nhat_quyen_thanh_vien_phong_ws(str(nguoi_dung_hien_tai['id']), data.get('data').get('thanh_vien_phong_id'), data.get('data').get('quyen_moi'), session)

                    if result['success']:
                        await connection_manager.broadcast({
                            "type": "cap_nhat_quyen_thanh_vien",
                            "action": "quyen_thanh_vien_da_duoc_cap_nhat",
                            "data": {
                                "thanh_vien_phong_id": data.get('data').get('thanh_vien_phong_id'),
                                "quyen_moi": result['message']['data']['quyen']
                            }
                        }, room_id)
                    pass
            elif type == 'roi_phong':
                if data.get('action') == 'roi_phong':
                    result = await roi_phong_ws(str(nguoi_dung_hien_tai['id']), room_id, session)
                    
                    if result['success']:
                        tat_ca_thanh_vien = await crud_thanh_vien_phong.get_multi(session, phong_nghe_nhac_id=room_id)
                        # sort cac_thanh_vien_khac theo trang thai
                        tat_ca_thanh_vien = sorted(tat_ca_thanh_vien, key=lambda x: x.trang_thai)
                        tat_ca_thanh_vien_data = []
                        
                        for tv in tat_ca_thanh_vien:
                            nguoi_dung = await crud_nguoi_dung.get(session, id=tv.nguoi_dung_id)
                            tat_ca_thanh_vien_data.append({
                                "id": str(tv.id),
                                "ho_ten": nguoi_dung.ten_nguoi_dung,
                                "avatar": nguoi_dung.anh_dai_dien,
                                "trang_thai": tv.trang_thai,
                                "quyen": tv.quyen
                            })
                        await connection_manager.broadcast({
                            "type": "roi_phong",
                            "action": "thanh_vien_roi_phong",
                            "data": {
                                "thanh_vien_vua_roi_phong": {
                                    "id": str(thanh_vien_phong.id),
                                    "ho_ten": nguoi_dung_hien_tai['ten_nguoi_dung'],
                                    "avatar": nguoi_dung_hien_tai['anh_dai_dien'],
                                    "quyen": thanh_vien_phong.quyen
                                },
                                "tat_ca_thanh_vien": tat_ca_thanh_vien_data
                            }
                        }, room_id)
                        await connection_manager.disconnect(room_id, websocket)
                    pass
            elif type == 'xoa_thanh_vien_phong':
                if data.get('action') == 'xoa_thanh_vien_phong':
                    result = await xoa_thanh_vien_phong_ws(str(nguoi_dung_hien_tai['id']), data.get('data').get('thanh_vien_phong_id'), session)
                    
                    if result['success']:
                        tat_ca_thanh_vien = await crud_thanh_vien_phong.get_multi(session, phong_nghe_nhac_id=room_id)
                        # sort cac_thanh_vien_khac theo trang thai
                        tat_ca_thanh_vien = sorted(tat_ca_thanh_vien, key=lambda x: x.trang_thai)
                        tat_ca_thanh_vien_data = []
                        
                        for tv in tat_ca_thanh_vien:
                            nguoi_dung = await crud_nguoi_dung.get(session, id=tv.nguoi_dung_id)
                            tat_ca_thanh_vien_data.append({
                                "id": str(tv.id),
                                "ho_ten": nguoi_dung.ten_nguoi_dung,
                                "avatar": nguoi_dung.anh_dai_dien,
                                "trang_thai": tv.trang_thai,
                                "quyen": tv.quyen
                            })
                        await connection_manager.broadcast({
                            "type": "xoa_thanh_vien_phong",
                            "action": "thanh_vien_da_bi_xoa",
                            "data": {
                                "thanh_vien_vua_bi_xoa": {
                                    "id": str(data.get('data').get('thanh_vien_phong_id'))
                                },
                                "tat_ca_thanh_vien": tat_ca_thanh_vien_data
                            }
                        }, room_id)
                    pass
            else:
                await connection_manager.broadcast(data, room_id)
                    
    except WebSocketDisconnect:
        connection_manager.broadcast(
            {
                "type": "thanh_vien_phong",
                "action": "roi_phien",
                "data": {
                    "thanh_vien_vua_roi_phien": {
                        "id": str(thanh_vien_phong.id),
                        "ho_ten": nguoi_dung_hien_tai['ten_nguoi_dung'],
                        "avatar": nguoi_dung_hien_tai['anh_dai_dien'],
                        "trang_thai": 'HoatDong',
                        "quyen": thanh_vien_phong.quyen
                    }
                }
            }, room_id
        )
        
        await connection_manager.disconnect(room_id, websocket)
        # update trang thai thanh Hoat Dong
        thanh_vien_phong_update_data = {
            'phong_nghe_nhac_id': room_id,
            'nguoi_dung_id': nguoi_dung_hien_tai['id'],
            'trang_thai': 'HoatDong'
        }
        await crud_thanh_vien_phong.update(session, db_obj=thanh_vien_phong, obj_in=ThanhVienPhongUpdateDB(**thanh_vien_phong_update_data))
        await websocket.close()
        