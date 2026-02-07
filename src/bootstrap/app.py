from fastapi import FastAPI
from src.api import router


def create_app():
    app = FastAPI(title="Minerva Token Gatekeeper")
    app.include_router(router)
    return app
