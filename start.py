"""Script for local start of app."""
import uvicorn

from src.conf.config import settings


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True
    )
