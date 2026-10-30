import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from backend.app.core.database import Base, get_db
from backend.app.main import app
from backend.app.data.seed_data import seed_database
from backend.app.data import seed_data

TEST_DB_URL = "sqlite:///./test_nexora.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function", autouse=True)
def reset_db():
    # Fresh schema for every test
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    
    orig_engine = seed_data.engine
    orig_session = seed_data.SessionLocal
    seed_data.engine = test_engine
    seed_data.SessionLocal = TestingSessionLocal
    seed_database()
    seed_data.engine = orig_engine
    seed_data.SessionLocal = orig_session
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
