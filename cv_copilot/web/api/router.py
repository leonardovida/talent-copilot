from fastapi.routing import APIRouter

from cv_copilot.web.api import (
    docs,
    echo,
    job_descriptions,
    monitoring,
    parsed_job_descriptions,
    parsed_texts,
    pdfs,
    redis,
    texts,
    users,
)

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(users.router)
api_router.include_router(docs.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(pdfs.router, prefix="/pdfs", tags=["pdf"])
api_router.include_router(
    job_descriptions.router,
    prefix="/job-descriptions",
    tags=["job-descriptions"],
)
api_router.include_router(redis.router, prefix="/redis", tags=["redis"])
api_router.include_router(texts.router, prefix="/texts", tags=["text"])
api_router.include_router(
    parsed_job_descriptions.router,
    prefix="/parsed-job-descriptions",
    tags=["parsed-job-descriptions"],
)
api_router.include_router(
    parsed_texts.router,
    prefix="/parsed-texts",
    tags=["parsed-texts"],
)
