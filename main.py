from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.config import settings
from api import router
import uvicorn


def create_application() -> FastAPI:
    application = FastAPI(title=settings.APP_NAME)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )
    application.include_router(router)
    return application


app = create_application()


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host=settings.FASTAPI_HOST, port=settings.FASTAPI_PORT, reload=True
    )
