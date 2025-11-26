from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from src.core.setting import settings
from src.presentation.fast_api.middlewares.jwt import JWTManager
from src.presentation.fast_api.v1.interview import interview
from src.dependencies.main import setup_dependencies
from loguru import logger
import uvicorn

app = FastAPI(
    title=settings.project_name,
    description=settings.project_description,
    version=settings.project_version,
    default_response_class=ORJSONResponse,
)

#
# @app.middleware("http")
# async def jwt_middleware(request, call_next):
#     return await JWTManager(settings.public_key)(request, call_next)


app.include_router(interview.router, prefix="/api/v1")
setup_dependencies(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
