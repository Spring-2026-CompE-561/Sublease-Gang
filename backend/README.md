# Sublease Marketplace

A web marketplace for college students to list and find rooms for subleasing.

There is no central place for college students to list or find subleases. This project creates a user-friendly website that allows students to find rooms available in their area within their desired time frame.

The website is limited to matching people with available rooms. Payment processing and lease signing are left to the discretion of the current resident.

## Features

- Homepage with sublease listings (including pictures, room size, price, and time frame)
- User authentication (JWT with Argon2 password hashing)
- Page to create listings
- Filtering options:
  - College
  - Time frame
  - Room size
  - Price
- Messaging system between users
- Map to display locations of listings

## Tech Stack

- **Backend:** Python 3.13+, FastAPI, SQLAlchemy, Pydantic v2
- **Frontend:** Next.js 16, React 19, TypeScript, Tailwind CSS v4
- **Database:** SQLite (development)
- **Package Management:** [uv](https://docs.astral.sh/uv/) (backend), npm (frontend)

## Architecture

The backend follows a **Routes → Services → Repository → Models** layered architecture:

- **Routes** handle HTTP concerns (request parsing, response codes, error mapping)
- **Services** contain business logic and orchestrate repository calls
- **Repository** encapsulates all database queries and raises domain exceptions
- **Models** define SQLAlchemy table schemas

## Project Structure

```
Sublease-Gang/
├── backend/
│   ├── src/
│   │   └── app/
│   │       ├── api/v1/          # API route registration
│   │       ├── core/            # Settings, database, auth, dependencies
│   │       ├── errors/          # Custom exception handlers (auth, conflict, not_found, permission, validation, server)
│   │       ├── middleware/      # Request ID, logging, rate limiting, security headers
│   │       ├── models/          # SQLAlchemy models (user, listing, profile, conversation, message, token)
│   │       ├── repository/      # Database access layer with domain exceptions
│   │       ├── routes/          # Route handlers (auth, users, listings, map, conversations)
│   │       ├── schemas/         # Pydantic request/response schemas
│   │       ├── services/        # Business logic (user, listing, profile, conversation, message, token)
│   │       └── main.py          # FastAPI app entry point
│   ├── tests/                   # Pytest test suite (repository, routes, schemas, auth)
│   ├── pyproject.toml           # Python dependencies & tool config
│   └── sublease-gang.yaml       # OpenAPI specification
├── frontend/
│   ├── app/                     # Next.js app directory
│   ├── public/                  # Static assets
│   ├── package.json             # Node dependencies
│   └── ...
└── README.md
```

## Prerequisites

- **Python 3.13+**
- **Node.js 18+** and **npm**
- **[uv](https://docs.astral.sh/uv/)** (Python package manager)

Install uv if you don't have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Setup

### Backend

```bash
cd backend

# Install all dependencies (creates a virtual environment automatically)
uv sync --group dev
```

Create a `.env` file in the `backend/` directory (optional — defaults are provided):

```env
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///./sublease_marketplace.db
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install
```

## Running the Application

### Backend (API server)

```bash
cd backend

# Start the FastAPI development server
uv run fastapi dev src/app/main.py
```

The API will be available at **http://localhost:8000**.

Interactive API docs (Swagger UI) are at **http://localhost:8000/docs**.

### Frontend (Next.js)

```bash
cd frontend

# Start the Next.js development server
npm run dev
```

The frontend will be available at **http://localhost:3000**.

## Running Tests

```bash
cd backend

# Run the full test suite
uv run pytest

# Run with verbose output
uv run pytest -v

# Run a specific test file
uv run pytest tests/test_repository.py

# Run a specific test class or function
uv run pytest tests/test_repository.py::TestUserRepository
uv run pytest tests/test_schemas.py::TestUserCreate::test_valid
```

Tests use an **in-memory SQLite database** so no external database setup is required.

## Linting

### Backend

```bash
cd backend

# Run ruff linter
uv run ruff check .

# Auto-fix lint issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

### Frontend

```bash
cd frontend

# Run ESLint
npm run lint
```

## API Endpoints

The full OpenAPI specification is available in [`backend/sublease-gang.yaml`](backend/sublease-gang.yaml).

| Method | Endpoint                              | Description                      |
| ------ | ------------------------------------- | -------------------------------- |
| POST   | `/api/v1/auth/signup`                 | Create a new account             |
| POST   | `/api/v1/auth/login`                  | Log in                           |
| POST   | `/api/v1/auth/logout`                 | Log out (authenticated)          |
| POST   | `/api/v1/auth/refresh`                | Refresh tokens (stub)            |
| POST   | `/api/v1/auth/forgot_password`        | Request password reset (stub)    |
| PUT    | `/api/v1/auth/reset_password`         | Reset password (stub)            |
| POST   | `/api/v1/users/`                      | Create a new user                |
| GET    | `/api/v1/users/me`                    | Get current user profile         |
| PATCH  | `/api/v1/users/me`                    | Update current user profile      |
| DELETE | `/api/v1/users/me`                    | Delete current user account      |
| PUT    | `/api/v1/users/me/password`           | Change password                  |
| GET    | `/api/v1/users/{id}`                  | Get user by ID                   |
| POST   | `/api/v1/listings/`                   | Create a listing (authenticated) |
| GET    | `/api/v1/listings/`                   | Search listings with filters     |
| GET    | `/api/v1/listings/filters`            | Get available filter options     |
| GET    | `/api/v1/listings/{id}`               | Get a specific listing           |
| PUT    | `/api/v1/listings/{id}`               | Update a listing (owner only)    |
| DELETE | `/api/v1/listings/{id}`               | Delete a listing (owner only)    |
| GET    | `/api/v1/map/listings`                | Get listings within map bounds   |
| GET    | `/api/v1/map/geocode`                 | Geocode an address               |
| GET    | `/api/v1/conversations/`              | List conversations (stub)        |
| POST   | `/api/v1/conversations/`              | Create a conversation (stub)     |
| GET    | `/api/v1/conversations/{id}/messages` | List messages (authenticated)    |
| POST   | `/api/v1/conversations/{id}/messages` | Send a message (authenticated)   |
