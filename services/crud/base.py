"""
This module defines the base CRUD class for interacting with the database.
The CRUDBase class contains generic methods for common database operations
like create, read, update, delete, and search.
"""

import logging
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# Type definitions
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

# Set up logging
logger = logging.getLogger(__name__)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    CRUDBase is a generic class for handling common CRUD operations in a database.

    Attributes:
        _model (Type[ModelType]): The SQLAlchemy model representing the database table.

    Methods:
        create: Create a new record.
        get: Retrieve a record by filtering.
        get_multi: Retrieve multiple records with pagination.
        update: Update a record with the provided data.
        delete: Delete a record.
        search: Search for records based on the provided filters.
    """

    def __init__(self, model: Type[ModelType]) -> None:
        self._model = model

    async def create(
        self, session: AsyncSession, obj_in: CreateSchemaType
    ) -> Optional[ModelType]:
        """
        Create a new record in the database.

        Parameters:
            session (AsyncSession): The current database session.
            obj_in (CreateSchemaType): The data for the new record.

        Returns:
            Optional[ModelType]: The created record if successful, else None.
        """
        obj_in_data = obj_in.dict()
        db_obj = self._model(**obj_in_data)
        session.add(db_obj)

        try:
            await session.commit()
            await session.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error("Error while creating record: %s", str(e))
            return None
        
    async def create_multi(
        self, session: AsyncSession, objs_in: List[CreateSchemaType]
    ) -> List[ModelType]:
        """
        Create multiple records in the database.

        Parameters:
            session (AsyncSession): The current database session.
            objs_in (List[CreateSchemaType]): The data for the new records.

        Returns:
            List[ModelType]: The created records if successful, else an empty list.
        """
        # Chuyển đổi danh sách các schema input thành danh sách các đối tượng model
        objs_in_data = [obj_in.dict() for obj_in in objs_in]
        db_objs = [self._model(**obj_data) for obj_data in objs_in_data]
        
        # Thêm tất cả các đối tượng vào session
        session.add_all(db_objs)

        try:
            # Commit và refresh tất cả các đối tượng sau khi thêm vào DB
            await session.commit()
            
            # Refresh từng đối tượng để lấy các giá trị được gán từ DB (như ID auto increment)
            for db_obj in db_objs:
                await session.refresh(db_obj)
            
            return db_objs
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error("Error while creating multiple records: %s", str(e))
            return []

    async def get(self, session: AsyncSession, *args, **kwargs) -> Optional[ModelType]:
        """
        Retrieve a record based on the provided filters.

        Parameters:
            session (AsyncSession): The current database session.
            args: Optional SQLAlchemy filter arguments.
            kwargs: Filter conditions.

        Returns:
            Optional[ModelType]: The retrieved record or None if not found.
        """
        try:
            result = await session.execute(
                select(self._model).filter(*args).filter_by(**kwargs)
            )
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error("Error while retrieving record: %s", str(e))
            return None

    async def get_multi(
        self, session: AsyncSession, *args, offset: int = 0, limit: int = 100, **kwargs
    ) -> List[ModelType]:
        """
        Retrieve multiple records with optional filters and pagination.

        Parameters:
            session (AsyncSession): The current database session.
            args: Optional SQLAlchemy filter arguments.
            offset (int): The number of records to skip.
            limit (int): The maximum number of records to return.
            kwargs: Filter conditions.

        Returns:
            List[ModelType]: A list of retrieved records.
        """
        try:
            result = await session.execute(
                select(self._model)
                .filter(*args)
                .filter_by(**kwargs)
                .offset(offset)
                .limit(limit)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error("Error while retrieving multiple records: %s", str(e))
            return []

    async def update(
        self,
        session: AsyncSession,
        *,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        db_obj: Optional[ModelType] = None,
        **kwargs,
    ) -> Optional[ModelType]:
        """
        Update a record with the provided data.

        Parameters:
            session (AsyncSession): The current database session.
            obj_in (Union[UpdateSchemaType, Dict[str, Any]]): The updated data.
            db_obj (Optional[ModelType]): The database object to update.
            kwargs: Additional conditions to locate the object.

        Returns:
            Optional[ModelType]: The updated record if successful, else None.
        """
        db_obj = db_obj or await self.get(session, **kwargs)
        if not db_obj:
            return None

        update_data = (
            obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        )

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        session.add(db_obj)
        try:
            await session.commit()
            await session.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error("Error while updating record: %s", str(e))
            return None

    async def delete(
        self, session: AsyncSession, *args, db_obj: Optional[ModelType] = None, **kwargs
    ) -> Optional[ModelType]:
        """
        Delete a record from the database.

        Parameters:
            session (AsyncSession): The current database session.
            args: Optional SQLAlchemy filter arguments.
            db_obj (Optional[ModelType]): The database object to delete.
            kwargs: Additional conditions to locate the object.

        Returns:
            Optional[ModelType]: The deleted record if successful, else None.
        """
        db_obj = db_obj or await self.get(session, *args, **kwargs)
        if not db_obj:
            return None

        try:
            await session.delete(db_obj)
            await session.commit()
            return db_obj
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error("Error while deleting record: %s", str(e))
            return None

    async def search(
        self, session: AsyncSession, offset: int = 0, limit: int = 100, **kwargs
    ) -> List[ModelType]:
        """
        Search for records using filters.

        Parameters:
            session (AsyncSession): The current database session.
            offset (int): The number of records to skip.
            limit (int): The maximum number of records to return.
            kwargs: Filters to apply for the search.

        Returns:
            List[ModelType]: A list of records that match the search criteria.
        """
        try:
            query = select(self._model)
            for key, value in kwargs.items():
                query = query.filter(
                    func.lower(getattr(self._model, key)).like(f"%{value.lower()}%")
                )

            query = query.offset(offset).limit(limit)
            result = await session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error("Error while searching records: %s", str(e))
            return []
