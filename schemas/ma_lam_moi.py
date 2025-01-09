"""
This module defines the Pydantic schemas for managing Refresh Tokens.
It includes schemas for creating, updating,
and outputting Refresh Token information, as well as managing tokens in the database.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, UUID4


class MaLamMoiBase(BaseModel):
    """
    Base schema for Refresh Token. It includes fields shared across different refresh token-related schemas.

    Attributes:
        token (str): The refresh token.
        expires_at (datetime): The expiration date and time of the token.
        created_at (Optional[datetime]): The date and time the token was created.
        revoked_at (Optional[datetime]): The date and time the token was revoked.
        nguoi_dung_id (UUID4): The ID of the associated nguoi_dung.
        is_revoked (bool): Flag indicating whether the token has been revoked, defaults to False.
    """

    ma: str
    thoi_gian_het_han: datetime
    thoi_gian_tao: Optional[datetime] = None
    thoi_gian_thu_hoi: Optional[datetime] = None
    nguoi_dung_id: UUID4
    da_thu_hoi: Optional[bool] = False


class MaLamMoiCreate(MaLamMoiBase):
    """
    Schema for creating a new Refresh Token.

    Attributes:
        token (str): The refresh token.
        expires_at (datetime): The expiration date and time of the token.
        nguoi_dung_id (UUID4): The ID of the associated nguoi_dung.
    """

    pass


class MaLamMoiOut(MaLamMoiBase):
    """
    Schema for outputting Refresh Token information.

    Attributes:
        id (UUID4): The unique identifier of the refresh token.
        is_valid (bool): Flag indicating whether the token is valid.
    """

    id: UUID4
    con_hieu_luc: bool

    class Config(object):
        """
        Pydantic configuration for FaceDirectionLogOut schema
        """

        from_attributes = True


class MaLamMoiInDB(BaseModel):
    """
    Schema for representing a Refresh Token as stored in the database.

    Attributes:
        id (UUID4): The unique identifier of the refresh token.
        token (str): The refresh token.
        expires_at (datetime): The expiration date and time of the token.
        created_at (Optional[datetime]): The date and time the token was created.
        revoked_at (Optional[datetime]): The date and time the token was revoked.
        nguoi_dung_id (UUID4): The ID of the associated nguoi_dung.
        is_revoked (bool): Flag indicating whether the token has been revoked, defaults to False.
    """

    id: UUID4
    ma: str
    thoi_gian_het_han: datetime
    thoi_gian_tao: Optional[datetime] = None
    thoi_gian_thu_hoi: Optional[datetime] = None
    nguoi_dung_id: UUID4
    da_thu_hoi: bool = False


class MaLamMoiUpdateDB(BaseModel):
    """
    Schema for updating Refresh Token information in the database.

    Attributes:
        revoked_at (Optional[datetime]): The date and time the token was revoked, if applicable.
        is_revoked (Optional[bool]): Flag indicating whether the token has been revoked.
    """

    thoi_gian_thu_hoi: Optional[datetime] = None
    da_thu_hoi: Optional[bool] = None


class MaLamMoiSchema(BaseModel):
    """
    Schema for decoding a Refresh Token.

    Attributes:
        token (str): The refresh token to decode.
    """

    ma_lam_moi: str
