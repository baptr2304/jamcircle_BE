"""
This module contains CRUD operations for the NguoiDung model.
It extends from the generic CRUDBase class and adds specific 
functionality for creating nguoi_dungs with mat_khau hashing.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status, Depends
from typing import Any, Dict, Optional, Union
from models.nguoi_dung import NguoiDung
from schemas.nguoi_dung import NguoiDungCreate, NguoiDungUpdateDB, NguoiDungOut
from utils.security import ma_hoa_mat_khau
from services.crud.base import CRUDBase
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)


class CRUDNguoiDung(CRUDBase[NguoiDung, NguoiDungCreate, NguoiDungUpdateDB]):
    """
    CRUD operations for the NguoiDung model. This class extends CRUDBase and provides additional
    methods to handle specific requirements for managing nguoi_dungs, such as hashing mat_khaus.
    """

    async def create(self, session: AsyncSession, obj_in: NguoiDungCreate) -> NguoiDung:
        """
        Create a new NguoiDung in the database after hashing the mat_khau.

        Parameters:
            session (AsyncSession): The database session.
            obj_in (NguoiDungCreate): The data needed to create a new nguoi_dung.

        Returns:
            NguoiDung: The created NguoiDung object.

        Raises:
            HTTPException: If there was an error while creating the nguoi_dung.
        """
        obj_in_data = obj_in.dict()

        # Hash the mat_khau securely
        obj_in_data["mat_khau_ma_hoa"] = ma_hoa_mat_khau(obj_in.mat_khau)

        # Remove plain mat_khau from the dictionary to avoid saving it
        del obj_in_data["mat_khau"]

        db_obj = self._model(**obj_in_data)

        try:
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            await session.rollback()
            logger.error(f"Integrity error while creating nguoi_dung: {e}")
            print("Integrity error while creating nguoi_dung: ", e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="NguoiDung with this data already exists. Please check the input data.",
            )
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database error while creating nguoi_dung: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the nguoi_dung. Please try again later.",
            )

    async def update(
        self,
        session: AsyncSession,
        obj_in: Union[NguoiDungUpdateDB, Dict[str, Any]],
        db_obj: Optional[NguoiDung] = None,
        **kwargs,
    ) -> Optional[NguoiDung]:
        """
        Update an existing NguoiDung record with new data.

        Parameters:
            session (AsyncSession): The database session.
            obj_in (Union[NguoiDungUpdateDB, Dict[str, Any]]): The updated data for NguoiDung.
            db_obj (Optional[NguoiDung]): The existing NguoiDung object to update, if available.
            kwargs: Additional conditions to locate the object if db_obj is not provided.

        Returns:
            Optional[NguoiDung]: The updated NguoiDung object if successful, else None.

        Raises:
            HTTPException: If there was an error updating the nguoi_dung.
        """
        db_obj = db_obj or await self.get(session, **kwargs)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="NguoiDung not found"
            )

        # Convert obj_in to a dictionary if it's a Pydantic model
        update_data = (
            obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        )

        update_data["thoi_gian_cap_nhat"] = datetime.now()

        # Check if 'mat_khau' needs to be updated, and hash it if present
        if "mat_khau" in update_data:
            update_data["mat_khau_ma_hoa"] = ma_hoa_mat_khau(
                update_data.pop("mat_khau")
            )

        # Update other fields in the db_obj
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        session.add(db_obj)
        try:
            await session.commit()
            await session.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            await session.rollback()
            logger.error(f"Integrity error while updating nguoi_dung: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update operation conflicts with existing data. Please check the input data.",
            )
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database error while updating nguoi_dung: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating the nguoi_dung. Please try again later.",
            )


# Instantiate the CRUDNguoiDung class for the NguoiDung model
crud_nguoi_dung = CRUDNguoiDung(NguoiDung)
