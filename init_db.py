"""
This module initializes the database for the FastAPI application.
It creates the database if it doesn't exist,
creates tables, and seeds the database with initial data using JSON files.
"""

import os
import json
import asyncio
import logging
from logging.handlers import RotatingFileHandler
import secrets
from datetime import datetime, timedelta
from sqlalchemy_utils import database_exists, create_database

from config.database import database
from config.config import settings
from models.base import Base

from schemas.nguoi_dung import NguoiDungCreate
from schemas.danh_sach_phat import DanhSachPhatCreate
from schemas.bai_hat import BaiHatCreate
from schemas.danh_sach_phat_bai_hat import DanhSachPhatBaiHatCreate

from services.crud.nguoi_dung import crud_nguoi_dung
from services.crud.danh_sach_phat import crud_danh_sach_phat
from services.crud.bai_hat import crud_bai_hat
from services.crud.danh_sach_phat_bai_hat import crud_danh_sach_phat_bai_hat

# Logging Configuration
LOG_DIR = "./logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
LOG_FILE = os.path.join(
    LOG_DIR, datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "_init_db.log"
)
print({"LOG_FILE": LOG_FILE})


def setup_logging():
    """
    Set up logging configuration for production.
    Uses RotatingFileHandler for safe log management with rotation.
    """
    # Create a rotating file handler (log file size limit: 5MB, backup count: 5)
    handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    # Configure SQLAlchemy Engine logs for warning level
    sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
    sqlalchemy_logger.setLevel(logging.WARNING)
    sqlalchemy_logger.addHandler(handler)


# Call the logging setup function
setup_logging()


def create_database_if_not_exists():
    """
    Create the PostgreSQL database if it doesn't already exist.
    """
    sync_url = settings.POSTGRES_URI.replace("+asyncpg", "")
    try:
        if not database_exists(sync_url):
            create_database(sync_url)
            logging.info(f"Created database {settings.POSTGRES_DB}")
        else:
            logging.info(f"Database {settings.POSTGRES_DB} already exists")
    except Exception as e:
        logging.error(f"Error creating database: {str(e)}")
        raise


def load_initial_data():
    """
    Load initial seed data from JSON files with UTF-8 encoding.
    """
    files = ["nguoi_dung.json", "album.json", "audio.json", "track.json", "lyric.json"]
    data = {}
    for file_name in files:
        with open(f"./data/init_data/{file_name}", "r", encoding="utf-8") as file:
            key = file_name.replace(".json", "")
            data[key] = json.load(file)
    return data

async def find_lyric_by_trackId(trackId, lyrics):
    for lyric in lyrics:
        if lyric["trackId"] == str(trackId):
            return lyric
    return None

async def find_audio_by_id(audioId, audios):
    for audio in audios:
        if audio["id"] == audioId:
            return audio
    return None

async def find_album_index_by_id(albumId, albums):
    for index, album in enumerate(albums):
        if album["id"] == albumId:
            return index
    return None

async def find_album_image_by_id(albumId, albums):
    for album in albums:
        if album["id"] == albumId:
            return album["coverImageUrl"]
    return None

async def create_initial_records(data, session):
    """
    Create initial records for nguoi_dungs
    """
    logging.info("Creating initial data")

    try:
        # Create nguoi_dungs
        nguoi_dungs = [
            await crud_nguoi_dung.create(session, NguoiDungCreate(**nguoi_dung))
            for nguoi_dung in data["nguoi_dung"]
        ]
        logging.info(f"Created {len(nguoi_dungs)} nguoi_dungs")

        albums = data["album"]
        audios = data["audio"]
        tracks = data["track"]
        lyrics = data["lyric"]
        
        # Create danh_sach_phat
        danh_sach_phat_create_db = []
        danh_sach_phat_create_datas = []
        for album in albums:
            danh_sach_phat_create_data = {
                "ten_danh_sach_phat": album["title"],
                "loai": "album",
                "anh": album["coverImageUrl"],
                # convert int to datetime
                "thoi_gian_ra_mat": datetime.strptime(str(album["releasedAt"]), "%Y%m%d"),
                "thoi_gian_tao": datetime.now()
            }
            danh_sach_phat_create_datas.append(danh_sach_phat_create_data)
        danh_sach_phat_create_db = await crud_danh_sach_phat.create_multi(session, [DanhSachPhatCreate(**danh_sach_phat_create_data) for danh_sach_phat_create_data in danh_sach_phat_create_datas])
        logging.info(f"Created {len(danh_sach_phat_create_db)} danh_sach_phat")
        
        bai_hat_create_db = []
        bai_hat_create_datas = []
        danh_sach_phat_bai_hat_create_datas = []
        for track in tracks:
            loi_bai_hat = await find_lyric_by_trackId(track["id"], lyrics)
            audio = await find_audio_by_id(track["audioId"], audios)
            
            bai_hat_create_data = {
                "ten_bai_hat": track["title"],
                "anh": await find_album_image_by_id(track["albumId"], albums) if await find_album_image_by_id(track["albumId"], albums) else None,
                "ten_ca_si": track["artistNames"],
                "loi_bai_hat" : loi_bai_hat["content"] if loi_bai_hat else None,
                "thoi_luong": int(int(track["durationMs"]) / 1000),
                "lien_ket": audio["fullUrl"],
                "trang_thai": "hoat_dong",
                "quyen_rieng_tu": "cong_khai",
                "thoi_gian_tao": datetime.now()
            }
            bai_hat_create_datas.append(bai_hat_create_data)
            
            album_index = await find_album_index_by_id(track["albumId"], albums)
            danh_sach_phat_bai_hat_create_data = {
                "danh_sach_phat_id": danh_sach_phat_create_db[album_index].id,
                "bai_hat_index": len(bai_hat_create_datas) - 1,
                "so_thu_tu": track["trackNumber"],
                "bai_hat_id": None,
                "thoi_gian_tao": datetime.now()
            }
            danh_sach_phat_bai_hat_create_datas.append(danh_sach_phat_bai_hat_create_data)
            print("Len danh_sach_phat_bai_hat_create_datas: ", len(danh_sach_phat_bai_hat_create_datas))
        bai_hat_create_db = await crud_bai_hat.create_multi(session, [BaiHatCreate(**bai_hat_create_data) for bai_hat_create_data in bai_hat_create_datas])
        logging.info(f"Created {len(bai_hat_create_db)} bai_hat")
        
        danh_sach_phat_bai_hat_create_db = []
        for danh_sach_phat_bai_hat_create_data in danh_sach_phat_bai_hat_create_datas:
            bai_hat_index = danh_sach_phat_bai_hat_create_data["bai_hat_index"]
            # remove bai_hat_index from danh_sach_phat_bai_hat_create_data
            del danh_sach_phat_bai_hat_create_data["bai_hat_index"]
            danh_sach_phat_bai_hat_create_data["bai_hat_id"] = bai_hat_create_db[bai_hat_index].id
        danh_sach_phat_bai_hat_create_db = await crud_danh_sach_phat_bai_hat.create_multi(session, [DanhSachPhatBaiHatCreate(**danh_sach_phat_bai_hat_create_data) for danh_sach_phat_bai_hat_create_data in danh_sach_phat_bai_hat_create_datas])
        
        logging.info(f"Created {len(danh_sach_phat_bai_hat_create_db)} danh_sach_phat_bai_hat")
    except Exception as e:
        logging.error(f"Error initializing data: {str(e)}")
        raise


async def init_db():
    """
    Initialize the database, create tables, and seed initial data.
    """
    try:
        create_database_if_not_exists()

        async with database.get_async_engine().begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            logging.info("Created all tables")

        data = load_initial_data()

        async with database.AsyncSessionLocal() as session:
            await create_initial_records(data, session)

    except Exception as e:
        logging.error(f"Database initialization failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(init_db())
