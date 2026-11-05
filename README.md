# Primetrade.ai Backend Assignment

[![CI](https://github.com/Ryzuuuu/primetrade-assignment/actions/workflows/ci.yml/badge.svg)](https://github.com/Ryzuuuu/primetrade-assignment/actions/workflows/ci.yml)

A scalable REST API with JWT authentication, role-based access control, and full CRUD operations built with FastAPI and PostgreSQL, plus a small vanilla-JS frontend to exercise it.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Authentication | JWT (python-jose) |
| Password Hashing | bcrypt (passlib) |
| Validation | Pydantic |
| Testing | pytest, Ruff (lint), GitHub Actions (CI) |
| Frontend | Vanilla JS |
| API Docs | Swagger UI (auto-generated) |

---

## Features

- User registration and login with bcrypt password hashing
- JWT-based authentication with configurable expiry
- Role-based access control (user vs admin)
- Full CRUD for Tasks (Create, Read, Update, Delete)
- Protected routes: 401 if unauthenticated, 403 if insufficient role
- Auto-generated Swagger documentation at `/docs`
- Configurable CORS for frontend integration
- Input validation and structured error responses
- API versioning under `/api/v1/`
- Automated test suite (runs without PostgreSQL) and CI on every push

---

## Project Structure

```
primetrade-assignment/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # App entry point, middleware, router registration
│   │   ├── database.py      # DB connection and session management
│   │   ├── models.py        # SQLAlchemy table definitions (User, Task)
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   ├── auth.py          # JWT creation and bcrypt hashing
│   │   ├── dependencies.py  # get_current_user and require_admin guards
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── auth.py      # /register and /login endpoints
│   │       └── tasks.py     # CRUD task endpoints
│   ├── tests/               # pytest suite (auth, RBAC, task CRUD)
│   ├── .env.example
│   ├── pytest.ini
│   ├── requirements.txt
│   ├── requirements-dev.txt # Runtime deps + pytest, httpx, ruff
│   └── ruff.toml
├── frontend/
│   └── index.html           # Vanilla JS UI
├── .github/workflows/ci.yml # Lint + tests on push / PR
└── README.md
```

---

## Setup and Installation

### Prerequisites
- Python 3.11+
- PostgreSQL running locally

### 1. Clone the repository
```bash
git clone https://github.com/Ryzuuuu/primetrade-assignment.git
cd primetrade-assignment
```

### 2. Create the database
```sql
CREATE DATABASE primetrade_db;
```

### 3. Create a virtual environment
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure environment variables
```bash
cp .env.example .env         # Windows: copy .env.example .env
```
Edit `.env` with your values:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQLAlchemy connection string | required |
| `SECRET_KEY` | Key used to sign JWTs. Generate one with `python -c "import secrets; print(secrets.token_urlsafe(32))"` | required |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `30` |
| `CORS_ORIGINS` | Comma-separated origins allowed to call the API | `http://localhost:3000,http://127.0.0.1:3000` |

### 6. Start the server
```bash
uvicorn app.main:app --reload
```

Server runs at `http://127.0.0.1:8000`. Tables are created automatically on first start.

---

## API Reference

Swagger UI: **http://127.0.0.1:8000/docs**

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Register a new user (JSON body) | No |
| POST | `/api/v1/auth/login` | Login and receive JWT token (form-encoded body) | No |

### Tasks

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/tasks/` | Create a task | Yes |
| GET | `/api/v1/tasks/` | Get tasks (own tasks; all tasks if admin) | Yes |
| PUT | `/api/v1/tasks/{id}` | Update a task (partial updates supported) | Yes (owner or admin) |
| DELETE | `/api/v1/tasks/{id}` | Delete a task | Yes (owner or admin) |
| GET | `/api/v1/tasks/admin/all` | Get all tasks across users | Admin only |

### Validation rules

| Field | Rule |
|-------|------|
| `username` | 3-50 characters, unique |
| `email` | valid email address, unique |
| `password` | 6-128 characters |
| `title` | 1-200 characters |
| `description` | optional, up to 2000 characters |

### Status codes

| Code | Meaning |
|------|---------|
| 201 | Resource created |
| 204 | Deleted, no content |
| 400 | Duplicate email or username |
| 401 | Missing, invalid or expired token; wrong credentials |
| 403 | Not the owner of the task, or admin role required |
| 404 | Task not found |
| 422 | Request body failed validation |

### Example

```bash
# Register
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com", "password": "secret123"}'

# Login (form-encoded) and copy the access_token from the response
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -d "username=alice&password=secret123"

# Create a task
curl -X POST http://127.0.0.1:8000/api/v1/tasks/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Ship the assignment", "description": "Write the README"}'
```

### Creating an admin

Every new account gets the `user` role. To promote one, update it in the database (authorization is checked against the stored role on every request; log in again so the frontend shows the new role badge):

```sql
UPDATE users SET role = 'admin' WHERE username = 'alice';
```

---

## Authentication Flow

```
1. POST /register  ->  password hashed with bcrypt  ->  user saved to DB
2. POST /login     ->  password verified             ->  JWT token returned
3. Include token in subsequent requests:
   Authorization: Bearer <token>
4. Server decodes token  ->  identifies user and role
5. Admin-only routes verify role before granting access
```

---

## Frontend

Open a second terminal and serve the frontend:
```bash
cd frontend
python -m http.server 3000
```
Visit `http://localhost:3000`. The UI expects the API at `http://localhost:8000` (change the `API` constant in `index.html` if you run it elsewhere) and the frontend origin must be listed in `CORS_ORIGINS`.

The frontend supports user registration, login, JWT session management, and full task CRUD with success and error feedback.

---

## Testing

The tests use an in-memory SQLite database, so PostgreSQL is not needed:

```bash
cd backend
pip install -r requirements-dev.txt
pytest
ruff check .
```

They cover registration and login, token validation, task CRUD, ownership checks and admin-only access.

---

## Scalability Notes

| Concern | Approach |
|---------|----------|
| Stateless authentication | JWT allows any server instance to handle any request, enabling horizontal scaling |
| Microservices | Auth and Tasks are modular routers that can be extracted into independent services |
| Caching | Redis can cache GET /tasks responses to reduce database load |
| Load balancing | Stateless design is compatible with any load balancer (Nginx, AWS ALB) |
| Database scaling | Read replicas for high read traffic; connection pooling managed by SQLAlchemy |
| Deployment | Each service can be containerised with Docker and orchestrated via Kubernetes |

---

## Security Practices

- Passwords hashed with bcrypt (one-way, irreversible)
- JWT tokens have a configurable expiry window
- Environment secrets stored in `.env` and excluded from version control
- All inputs validated via Pydantic before reaching the database
- Ownership enforced on task mutations: users cannot modify other users' tasks
- Admin role required for elevated access endpoints
- Disabled accounts (`is_active = false`) cannot log in or use existing tokens
- The frontend escapes user-supplied text before rendering it

---

## Author

Neela — [github.com/Ryzuuuu](https://github.com/Ryzuuuu)
