from pytest_postgresql import factories  # type:ignore
from pytest_postgresql.janitor import DatabaseJanitor
from pytest_postgresql.executor import PostgreSQLExecutor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.state import State
from api.models import Base

import pytest

import alembic.config


test_db = factories.postgresql_proc(port=None, dbname="test_db")  # type:ignore


@pytest.fixture(scope="module")
def state_fixture(test_db: PostgreSQLExecutor):
    pg_host = test_db.host
    pg_port = test_db.port
    pg_user = test_db.user
    pg_password = test_db.password
    pg_db = test_db.dbname

    with DatabaseJanitor(
        user=pg_user,
        host=pg_host,
        port=pg_port,
        version="13",
        dbname=pg_db,
        password=pg_password,
    ):
        connection_str = (
            f"postgresql+psycopg2://{pg_user}:@{pg_host}:{pg_port}/{pg_db}"
        )
        engine = create_engine(connection_str)
        with engine.connect() as connection:
            # specify the db_path x argument
            alembic.config.main(
                argv=[
                    "--raiseerr",
                    "-x",
                    f"db_path={connection_str}",
                    "upgrade",
                    "head",
                ]
            )

            Base.metadata.create_all(connection)
            SessionLocal = sessionmaker(
                bind=engine, autoflush=False, autocommit=False
            )

            print("database created")
            yield State(SessionLocal(), "mysecret")
