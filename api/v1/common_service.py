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

bucket_name = settings.COMMDATA_BUCKET_NAME

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION_NAME
)


router = APIRouter(prefix="/common", tags=["Common service"])

# upload file to S3
@router.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """
    Uploads a file to the S3 bucket.
    """
    await file.seek(0)
    file_content = await file.read()
    
    try:
        s3_client.put_object(Bucket=bucket_name, Key=file.filename, Body=file_content)
        url = f"https://{bucket_name}.s3-{settings.AWS_REGION_NAME}.amazonaws.com/{file.filename}"
        return {"url": url}
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not available.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")