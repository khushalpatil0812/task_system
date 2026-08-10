# TaskFlow — Team Task Manager

TaskFlow is a responsive team task-management application with a React + TypeScript frontend and a FastAPI + SQLAlchemy backend. It provides JWT authentication, secure password hashing, project teams, task workflows, dashboards, and server-enforced role-based access control (RBAC).

## Features

- User signup, login, logout, profile updates, and password changes
- JWT-protected REST API with bcrypt password hashing
- Admin and Member roles with backend authorization
- Admin creation of member accounts and an All Members directory
- Projects with descriptions and team-member assignment
- Tasks with assignees, due dates, priorities, statuses, filters, search, and deletion
- Task workflow: **Todo**, **In Progress**, and **Completed**
- Dashboard totals, recent tasks, upcoming deadlines, and overdue-task metrics
- Responsive React interface, toast notifications, and dark-mode toggle

## Roles and permissions

The application has two roles: **Admin** and **Member**. Authorization is enforced by the API; hiding a frontend button alone does not grant or remove permission.

| Action | Admin | Member |
| --- | --- | --- |
| Sign up and log in | Yes | Yes |
| View dashboard | Yes | Yes |
| View permitted projects and tasks | Yes | Yes |
| Create, update, or delete projects | Yes | No |
| Create member accounts and view all members | Yes | No |
| Set project team members | Yes | No |
| Create, assign, edit, or delete tasks | Yes | No |
| Update task status | Any task | Only tasks assigned to them |

### RBAC flow

1. A user logs in with email and password.
2. The backend verifies the password hash and issues a JWT containing the user ID and role.
3. Protected requests send `Authorization: Bearer <token>`.
4. The API validates the JWT, loads the current user from the database, and checks permissions.
5. Invalid tokens return `401 Unauthorized`; prohibited actions return `403 Forbidden`.

The database role is authoritative. This means role changes take effect even when a user still has an older token.

## Technology

| Area | Technology |
| --- | --- |
| Frontend | React 19, TypeScript, Vite, React Router, Axios, React Hook Form, Recharts |
| Backend | FastAPI, SQLAlchemy 2, Pydantic |
| Authentication | JWT (`python-jose`) and bcrypt (`passlib`) |
| Database | SQLite by default; MySQL supported through PyMySQL |

## Run locally

### Prerequisites

- Python 3.12 or later
- Node.js 20 or later
- npm

### 1. Start the backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API is available at `http://127.0.0.1:8000` and OpenAPI documentation is at `http://127.0.0.1:8000/docs`.

### 2. Start the frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Open `http://127.0.0.1:5173` in a browser.

### 3. Production build

```powershell
cd frontend
npm run build
```

The generated frontend files are written to `frontend/dist`.

## Database configuration

### Default: SQLite

No database setup is needed for local development. If `DATABASE_URL` is unset, the backend uses:

```text
sqlite:///./team_tasks.db
```

The database file is created in `backend/team_tasks.db`, and the application creates the required tables at startup:

- `users`
- `projects`
- `tasks`
- `project_members`

### Optional: MySQL

Create `backend/.env` from the example file and provide a real MySQL connection string:

```powershell
Copy-Item .env.example .env
```

```env
DATABASE_URL=mysql+pymysql://MYSQL_USER:MYSQL_PASSWORD@localhost:3306/team_tasks
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Create the MySQL database before starting the API:

```sql
CREATE DATABASE team_tasks;
```

Do not commit `.env` files, database passwords, tokens, or real user passwords.

## Environment variables

| Variable | Required | Description |
| --- | --- | --- |
| `DATABASE_URL` | No | SQLAlchemy URL. Defaults to the local SQLite database. |
| `SECRET_KEY` | Recommended | Long, random key used to sign JWTs. |
| `ALGORITHM` | No | JWT algorithm; defaults to `HS256`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Token lifetime; defaults to `1440`. |
| `CORS_ORIGINS` | No | Comma-separated allowed web origins. |
| `VITE_API_URL` | No | Frontend API base URL, such as `http://127.0.0.1:8000/api`. |

## API overview

All application endpoints are under `/api`.

| Method | Endpoint | Access | Description |
| --- | --- | --- | --- |
| `GET` | `/health` | Public | API health check |
| `POST` | `/signup` | Public | Create an account; the first account is an admin |
| `POST` | `/login` | Public | Log in and receive a JWT |
| `GET`, `PUT` | `/profile` | Authenticated | View or update own profile |
| `GET`, `POST` | `/users` | Admin | List members or create a member account |
| `GET`, `POST` | `/projects` | Authenticated / Admin | List visible projects or create one |
| `GET`, `PUT`, `DELETE` | `/projects/{project_id}` | Authenticated / Admin | Read, update, or delete a project |
| `GET`, `POST` | `/tasks` | Authenticated / Admin | List visible tasks or create one |
| `PUT`, `DELETE` | `/tasks/{task_id}` | Assigned member or Admin / Admin | Update or delete a task |
| `GET` | `/dashboard` | Authenticated | Dashboard statistics and task summaries |

Tasks may be assigned only to members of their project. Members can submit only a status update for their own assigned tasks; the backend rejects other task fields and other members' tasks.

## Deployment notes

The project can be deployed with a FastAPI host (for example Railway) and a static frontend host (for example Vercel).

1. Deploy `backend` with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
2. Set backend environment variables, including a production `SECRET_KEY`, MySQL `DATABASE_URL`, and the deployed frontend origin in `CORS_ORIGINS`.
3. Deploy `frontend` with build command `npm run build` and output directory `dist`.
4. Set `VITE_API_URL` to the deployed API URL ending in `/api`.

For production database changes, add managed migrations such as Alembic before rollout.
