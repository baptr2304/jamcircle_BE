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
from openai import OpenAI
import openai

bucket_name = settings.BUCKET_NAME

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION_NAME
)

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

async def transcribe_audio(file: UploadFile) -> tuple[str, bool]:
    """
    Transcribes audio using OpenAI's Whisper model with the updated API.
    Returns tuple of (transcription text, success boolean)
    """
    temp_file_name = None
    try:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_name = temp_file.name

        # Use the OpenAI API to transcribe the audio file
        with open(temp_file_name, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            
        return transcript.text, True

    except openai.RateLimitError:
        print("OpenAI API quota exceeded")
        return "", False
    except openai.APIError as e:
        print(f"OpenAI API Error: {e}")
        return "", False
    except Exception as e:
        print(f"Error with OpenAI audio transcription: {e}")
        return "", False
    finally:
        # Clean up temporary file
        if temp_file_name and os.path.exists(temp_file_name):
            os.unlink(temp_file_name)

async def kiem_duyet_noi_dung(text: str) -> tuple[bool, bool, str]:
    """
    Content moderation using OpenAI API
    Returns tuple of (is_appropriate, success boolean, reason string)
    """
    if not text:  # If no text to moderate, consider it appropriate
        return True, True, ""
        
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """You are a content moderator. Evaluate if the content is appropriate.
                If inappropriate, explain why. Check for:
                - Offensive language
                - Hate speech
                - Explicit content
                - Violence
                - Copyright infringement hints
                Respond in format: 'APPROPRIATE' or 'INAPPROPRIATE: [detailed reason]'"""},
                {"role": "user", "content": f"Evaluate the following content: {text}"}
            ]
        )
        result = response.choices[0].message.content.strip()
        print(f"Content moderation result: {result}")
        
        is_appropriate = result.upper().startswith("APPROPRIATE")
        reason = result.split(": ")[1] if ": " in result else ""
        
        return is_appropriate, True, reason
        
    except openai.RateLimitError:
        print("OpenAI API quota exceeded during moderation")
        return True, False, "Moderation service unavailable"
    except openai.APIError as e:
        print(f"OpenAI API Error during moderation: {e}")
        return True, False, f"Moderation service error: {str(e)}"
    except Exception as e:
        print(f"Error with content moderation: {e}")
        return True, False, f"Moderation error: {str(e)}"


router = APIRouter(prefix="/bai_hat", tags=["Bai hat"])

@router.get("/tim_kiem")
async def tim_kiem_bai_hat(
    request: Request,
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
        print("Filters: ", filters)
        bai_hats = await crud_bai_hat.search(session, offset=offset, limit=limit, **filters)
        if not bai_hats:
            return []
        return bai_hats
    except Exception as e:
        print("Error: ", str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
async def xem_danh_sach_bai_hat(
    session: AsyncSession = Depends(get_session),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
):
    """
    Endpoint to get all songs.
    """
    try:
        bai_hats = await crud_bai_hat.get_multi(session, offset=offset, limit=limit)
    
        # sort by ten_bai_hat a to z
        bai_hats = sorted(bai_hats, key=lambda x: x.ten_bai_hat)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return bai_hats

@router.get("/{id}")
async def xem_chi_tiet_bai_hat(
    id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint to get song details by ID.
    """
    bai_hat = await crud_bai_hat.get(session, id=id)
    if not bai_hat:
        raise HTTPException(status_code=404, detail="Bai hat not found")
    return bai_hat

@router.post("")
async def tao_bai_hat(
    bai_hat: str,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Endpoint to create a new song.
    """
    try:
        # Reset file pointer
        await file.seek(0)
        
        # Try transcription, but continue if it fails
        transcribed_text, transcription_success = await transcribe_audio(file)
        if not transcription_success:
            print("Warning: Audio transcription failed, continuing without transcription")
        else:
            print(f"Transcribed text: {transcribed_text}")
            
        # Content moderation
        is_appropriate, moderation_success, moderation_reason = await kiem_duyet_noi_dung(transcribed_text)
        
        # If moderation was successful and content is inappropriate, block creation
        if moderation_success and not is_appropriate:
            raise HTTPException(
                status_code=400, 
                detail={
                    "message": "Nội dung bài hát không phù hợp",
                    "reason": moderation_reason
                }
            )
        
        # If moderation failed, log warning but allow creation
        if not moderation_success:
            print(f"Warning: Content moderation failed - {moderation_reason}")
            print("Continuing without moderation")
            
        # Rest of the function remains the same...
        # [Previous code for parsing JSON, creating record, S3 upload, etc.]
        
        try:
            bai_hat_dict = json.loads(bai_hat)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
            
        # Create song record
        bai_hat_create = BaiHatCreate(**bai_hat_dict)
        bai_hat_create_db = await crud_bai_hat.create(session, obj_in=bai_hat_create)
        
        # Reset file pointer for S3 upload
        await file.seek(0)
        file_content = await file.read()
        
        # Upload to S3
        tail_file = file.filename.split(".")[-1]
        ten_file = f"{bai_hat_create_db.id}.{tail_file}"
        
        try:
            s3_client.put_object(Bucket=bucket_name, Key=ten_file, Body=file_content)
        except NoCredentialsError:
            await crud_bai_hat.remove(session, id=bai_hat_create_db.id)
            raise HTTPException(status_code=500, detail="AWS credentials not available")
        except Exception as e:
            await crud_bai_hat.remove(session, id=bai_hat_create_db.id)
            raise HTTPException(status_code=500, detail=f"Error uploading to S3: {str(e)}")
            
        # Update song record with S3 link
        lien_ket = f"https://{bucket_name}.s3-{settings.AWS_REGION_NAME}.amazonaws.com/{ten_file}"
        bai_hat_update_data = BaiHatUpdateDB(lien_ket=lien_ket)
        
        bai_hat_update_db = await crud_bai_hat.update(
            session, 
            obj_in=bai_hat_update_data, 
            db_obj=bai_hat_create_db
        )
        
        await session.commit()
        
        response_data = {
            "id": str(bai_hat_update_db.id),
            "ten_bai_hat": bai_hat_update_db.ten_bai_hat,
            "anh": bai_hat_update_db.anh,
            "ten_ca_si": bai_hat_update_db.ten_ca_si,
            "the_loai": bai_hat_update_db.the_loai,
            "mo_ta": bai_hat_update_db.mo_ta,
            "loi_bai_hat": bai_hat_update_db.loi_bai_hat,
            "thoi_luong": bai_hat_update_db.thoi_luong,
            "lien_ket": bai_hat_update_db.lien_ket,
            "trang_thai": bai_hat_update_db.trang_thai,
            "quyen_rieng_tu": bai_hat_update_db.quyen_rieng_tu,
            "thoi_gian_tao": bai_hat_update_db.thoi_gian_tao.isoformat() if bai_hat_update_db.thoi_gian_tao else None,
            "thoi_gian_cap_nhat": bai_hat_update_db.thoi_gian_cap_nhat.isoformat() if bai_hat_update_db.thoi_gian_cap_nhat else None,
            "nguoi_dung_id": str(bai_hat_update_db.nguoi_dung_id) if bai_hat_update_db.nguoi_dung_id else None
        }

        # Add warnings if services failed
        if not transcription_success or not moderation_success:
            response_data["warnings"] = []
            if not transcription_success:
                response_data["warnings"].append("Audio transcription service unavailable")
            if not moderation_success:
                response_data["warnings"].append(f"Content moderation service unavailable: {moderation_reason}")
        
        return response_data
        
    except HTTPException as http_ex:
        # Nếu là HTTPException thì ta giữ nguyên mã lỗi
        await session.rollback()
        raise http_ex
    except Exception as e:
        # Nếu là lỗi khác, ta mới raise 500
        await session.rollback()
        print(f"Error creating song: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


