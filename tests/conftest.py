import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

# Import of Base and Models so SQLAlchemy knows the tables
from database.database import Base, get_db

#Import of all models
from database import models
from main import app


# Load environment variables from .env.test file
load_dotenv(dotenv_path=".env.test")


# Fixture for the  test database engine
@pytest.fixture(scope="session")
def engine_test():
    """ Creates SQLAlchemy engine for the test database"""
    url = os.getenv("DATABASE_URL_TEST")
    if not url:
        raise ValueError("DATABASE_URL_TEST environment variable not set for tests.")
    engine = create_engine(url)
    yield engine
    engine.dispose()


# Fixture to create and delete test tables
# 'autouse=True' ensures using fixture automatically
@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown_db(engine_test):
    """Creates all tables prior to tests and deletes them afterward """

    # Creates tables
    Base.metadata.create_all(bind=engine_test)

    # testing
    yield

    # Deletes tables
    Base.metadata.drop_all(bind=engine_test)


# Fixture creates encapsulated db session for every test
@pytest.fixture(scope="function")
def db_session_test(engine_test):
    """
    creates encapsulated db session for every test,
    which gets reset after every test (rollback).
    This provides a clean database environment for every test.
    """
    # Creates connection and starts a transaction
    connection = engine_test.connect()
    transaction = connection.begin()

    # Creates session which is linked to a specific connection
    db = Session(bind=connection)

    # Overrides the `get_db` dependency of the FastAPI-App for the time of the test
    # Therefore, the app uses the test session here instead of the standard session
    app.dependency_overrides[get_db] = lambda: db

    try:
        # Passing of the session to the test here
        yield db
    finally:
        # Closes session after test
        db.close()
        transaction.rollback()
        connection.close()

        # removal of overriding the `get_db` dependency
        app.dependency_overrides.pop(get_db)


# Fixture for the FastAPI TestClient
@pytest.fixture(scope="function")
def client():
    """ Provides FastAPI TestClient to send requests to the app. """

    return TestClient(app)