# Team Task Manager

A production-oriented, responsive team task-management application. It has a React 19 + TypeScript frontend and a FastAPI + SQLAlchemy backend, secured by JWT authentication and role-based access controls.

## Features

- JWT signup/login/logout, bcrypt password hashing, protected routes
- Admin and member roles, with server-side authorization (the very first account is the setup admin; later registrations are members)
- Project teams, task assignment, filters, search, due-date ordering, task lifecycle
- Dashboard metrics, workload chart, recent tasks and upcoming deadlines
- Profile and password management, responsive interface, toast feedback and dark-mode toggle

## Local installation

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

The frontend runs on `http://localhost:5173`; API docs are at `http://localhost:8000/docs`.

## Environment variables

Backend (`backend/.env`):

| Variable | Description |
| --- | --- |
| `DATABASE_URL` | MySQL SQLAlchemy URL, e.g. `mysql+pymysql://user:password@host:3306/team_tasks` |
| `SECRET_KEY` | Long random JWT signing secret |
| `ALGORITHM` | JWT algorithm (`HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime in minutes |
| `CORS_ORIGINS` | Comma-separated permitted web origins |

Frontend (`frontend/.env`): `VITE_API_URL=https://your-api.railway.app/api`

## Deployment

### Railway (API and MySQL)

1. Create a Railway MySQL service, then set `DATABASE_URL` to its connection string in the API service variables.
2. Deploy `backend` as the Railway service root. Use start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
3. Configure `SECRET_KEY`, `ALGORITHM=HS256`, `ACCESS_TOKEN_EXPIRE_MINUTES=1440`, and `CORS_ORIGINS` with the Vercel production URL.
4. The schema is created automatically at backend startup. For teams needing managed migrations, add Alembic before first production rollout.

### Vercel (web app)

1. Import the repository and set Vercel's Root Directory to `frontend`.
2. Set `VITE_API_URL` to the Railway API URL ending in `/api`.
3. Build command: `npm run build`; output directory: `dist`.

## API

Endpoints are namespaced under `/api`: `POST /signup`, `POST /login`, `GET/PUT /profile`, `GET /users`, CRUD `/projects`, CRUD `/tasks`, and `GET /dashboard`. Send `Authorization: Bearer <token>` for protected endpoints. OpenAPI documentation is automatically available at `/docs`.
"# task_system" 
