from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.middleware.rate_limit import RateLimitMiddleware
from app.models.conversations import Conversation
from app.models.listing import Listing
from app.models.user import User


def _clear_rate_limiter(application) -> None:
    """Walk the middleware chain and reset all rate-limiter token buckets."""
    mw = application.middleware_stack
    while mw is not None:
        if isinstance(mw, RateLimitMiddleware):
            mw.buckets.clear()
            return
        mw = getattr(mw, "app", None)


@pytest.fixture()
def db_session():
    """Yield a SQLAlchemy session connected to a fresh in-memory database."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session = sessionmaker(bind=engine)
    session = testing_session()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def client(db_session):
    """Yield a FastAPI TestClient whose DB dependency points at the test session."""

    def _override():
        yield db_session

    app.dependency_overrides[get_db] = _override
    with TestClient(app, raise_server_exceptions=False) as c:
        _clear_rate_limiter(app)
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Factory fixtures – each returns a callable that creates ORM objects in the
# test database.  An internal counter auto-generates unique field values so
# tests can call the factory multiple times without collisions.
# ---------------------------------------------------------------------------


@pytest.fixture()
def make_user(db_session):
    counter = [0]

    def _factory(
        *,
        email: str | None = None,
        username: str | None = None,
        password_hash: str = "fakehash_abc123",
    ) -> User:
        counter[0] += 1
        user = User(
            email=email or f"user{counter[0]}@example.com",
            username=username or f"testuser{counter[0]}",
            password_hash=password_hash,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _factory


@pytest.fixture()
def make_listing(db_session):
    counter = [0]

    def _factory(host_id: int, **overrides) -> Listing:
        counter[0] += 1
        now = datetime.now(timezone.utc)
        defaults: dict = {
            "host_id": host_id,
            "title": f"Test Listing {counter[0]}",
            "description": "A test listing description",
            "price": 1000.0,
            "location": "Test City",
            "room_type": "single",
            "sqft": 500,
            "start_date": now,
            "end_date": now + timedelta(days=30),
            "college_id": 1,
            "latitude": 40.7128,
            "longitude": -74.006,
        }
        defaults.update(overrides)
        listing = Listing(**defaults)
        db_session.add(listing)
        db_session.commit()
        db_session.refresh(listing)
        return listing

    return _factory


@pytest.fixture()
def make_conversation(db_session):
    def _factory(
        listing_id: int, user_one_id: int, user_two_id: int
    ) -> Conversation:
        uid1, uid2 = sorted([user_one_id, user_two_id])
        convo = Conversation(
            listing_id=listing_id, user_one_id=uid1, user_two_id=uid2
        )
        db_session.add(convo)
        db_session.commit()
        db_session.refresh(convo)
        return convo

    return _factory
