# Task & Habit API

A REST API for managing personal tasks and daily habits. Users can register, authenticate with JWT tokens, create and manage tasks, track habits with daily check-ins, and view streak statistics.

## Technologies

| Technology | Purpose |
|---|---|
| [FastAPI](https://fastapi.tiangolo.com/) | Web framework and API routing |
| [Uvicorn](https://www.uvicorn.org/) | ASGI server (included via `fastapi[standard]`) |
| [SQLAlchemy](https://www.sqlalchemy.org/) | ORM and database access |
| [SQLite](https://www.sqlite.org/) | Default database (via connection URL in `.env`) |
| [Pydantic](https://docs.pydantic.dev/) | Request/response validation and settings |
| [python-jose](https://python-jose.readthedocs.io/) | JWT token creation and verification |
| [Passlib](https://passlib.readthedocs.io/) + [bcrypt](https://github.com/pyca/bcrypt/) | Password hashing |
| [python-multipart](https://github.com/Kludex/python-multipart) | Form data parsing (OAuth2 login) |

## Project Structure

```
task-habit-api/
├── app/
│   ├── main.py              # FastAPI app entry point, router registration
│   ├── database.py          # SQLAlchemy engine, session, and Base model
│   ├── models.py            # SQLAlchemy ORM models (User, Task, Habit, HabitLog)
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── dependencies.py      # Shared dependencies (e.g. get_current_user)
│   ├── core/
│   │   ├── config.py        # Environment-based settings
│   │   └── security.py      # Password hashing and JWT utilities
│   ├── api/
│   │   ├── main.py          # API router assembly
│   │   ├── root.py          # Landing page
│   │   ├── auth.py          # Registration, login, and current user
│   │   ├── tasks.py         # Task CRUD and search
│   │   └── habits.py        # Habit management, check-ins, and stats
├── requirements.txt         # pip dependencies (also declared in pyproject.toml)
├── pyproject.toml           # Vercel / uv dependency manifest
├── .env.example             # Environment variable template
├── .env                     # Local environment variables (not committed)
└── README.md
```

### Data Models

- **User** — owns tasks and habits; authenticated via JWT
- **Task** — title, description, priority, completion status
- **Habit** — named habit tracked by the user
- **HabitLog** — one check-in record per habit per day

## Prerequisites

- Python 3.11+ (tested with Python 3.14)
- `pip` and `venv`

## Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd task-habit-api
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS / Linux
   # venv\Scripts\activate    # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   Or with [uv](https://docs.astral.sh/uv/) (matches the [Vercel FastAPI example](https://github.com/vercel/vercel/tree/main/examples/fastapi)):

   ```bash
   uv sync
   ```

4. **Configure environment variables**

   Copy `.env.example` to `.env` and update the placeholder values:

   ```bash
   cp .env.example .env
   ```

   Then open `.env` and change at least `SECRET_KEY` and `SQLALCHEMY_DATABASE_URL` (for example, replace `your-db-name-db` with your preferred SQLite filename):

   ```env
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   SECRET_KEY=a-very-secret-key-change-this-later
   SQLALCHEMY_DATABASE_URL=sqlite:///./your-db-name-db.db
   ```

   | Variable | Required | Description |
   |---|---|---|
   | `SECRET_KEY` | Yes | Secret used to sign JWT tokens |
   | `SQLALCHEMY_DATABASE_URL` | Yes | Database connection string |
   | `ALGORITHM` | No | JWT signing algorithm (default: `HS256`) |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Token lifetime in minutes (default: `30`) |

   Tables are created automatically on startup via SQLAlchemy's `create_all`.

## Running the Server

**Development** (with auto-reload):

```bash
fastapi dev app/main.py
```

**Production-style**:

```bash
fastapi run app/main.py
```

The API is available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

### Interactive Docs

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## API Overview

All task and habit endpoints require a Bearer token. Obtain one by registering and logging in.

### Authentication (`/auth`)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Create a new user account |
| `POST` | `/auth/login` | Login and receive a JWT access token |
| `GET` | `/auth/me` | Get the currently authenticated user |

**Login** expects form-urlencoded data (`username`, `password`), not JSON.

### Tasks (`/tasks`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/tasks` | List all tasks for the current user |
| `GET` | `/tasks/{id}` | Get a single task |
| `POST` | `/tasks` | Create a new task |
| `PUT` | `/tasks/{id}` | Update a task |
| `DELETE` | `/tasks/{id}` | Delete a task |
| `GET` | `/tasks/search?title=...` | Search tasks by title |

### Habits (`/habits`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/habits` | List all habits for the current user |
| `POST` | `/habits` | Create a new habit |
| `POST` | `/habits/{id}/checkin` | Check in a habit for today |
| `GET` | `/habits/{habit_id}/stats` | Get streak and check-in statistics |

## Quick Start Example

```bash
# Register a user
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "secret123"}'

# Login and save the token
curl -X POST http://127.0.0.1:8000/auth/login \
  -d "username=demo&password=secret123"

# Create a task (replace TOKEN with the access_token from login)
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk and eggs", "priority": 2}'

# Create a habit and check in
curl -X POST http://127.0.0.1:8000/habits \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Morning run"}'

curl -X POST http://127.0.0.1:8000/habits/1/checkin \
  -H "Authorization: Bearer TOKEN"
```

## Deploying to Vercel

This project follows the [Vercel FastAPI deployment guide](https://vercel.com/docs/frameworks/backend/fastapi). Vercel auto-detects the `app` instance in `app/main.py`.

### 1. Set environment variables in Vercel

In your Vercel project dashboard, go to **Settings → Environment Variables** and add:

| Variable | Value |
|---|---|
| `SECRET_KEY` | A strong random secret for JWT signing |
| `SQLALCHEMY_DATABASE_URL` | `sqlite:////tmp/task-habits.db` |
| `ALGORITHM` | `HS256` (optional) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` (optional) |

Use `/tmp` for SQLite on Vercel because the filesystem is writable there. Note that data in `/tmp` is ephemeral and may not persist between function invocations.

### 2. Deploy

If the GitHub repo is already connected to Vercel, push these changes to trigger a deployment:

```bash
git add .
git commit -m "Configure FastAPI for Vercel deployment"
git push
```

Or deploy manually with the Vercel CLI:

```bash
npm install -g vercel
vercel --prod
```

### 3. Verify

After deployment:

- Health check: `https://<your-project>.vercel.app/`
- API docs: `https://<your-project>.vercel.app/docs`

### Local development with Vercel CLI

```bash
pip install -r requirements.txt
vercel dev
```
