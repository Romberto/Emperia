from sqlalchemy.ext.asyncio.session import AsyncSession

from core.config import settings
from main import app_main
from models.base import Base
from models.db_helper import DataBaseHelper
import pytest

test_db_helper = DataBaseHelper(
    url=str(settings.db.test_url),
    echo=False,
    echo_pool=False,
    )

@pytest.fixture(scope="session")
def anyio_backend():
    return 'asyncio'


@pytest.fixture(scope='session')
async def prepare_database():
    """Создаёт все таблицы и удаляет после завершения сессии."""
    if settings.run.debug != 1:
        print('*'*50)
        pytest.exit("❌ Запуск тестов разрешён только в режиме DEBUG (settings.run.debug == 1)", returncode=1)

    async with test_db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_db_helper.dispose()

@pytest.fixture(scope='function')
async def session(prepare_database) -> AsyncSession:
    """Открывает сессию на время теста."""
    async with test_db_helper.session_factory() as session:
        yield session

@pytest.fixture(autouse=True)
def override_get_db(session: AsyncSession):
    app_main.dependency_overrides[test_db_helper.session_getter] = lambda: session
    yield
    app_main.dependency_overrides = {}