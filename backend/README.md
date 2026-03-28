# Sublease Marketplace API — Backend

FastAPI backend for the Sublease Gang platform, providing REST endpoints for sublease listings, user accounts, messaging, and map search.

## Tech Stack

- **Framework:** FastAPI
- **Database:** SQLite (default) via SQLAlchemy ORM
- **Package Manager:** [uv](https://docs.astral.sh/uv/)
- **Linter:** Ruff
- **Auth tokens:** PyJWT + Argon2 password hashing (pwdlib)
- **Python:** 3.13+

## Getting Started

### 1. Install dependencies

```bash
cd backend
uv sync
```

### 2. Configure environment (optional)

Create a `.env` file in the `backend/` directory to override defaults:

```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///./sublease_marketplace.db
CORS_ORIGINS=["http://localhost:3000"]
ENVIRONMENT=development
```

### 3. Run the dev server

```bash
cd backend
uv run uvicorn app.main:app --reload --app-dir src
```

The API will be available at **http://localhost:8000**.

### 4. View API docs

FastAPI auto-generates interactive docs:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 5. Run tests

```bash
cd backend
uv run pytest
```

### 6. Lint / format

```bash
cd backend
uv run ruff check src/
uv run ruff format src/
```

## Project Structure

```
backend/
├── src/app/
│   ├── main.py                  # FastAPI app, middleware registration
│   ├── api/v1/routes.py         # Versioned API router (/api/v1)
│   ├── core/
│   │   ├── settings.py          # App config (pydantic-settings, reads .env)
│   │   └── database.py          # SQLAlchemy engine, session, Base
│   ├── models/
│   │   ├── user.py              # User account
│   │   ├── profiles.py          # User profile (1-to-1 with User)
│   │   ├── listing.py           # Sublease listing
│   │   ├── conversations.py     # Conversation (between two users on a listing)
│   │   ├── messages.py          # Chat message
│   │   ├── token.py             # JWT refresh/access token records
│   │   └── crud.py              # Shared CRUD helpers
│   ├── routes/
│   │   ├── auth.py              # Signup, login, logout, password reset
│   │   ├── listings.py          # CRUD + search/filter for listings
│   │   ├── users.py             # User profile management
│   │   ├── conversations.py     # Messaging / conversations
│   │   └── map.py               # Map-based listing search + geocode
│   ├── schemas/                 # Pydantic request/response schemas
│   └── middleware/
│       ├── request_id.py        # Adds X-Request-ID to every response
│       ├── logging.py           # Logs method, path, status, duration
│       ├── security_headers.py  # Security headers (HSTS, CSP, etc.)
│       └── rate_limit.py        # Token-bucket rate limiting
├── pyproject.toml
└── uv.lock
```

## API Routes

All routes are prefixed with `/api/v1`.

### Auth (`/api/v1/auth`)
| Method | Path                | Description                  | Status      |
|--------|---------------------|------------------------------|-------------|
| POST   | `/signup`           | Create a new account         | Stub (TODO) |
| POST   | `/login`            | Login, returns tokens        | Stub (TODO) |
| POST   | `/refresh`          | Refresh access token         | Stub (TODO) |
| POST   | `/logout`           | Invalidate refresh token     | Stub (TODO) |
| POST   | `/forgot_password`  | Send password reset email    | Stub (TODO) |
| PUT    | `/reset_password`   | Reset password with token    | Stub (TODO) |

### Listings (`/api/v1/listings`)
| Method | Path                | Description                          | Status      |
|--------|---------------------|--------------------------------------|-------------|
| GET    | `/`                 | Search listings with filters/sorting | Implemented |
| GET    | `/filters`          | Get available filter options         | Implemented |
| GET    | `/{listing_id}`     | View a single listing                | Implemented |
| POST   | `/`                 | Create a new listing                 | Needs auth  |
| PUT    | `/{listing_id}`     | Update a listing                     | Needs auth  |
| DELETE | `/{listing_id}`     | Delete a listing                     | Needs auth  |

### Users (`/api/v1/users`)
| Method | Path              | Description                    | Status      |
|--------|-------------------|--------------------------------|-------------|
| GET    | `/me`             | Get current user's profile     | Needs auth  |
| PATCH  | `/me`             | Update current user's profile  | Needs auth  |
| DELETE | `/me`             | Delete current user's account  | Needs auth  |
| PUT    | `/me/password`    | Change password                | Needs auth  |
| GET    | `/{user_id}`      | Get a user's public profile    | Implemented |
| POST   | `/`               | Create a new user              | Implemented |

### Conversations (`/api/v1/conversations`)
| Method | Path                              | Description              | Status      |
|--------|-----------------------------------|--------------------------|-------------|
| GET    | `/`                               | List user's conversations| Stub (TODO) |
| POST   | `/`                               | Create a conversation    | Stub (TODO) |
| GET    | `/{conversation_id}/messages`     | Get messages             | Stub (TODO) |
| POST   | `/{conversation_id}/messages`     | Send a message           | Stub (TODO) |

### Map (`/api/v1/map`)
| Method | Path          | Description                           | Status      |
|--------|---------------|---------------------------------------|-------------|
| GET    | `/listings`   | Get listing pins within map bounds    | Implemented |
| GET    | `/geocode`    | Convert address to coordinates        | Stub (TODO) |

## Middleware Stack

Middleware executes in this order (top = outermost):

1. **CORS** — Allows configured frontend origins
2. **Rate Limiting** — Token-bucket per IP for auth/messaging/listing endpoints
3. **Security Headers** — X-Content-Type-Options, X-Frame-Options, HSTS (production only), etc.
4. **Logging** — Logs request method, path, status code, and duration
5. **Request ID** — Attaches a unique `X-Request-ID` header to every response

## Database

SQLite by default (file: `sublease_marketplace.db`). Tables are auto-created on startup via `Base.metadata.create_all()`. Override `DATABASE_URL` in `.env` to use PostgreSQL or another database.
