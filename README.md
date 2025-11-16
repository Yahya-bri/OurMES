# OurMES - Manufacturing Execution System

## Overview
OurMES is a comprehensive Manufacturing Execution System (MES) built with Django and Vue.js, inspired by the Qcadoo MES system. It provides a complete solution for managing production processes, orders, technologies, materials, and production tracking.

## Architecture

### Backend (Django REST Framework)
- **Framework**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT
- **API Documentation**: Swagger/OpenAPI

### Frontend (Vue.js 3)
- **Framework**: Vue 3 with Composition API
- **Build Tool**: Vite
- **UI Library**: Element Plus
- **State Management**: Pinia
- **Routing**: Vue Router

## Features

### Core Modules

#### 1. Basic Data Management
- **Companies**: Manage suppliers, customers, and producers
- **Products**: Product catalog with types (components, intermediates, final products, waste, packages)
- **Workstations**: Production machines and work centers
- **Production Lines**: Manufacturing lines with workstation assignments
- **Staff**: Worker management

#### 2. Routing
- **Routing Definitions**: Production process blueprints
- **Operations**: Individual production steps with time parameters
- **Routing Operations**: Tree-structured operation flows
- **Input/Output Components**: Material requirements and outputs for operations
- **State Management**: Draft, Accepted, Checked, Outdated, Declined

#### 3. Orders
- **Production Orders**: Comprehensive order management with state tracking
- **Order States**: Pending, Accepted, In Progress, Completed, Declined, Interrupted, Abandoned
- **Quantity Tracking**: Planned vs. done quantities
- **Date Management**: Planned, effective, and corrected dates
- **State Change History**: Complete audit trail of all state changes

#### 4. Production Tracking
- **Real-time Order Status**: Monitor orders in production
- **Progress Tracking**: Visual progress indicators
- **Workstation Status**: Active/inactive workstation monitoring
- **Production Line Status**: Line availability tracking

#### 5. Additional Modules
- **Deliveries**: Supplier delivery management
- **Scheduling**: Production scheduling and capacity planning
- **Production Counting**: Quantity recording and quality tracking

## Project Structure

### Backend Structure
```
backend/
├── mes/
│   ├── plugins/
│   │   ├── basic/
│   │   │   ├── api/           # DRF viewsets, routers and serializers
│   │   │   ├── application/   # orchestration/services layer
│   │   │   └── domain/        # domain models and aggregates
│   │   ├── orders/
│   │   ├── routing/
│   │   ├── deliveries/
│   │   ├── scheduling/
│   │   └── production_counting/
│   └── urls.py
├── ourmes_backend/
│   └── settings/              # base/dev/prod settings split
└── manage.py
```

### Frontend Structure
```
frontend/
├── src/
│   ├── core/
│   │   ├── api/httpClient.js  # Axios instance with interceptors
│   │   ├── router/            # Vue Router setup + guards
│   │   └── stores/            # App-wide Pinia stores
│   ├── modules/               # Feature modules (pages + services + stores)
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── orders/
│   │   ├── products/
│   │   ├── routing/
│   │   ├── basic-data/
│   │   ├── production/
│   │   ├── planning/
│   │   └── reports/
│   ├── components/            # Cross-module UI pieces
│   └── App.vue
├── index.html
├── package.json
└── vite.config.js
```

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Node.js 16+ and npm
- PostgreSQL 12+
- Docker and Docker Compose (optional)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd OurMES/backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Configure your database in `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/OurMES_db
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

6. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

8. Run the development server:
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/api/`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd OurMES/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure the API URL in `src/services/api.js` if needed:
   ```javascript
   baseURL: 'http://localhost:8000/api'
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```

5. Build for production:
   ```bash
   npm run build
   ```

The application will be available at `http://localhost:5173/`

### Docker Deployment

1. Build and run with Docker Compose:
   ```bash
   cd OurMES/docker
   docker-compose up -d --build
   ```

2. The application will be available at:
   - Frontend: `http://localhost:80`
   - Backend API: `http://localhost:80/api/`
   - Admin: `http://localhost:80/admin/`

## API Endpoints

### Basic Module
- `GET/POST /api/mes/basic/companies/` - Companies CRUD
- `GET/POST /api/mes/basic/products/` - Products CRUD
- `GET/POST /api/mes/basic/workstations/` - Workstations CRUD
- `GET/POST /api/mes/basic/production-lines/` - Production Lines CRUD
- `GET/POST /api/mes/basic/staff/` - Staff CRUD

### Routing Module
- `GET/POST /api/mes/routing/technologies/` - Routing CRUD
- `POST /api/mes/routing/technologies/{id}/change_state/` - Change routing state
- `GET/POST /api/mes/routing/operations/` - Operations CRUD
- `GET/POST /api/mes/routing/technology-operations/` - Routing operation components
- `GET/POST /api/mes/routing/operation-inputs/` - Operation input products
- `GET/POST /api/mes/routing/operation-outputs/` - Operation output products

### Orders Module
- `GET/POST /api/mes/orders/orders/` - Orders CRUD
- `GET /api/mes/orders/orders/dashboard_stats/` - Dashboard statistics
- `POST /api/mes/orders/orders/{id}/change_state/` - Change order state
- `GET /api/mes/orders/order-state-changes/` - Order state change history

## Technologies Used

### Backend
- Django 4.2
- Django REST Framework 3.14
- PostgreSQL
- django-filter for API filtering
- django-cors-headers for CORS
- djangorestframework-simplejwt for JWT authentication

### Frontend
- Vue 3.4 (Composition API)
- Vite 5.0
- Vue Router 4.2
- Pinia 2.1
- Element Plus 2.5
- Axios 1.6

## Development Guidelines

### Backend
1. Follow Django best practices
2. Use class-based views and ViewSets
3. Implement proper serializers for all models
4. Add filtering, searching, and ordering capabilities
5. Document API endpoints

### Frontend
1. Use Composition API for all components
2. Implement proper state management with Pinia
3. Follow Vue.js style guide
4. Use Element Plus components consistently
5. Handle errors gracefully

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is inspired by Qcadoo MES and follows similar architectural patterns.

## Support

For issues and questions, please create an issue on the GitHub repository.
