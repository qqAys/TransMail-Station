from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.routers import api_router
from app.services.cron_service import should_send_email
from app.utils.util import Config, app_name, app_version, logger

config = Config()

@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info(f"Starting app {_app.__str__()}")
    logger.info("Starting scheduler")
    scheduler.add_job(should_send_email, "interval", minutes=config.send_interval)
    scheduler.start()
    logger.info("Scheduler started")

    yield

    logger.info("Stopping scheduler")
    scheduler.shutdown()
    logger.info("Scheduler stopped")


app = FastAPI(redoc_url=None, title=app_name, version=app_version, lifespan=lifespan)
app.add_middleware(
    middleware_class=TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0", *config.trusted_hosts]
)
app.include_router(router=api_router.router)

scheduler = BackgroundScheduler()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=config.app_port, log_level=config.asgi_log_level)
