from datetime import datetime
from io import BytesIO
from typing import Any, AsyncGenerator

import pytest
from fakeredis import FakeServer
from fakeredis.aioredis import FakeConnection
from fastapi import FastAPI, UploadFile
from httpx import AsyncClient
from redis.asyncio import ConnectionPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from starlette.datastructures import Headers

from cv_copilot.db.dao.job_descriptions import JobDescriptionDAO
from cv_copilot.db.dao.pdfs import PDFDAO
from cv_copilot.db.dependencies import get_db_session
from cv_copilot.db.utils import create_database, drop_database
from cv_copilot.services.redis.dependency import get_redis_pool
from cv_copilot.settings import settings
from cv_copilot.web.application import get_app
from cv_copilot.web.dto.job_description.schema import (
    JobDescriptionDTO,
    JobDescriptionInputDTO,
)
from cv_copilot.web.dto.pdfs.schema import PDFModelDTO, PDFModelInputDTO


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Backend for anyio pytest plugin.

    :return: backend name.
    """
    return "asyncio"


@pytest.fixture(scope="session")
async def _engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create engine and databases.

    :yield: new engine.
    """
    from cv_copilot.db.meta import meta  # noqa: WPS433
    from cv_copilot.db.models import load_all_models  # noqa: WPS433

    load_all_models()

    await create_database()

    engine = create_async_engine(str(settings.db_url))
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()
        await drop_database()


@pytest.fixture
async def dbsession(
    _engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get session to database.

    Fixture that returns a SQLAlchemy session with a SAVEPOINT, and the rollback to it
    after the test completes.

    :param _engine: current engine.
    :yields: async session.
    """
    async with _engine.begin() as conn:
        # Start a nested transaction (savepoint)
        await conn.begin_nested()

        session_maker = async_sessionmaker(
            bind=conn,
            expire_on_commit=False,
        )
        session = session_maker()

        try:
            yield session
        finally:
            # Rollback the outer transaction
            await conn.rollback()
            await session.close()


@pytest.fixture
async def fake_redis_pool() -> AsyncGenerator[ConnectionPool, None]:
    """
    Get instance of a fake redis.

    :yield: FakeRedis instance.
    """
    server = FakeServer()
    server.connected = True
    pool = ConnectionPool(connection_class=FakeConnection, server=server)

    yield pool

    await pool.disconnect()


@pytest.fixture
def fastapi_app(
    dbsession: AsyncSession,
    fake_redis_pool: ConnectionPool,
) -> FastAPI:
    """
    Fixture for creating FastAPI app.

    :return: fastapi app with mocked dependencies.
    """
    application = get_app()
    application.dependency_overrides[get_db_session] = lambda: dbsession
    application.dependency_overrides[get_redis_pool] = lambda: fake_redis_pool
    return application  # noqa: WPS331


@pytest.fixture
async def client(
    fastapi_app: FastAPI,
    anyio_backend: Any,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that creates client for requesting server.

    :param fastapi_app: the application.
    :yield: client for the app.
    """
    async with AsyncClient(app=fastapi_app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def create_job_description(dbsession: AsyncSession) -> JobDescriptionDTO:
    """Create a fixture to create a job description.

    :param dbsession: AsyncSession instance.
    :return: JobDescriptionDTO instance.
    """
    job_description_dao = JobDescriptionDAO(dbsession)
    job_description_input_dto = JobDescriptionInputDTO(
        title="Sample Job Title",
        description="Sample Job Description",
    )
    return await job_description_dao.create_job_description(job_description_input_dto)


@pytest.fixture
async def create_pdf(dbsession: AsyncSession) -> PDFModelDTO:
    """Create a fixture to create a job pdf.

    :param dbsession: AsyncSession instance.
    :return: PDFModelDTO instance.
    """
    date = datetime(2023, 1, 1).isoformat()
    pdf_dao = PDFDAO(dbsession)

    # Create a PDF file in memory
    pdf_file_content = b"%PDF-1.4..."
    pdf_file = BytesIO(pdf_file_content)
    pdf_file.name = "test.pdf"
    upload_file = UploadFile(
        filename=pdf_file.name,
        file=pdf_file,
        headers=Headers({"content-type": "application/pdf"}),
    )

    # Create a PDFModelInputDTO without the file attribute
    pdf_input = PDFModelInputDTO(name="test.pdf", job_id=1, created_date=date)

    # Pass the UploadFile object and the PDFModelInputDTO to the upload_pdf method
    return await pdf_dao.upload_pdf(pdf_input, upload_file)
