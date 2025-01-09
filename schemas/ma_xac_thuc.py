"""
This module defines the Pydantic schemas for managing authentication tokens.
It includes schemas for creating, refreshing,
and outputting token information.
"""

from typing import Literal, Optional
from datetime import datetime as DateTime
from pydantic import BaseModel


class Ma(BaseModel):
    """
    Schema for representing an access token.

    Attributes:
        access_token (str): The JWT access token.
        token_type (Literal["bearer"]): The type of token, usually "bearer".
    """

    access_token: str
    token_type: Literal["bearer"]


class ThongTinMaSchema(BaseModel):
    """
    Schema for the payload of a token, typically used when decoding tokens.

    Attributes:
        nguoi_dung_id (Optional[str]): The ID of the nguoi_dung that the token belongs to.
        expires_at (Optional[DateTime]): The expiration date and time of the token.
    """

    nguoi_dung_id: Optional[str]
    thoi_gian_het_han: Optional[DateTime]


class MaCreate(BaseModel):
    """
    Schema for creating a new token, which includes both access and refresh tokens.

    Attributes:
        access_token (str): The JWT access token.
        ma_lam_moi (Optional[str]): The refresh token for renewing access tokens.
        expires_at (DateTime): The expiration date and time of the token.
        nguoi_dung_id (str): The ID of the nguoi_dung that the token is issued for.
    """

    access_token: str
    ma_lam_moi: Optional[str]
    expires_at: DateTime
    nguoi_dung_id: str


class MaRefresh(BaseModel):
    """
    Schema for refreshing a token.

    Attributes:
        ma_lam_moi (str): The refresh token used to request a new access token.
    """

    ma_lam_moi: str
