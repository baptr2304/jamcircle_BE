"""
This module defines the base class for all SQLAlchemy models used in the FastAPI application.
It provides basic functionality, such as dynamic table name generation and converting a model instance
to a dictionary.
"""

from typing import Any, Dict
import inflection
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base(object):
    """
    Base class for all SQLAlchemy models.

    This class is decorated with `@as_declarative()` which allows us to use it as a declarative
    base class for SQLAlchemy ORM models. It provides automatic table name generation based on
    the class name and a `dict` method to convert model instances into dictionaries.
    """

    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        """
        Automatically generate the table name for the model by converting the class name to snake_case.

        Returns:
            str: The generated table name.
        """
        return inflection.underscore(cls.__name__)

    def dict(self) -> Dict[str, Any]:
        """
        Convert a SQLAlchemy model instance to a dictionary.

        Returns:
            Dict[str, Any]: A dictionary representation of the model instance.
        """
        return {
            c.key: getattr(self, c.key, None) for c in inspect(self).mapper.column_attrs
        }
