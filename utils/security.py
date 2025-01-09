"""
This module provides utility functions for handling password security.
It includes functionality for hashing passwords and verifying hashed passwords using bcrypt.
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def xac_thuc_mat_khau(plain_password: str, mat_khau_ma_hoa: str) -> bool:
    """
    Verify if the provided plain password matches the hashed password.

    Parameters:
        plain_password (str): The plain-text password provided by the nguoi_dung.
        mat_khau_ma_hoa (str): The hashed password stored in the database.

    Returns:
        bool: True if the plain password matches the hashed password, otherwise False.
    """
    return pwd_context.verify(plain_password, mat_khau_ma_hoa)


def ma_hoa_mat_khau(password: str) -> str:
    """
    Hash the provided password.

    Parameters:
        password (str): The plain-text password to hash.

    Returns:
        str: The hashed version of the password using bcrypt.
    """
    return pwd_context.hash(password)
