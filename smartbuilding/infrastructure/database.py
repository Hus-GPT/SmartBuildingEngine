from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from smartbuilding.config import get_settings


def build_engine(database_url: str | None = None):
    return create_engine(database_url or get_settings().database_url, pool_pre_ping=True)


engine = build_engine()


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def create_schema() -> None:
    SQLModel.metadata.create_all(engine)
