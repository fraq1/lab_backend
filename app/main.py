import uvicorn
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from config.config import settings
from contextlib import asynccontextmanager
from fastapi_pagination import add_pagination
from models import db_helper, Base
from api import router as api_router
from fastapi.security import OAuth2PasswordBearer
from taskiq_broker import broker
import taskiq_fastapi
from tasks import generate_video_task  # noqa: F401
from exceptions import setup_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create media directories if they don't exist
    Path("media/images").mkdir(parents=True, exist_ok=True)
    Path("media/videos").mkdir(parents=True, exist_ok=True)

    # Start broker if not in worker process
    if not broker.is_worker_process:
        await broker.startup()

    yield
    # shutdown
    await db_helper.dispose()

    # Shutdown broker if not in worker process
    if not broker.is_worker_process:
        await broker.shutdown()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

app = FastAPI(
    lifespan=lifespan,
)

# Initialize taskiq-fastapi integration
taskiq_fastapi.init(broker, "app.main:app")

app.include_router(
    api_router,
)
add_pagination(app)

# Mount static files for media
app.mount("/media", StaticFiles(directory="media"), name="media")
#setup_exception_handlers(main_app)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
    )
