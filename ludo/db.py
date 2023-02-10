from sqlalchemy.orm import DeclarativeBase
from starlite import DTOFactory
from starlite.plugins.sql_alchemy import (
    SQLAlchemyConfig,
    SQLAlchemyEngineConfig,
    SQLAlchemyPlugin,
)

sqlalchemy_config = SQLAlchemyConfig(
    connection_string="sqlite+aiosqlite:///db.sqlite",
    dependency_key="session",
    engine_config=SQLAlchemyEngineConfig(echo=True),
)

sqlalchemy_plugin = SQLAlchemyPlugin(config=sqlalchemy_config)

dto_factory = DTOFactory(plugins=[sqlalchemy_plugin])


class Base(DeclarativeBase):
    pass


async def db_on_startup() -> None:
    async with sqlalchemy_config.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
