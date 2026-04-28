# Backend Test Suite

Comprehensive unit and integration tests for the Sublease Gang backend API using `pytest`.

## Testing Architecture

The test suite follows a layered testing approach:

- **Unit tests** verify service, repository, schema, and auth behavior in isolation.
- **Integration tests** verify HTTP routes end-to-end through FastAPI.

## Directory Structure

```text
tests/
├── conftest.py                         # Shared pytest fixtures/factories
├── unit/                               # Core/domain-level tests
│   ├── test_auth.py
│   ├── test_auth_tokens.py
│   ├── test_conversation_message_service.py
│   ├── test_dependencies.py
│   ├── test_listing_service.py
│   ├── test_repository.py
│   ├── test_schemas.py
│   └── test_user_service.py
└── integration/                        # Route/endpoint tests
    ├── test_routes_auth.py
    ├── test_routes_conversations.py
    ├── test_routes_listings.py
    ├── test_routes_map.py
    └── test_routes_users.py
```

## Prerequisites

Install backend dependencies:

```bash
cd backend
uv sync --group dev
```

## Running Tests

From the `backend/` directory:

```bash
# Run all tests
uv run python -m pytest tests -v
```

### Run by Category

```bash
# Unit tests only
uv run python -m pytest tests/unit -v

# Integration tests only
uv run python -m pytest tests/integration -v
```

### Run a Specific File

```bash
uv run python -m pytest tests/unit/test_repository.py -v
uv run python -m pytest tests/integration/test_routes_auth.py -v
```

### Run a Specific Class or Test

```bash
uv run python -m pytest tests/unit/test_repository.py::TestUserRepository -v
uv run python -m pytest tests/integration/test_routes_auth.py::test_login_success -v
```

## Shared Fixtures (`conftest.py`)

`tests/conftest.py` provides reusable fixtures used across both test categories:

- `db_session`: Fresh in-memory SQLite session per test
- `client`: FastAPI `TestClient` with dependency override for test DB
- `make_user`: User factory fixture
- `make_listing`: Listing factory fixture
- `make_conversation`: Conversation factory fixture

This keeps tests isolated, deterministic, and free of cross-test side effects.

## Test Database

Tests run against an in-memory SQLite database (`sqlite:///:memory:`):

- tables are created for each test session,
- data is isolated per test run,
- teardown is automatic after each test.

No external DB setup is required for routine local or CI test runs.

## CI-Friendly Commands

```bash
# Standard test run (exit code indicates pass/fail)
uv run python -m pytest tests

# Optional coverage
uv run python -m coverage run -m pytest tests
uv run python -m coverage report
```

## Troubleshooting

```bash
# More verbose output
uv run python -m pytest tests -vv

# Stop on first failure
uv run python -m pytest tests -x

# Show detailed tracebacks
uv run python -m pytest tests --tb=long
```
