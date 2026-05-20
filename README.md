# Primetrade.ai Backend Assignment

A scalable REST API with JWT authentication, role-based access control, and full CRUD operations built with FastAPI and PostgreSQL.

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
| Frontend | Vanilla JS |
| API Docs | Swagger UI (auto-generated) |

---

## Features

- User registration and login with bcrypt password hashing
- JWT-based authentication with configurable expiry
- Role-based access control (user vs admin)
- Full CRUD for Tasks (Create, Read, Update, Delete)
- Protected routes — 401 if unauthenticated, 403 if insufficient role
- Auto-generated Swagger documentation at `/docs`
- CORS-enabled for frontend integration
- Input validation and structured error responses
- API versioning under `/api/v1/`

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
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   └── index.html           # Vanilla JS UI
└── README.md
```

---

## Setup and Installation

### Prerequisites
- Python 3.10+
- PostgreSQL running locally

### 1. Clone the repository
```bash
git clone https://github.com/Ryzuuuu/primetrade-assignment.git
cd primetrade-assignment
```

### 2. Create a virtual environment
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```
Edit `.env` with your values:
```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/primetrade_db
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Create the database
```sql
CREATE DATABASE primetrade_db;
```

### 6. Start the server
```bash
uvicorn app.main:app --reload
```

Server runs at `http://127.0.0.1:8000`

---

## API Reference

Swagger UI: **http://127.0.0.1:8000/docs**

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Register a new user | No |
| POST | `/api/v1/auth/login` | Login and receive JWT token | No |

### Tasks

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/tasks/` | Create a task | Yes |
| GET | `/api/v1/tasks/` | Get tasks (own tasks; all tasks if admin) | Yes |
| PUT | `/api/v1/tasks/{id}` | Update a task | Yes |
| DELETE | `/api/v1/tasks/{id}` | Delete a task | Yes |
| GET | `/api/v1/tasks/admin/all` | Get all tasks across users | Admin only |

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
Visit `http://localhost:3000`

The frontend supports user registration, login, JWT session management, and full task CRUD with success and error feedback.

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
- Ownership enforced on task mutations — users cannot modify other users' tasks
- Admin role required for elevated access endpoints

---

## Author

Neela — [github.com/Ryzuuuu](https://github.com/Ryzuuuu)
