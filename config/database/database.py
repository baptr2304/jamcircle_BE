"""
This module handles the database setup for the FastAPI application,
including the creation of an async
SQLAlchemy engine, session maker, and session dependency for use in the app's routes.
"""

import logging
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from config.config import settings

logger = logging.getLogger(__name__)


def get_async_engine(uri: str = settings.POSTGRES_URI):
    """
    Create and return an async SQLAlchemy engine.

    Parameters:
        uri (str): The database URI for the PostgreSQL connection.

    Returns:
        AsyncEngine: An asynchronous SQLAlchemy engine.
    """
    try:
        engine = create_async_engine(
            uri,
            echo=True,
            poolclass=NullPool,
            # Disable connection pooling for better async handling
            pool_pre_ping=True,
            # Enable connection health checks
        )
        logger.info("Successfully created async database engine")
        return engine
    except Exception as e:
        logger.error(f"Failed to create database engine: {str(e)}")
        raise


def get_async_session_maker():
    """
    Create and return an async session maker.

    Returns:
        async_sessionmaker: An async session maker instance for creating sessions.
    """
    try:
        engine = get_async_engine()
        async_session = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        logger.info("Successfully created async session maker")
        return async_session
    except Exception as e:
        logger.error(f"Failed to create async session maker: {str(e)}")
        raise


# Create engine and SessionLocal instances
engine = get_async_engine()
AsyncSessionLocal = get_async_session_maker()


async def get_db():
    """
    Dependency that yields database sessions.

    This function should be used as a dependency in FastAPI routes to provide a database session
    that can be used for database operations. Once the request is complete, the session is closed.

    Yields:
        AsyncSession: A SQLAlchemy async session.
    """
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()
