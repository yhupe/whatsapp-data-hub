import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

# load .env.test file to interact with testing database
load_dotenv(dotenv_path=".env.test")

# Import Base und get_db
from database.database import Base, get_db

from main import app
# Import of all models that Base.metadata knows all of them when creating it for testing
from database import models

@pytest.fixture(scope="session")
def test_engine():
    """ Fixture for test engine (session-scope) """

    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set for tests in .env.test.")

    # Create engine
    engine = create_engine(DATABASE_URL)
    yield engine
    # Disposal of engine after all tests of the session
    engine.dispose()


@pytest.fixture(scope="function", autouse=True)
def db_session_for_test(test_engine):
    """ Fixture for test db session (function-scope),
    autouse=True: runs prior to every test.
    Creates tables before each test and drops them after each test.
    Provides a clean database session for each test function.
    """

    test_engine.dispose()

    # Deletion and new creation of tables prior to EVERY test to ensure test isolation
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    # New connection and transaction for the current test
    connection = test_engine.connect()
    transaction = connection.begin()

    # Binding the session to the specific connection
    db = Session(bind=connection)

    # Override the dependency of FastAPI app to use the test db session
    app.dependency_overrides[get_db] = lambda: db

    try:
        # provide session for the test
        yield db
    finally:
        # After test: close the session and rollback of transaction
        db.close()
        transaction.rollback()
        connection.close()

        # removal of overridden dependency
        app.dependency_overrides.pop(get_db)


@pytest.fixture(scope="function")
def client(db_session_for_test):
    """ Fixture for FastAPI TestClient,
    Provides FastAPI TestClient to send requests to the app.
    """

    return TestClient(app)