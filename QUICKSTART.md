# OurMES Local Development Quickstart

This guide helps you run the OurMES backend (Django) and frontend (Vue/Vite) on your local machine with SQLite for development.

## Prerequisites

- **Python 3.9+** (tested on Python 3.13)
- **Node.js 16+** and npm
- **bash** shell

## Repository Layout Cheat Sheet

```
backend/
└── mes/plugins/<plugin>/
    ├── domain/        # Django models + domain helpers
    ├── application/   # orchestration/services
    └── api/           # DRF serializers, routers, viewsets

frontend/src/
├── core/              # router, shared stores, Axios client
└── modules/           # feature packages (pages + services + stores)
```

## Quick Start

From the `OurMES/` directory, run:

```bash
bash run-local.sh
```

Or make it executable and run directly:

```bash
chmod +x run-local.sh
./run-local.sh
```

## What the Script Does

1. **Creates Python venv** at `backend/.venv` if missing
2. **Installs backend dependencies** from `backend/requirements.txt`
3. **Applies migrations** to SQLite (`backend/db.sqlite3`)
4. **Loads sample data** (companies, products, orders, users)
5. **Starts Django dev server** on `http://localhost:8000`
6. **Installs frontend deps** (npm) if missing
7. **Starts Vite dev server** on `http://localhost:5173`

Press **Ctrl+C** to stop both servers cleanly.

## Accessing the App

- **Frontend**: http://localhost:5173/
- **Backend API**: http://localhost:8000/api/
- **Django Admin**: http://localhost:8000/admin/
- **Swagger/OpenAPI**: http://localhost:8000/swagger/

## Demo Users (RBAC)

Sample users are created automatically with username = password:

| Username   | Password   | Roles       | Permissions                        |
|------------|------------|-------------|------------------------------------|
| `operator` | operator   | Operator    | Read-only; create production counts|
| `planner`  | planner    | Planner     | Read + create/edit orders          |
| `supervisor`| supervisor | Supervisor  | Read + edit orders/routing         |
| `admin`    | admin      | Admin       | Full access                        |

### Login Flow

1. Visit http://localhost:5173/
2. You'll be redirected to `/login` (unauthenticated)
3. Sign in with any demo user (e.g., `operator` / `operator`)
4. You'll be redirected to the Dashboard
5. Navigate to Orders or Technologies to see role-based UI controls

## Development Workflow

### Backend

- **Venv**: All backend commands run inside `backend/.venv`
- **Settings**: Uses `ourmes_backend.settings.dev` (SQLite)
- **Manage commands**:
  ```bash
  cd backend
  source .venv/bin/activate
  export DJANGO_SETTINGS_MODULE=ourmes_backend.settings.dev
  python manage.py <command>
  ```
- **Create migrations**:
  ```bash
  cd backend && source .venv/bin/activate
  export DJANGO_SETTINGS_MODULE=ourmes_backend.settings.dev
  python manage.py makemigrations
  python manage.py migrate
  ```

### Frontend

- **Install deps**: `cd frontend && npm install`
- **Dev server**: `npm run dev` (or via `run-local.sh`)
- **Build**: `npm run build`

### Reset Database

To start with a fresh SQLite DB:

```bash
rm backend/db.sqlite3
bash run-local.sh  # Will recreate and seed
```

## Troubleshooting

### `ModuleNotFoundError: No module named 'pkg_resources'`

The script installs `setuptools` automatically. If you see this error:

```bash
cd backend
source .venv/bin/activate
pip install --upgrade setuptools
```

### Port Already in Use

If `:8000` or `:5173` is taken, manually change ports in the script or stop conflicting processes:

```bash
lsof -ti:8000 | xargs kill -9
lsof -ti:5173 | xargs kill -9
```

### Frontend 401 on API Calls

- Ensure you're logged in at `/login`
- Check browser console for JWT token in `localStorage`
- Backend should accept requests from `http://localhost:5173` (CORS enabled)

## Next Steps

- Explore the Swagger API docs: http://localhost:8000/swagger/
- Check the Docker setup for production-like environments: `docker/README.md`
- Run tests: `cd backend && pytest` (configure as needed)

## Additional Notes

- **Timezone warnings**: Sample data uses naive datetimes; set `USE_TZ = False` or use timezone-aware dates to silence warnings.
- **Vite CJS warning**: Informational; Vite still works fine.
- **npm audit**: Known vulnerabilities in dev dependencies; run `npm audit fix` if desired.

---

**Happy coding!** 🚀
