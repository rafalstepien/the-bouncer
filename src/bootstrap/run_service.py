import uvicorn
from src.bootstrap.app import create_app

if __name__ == "__main__":
    uvicorn.run(
        f"{__name__}:{create_app.__name__}",
        host="0.0.0.0",
        port=8000,
        # port=config.port,
        reload=True,
    )
