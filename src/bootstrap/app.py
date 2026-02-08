from fastapi import FastAPI

from src.api import router
from src.bootstrap.configuration import Settings
from src.bootstrap.containers import Container


def create_app() -> FastAPI:
    container = Container()
    container.init_resources()
    container.config.from_pydantic(Settings())
    container.wire(modules=["src.api.endpoints"])

    app = FastAPI(title="Minerva Token Gatekeeper")
    setattr(app, "container", container)

    app.include_router(router)
    return app
