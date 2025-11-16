# OurMES MES Frontend (Vue 3 + Vite)

This is the frontend for the OurMES MES system, built with Vue 3, Vite, the Composition API, Vue Router, Pinia, and Element Plus for UI components.

## Project Structure

- `src/`
  - `views/` — Main pages (Dashboard, Orders, Production, Reports)
  - `components/` — Reusable UI components
  - `router/` — Vue Router setup
  - `store/` — Pinia stores
  - `services/` — API service modules
  - `App.vue` — Root component
  - `main.js` — Entry point

## Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Run the development server:
   ```bash
   npm run dev
   ```
3. Build for production:
   ```bash
   npm run build
   ```

## Features
- Dashboard overview
- Orders management
- Production tracking
- Reports
- Authentication (planned)

## Backend API
This frontend connects to the OurMES backend (Django REST API). Configure the API base URL in `src/services/api.js` as needed.

---

For more details, see the backend and MES documentation.