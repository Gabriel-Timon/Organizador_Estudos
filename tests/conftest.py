import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


engine_test = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

SessionTest = sessionmaker(
    bind=engine_test,
    autoflush=False,
    autocommit=False
)

Base.metadata.create_all(bind=engine_test)

def override_get_db():
    db_test = SessionTest()
    try:
        yield db_test
    finally:
        db_test.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def limpar_banco():
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)

    yield