import uvicorn

from src.bootstrap.app import create_app
from src.bootstrap.configuration import Settings

if __name__ == "__main__":
    settings = Settings()
    uvicorn.run(
        f"{__name__}:{create_app.__name__}",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.debug,
    )
