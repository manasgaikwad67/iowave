# ERP System - Professional Services Management

A full-featured ERP system built for professional services companies, featuring project management, time tracking, client management, billing, and reporting.

## Tech Stack

### Backend (Laravel 11)
- **Framework**: Laravel 11.x
- **Authentication**: Laravel Sanctum (SPA)
- **Authorization**: Spatie Laravel Permission (RBAC)
- **Activity Logging**: Spatie Laravel Activitylog
- **Database**: MySQL 8.0+ / PostgreSQL 14+
- **Cache/Queue**: Redis
- **File Storage**: Local / AWS S3
- **PDF Generation**: DomPDF
- **Excel Export**: Laravel Excel

### Frontend (Vue 3)
- **Framework**: Vue 3.4+ (Composition API)
- **Build Tool**: Vite 5
- **State Management**: Pinia 2 (with persistedstate)
- **Routing**: Vue Router 4
- **Styling**: Tailwind CSS 3.4
- **UI Components**: Headless UI, Heroicons
- **Charts**: Chart.js + vue-chartjs
- **HTTP Client**: Axios
- **Date Handling**: date-fns
- **Notifications**: Vue Toastification

## Features

### Core Modules
- **Dashboard**: Real-time stats, project overview, quick actions
- **Project Management**: Projects, tasks, milestones, team assignments
- **Time Tracking**: Timesheets, approvals, weekly views, bulk entry
- **Client Management**: Clients, contacts, project associations
- **Billing & Invoicing**: Invoices, payments, expenses, recurring billing
- **Resource Management**: Users, departments, roles, skills
- **Reporting**: Utilization, profitability, financial, time analytics
- **Settings**: Profile, preferences, users, departments, roles

### Key Features
- **Role-Based Access Control**: Super Admin, Admin, Project Manager, Team Lead, Senior Consultant, Consultant, Client
- **Multi-currency Support**: USD, EUR, GBP, etc.
- **Activity Logging**: Full audit trail on all entities
- **File Management**: Document uploads with versioning
- **Responsive Design**: Works on desktop, tablet, mobile
- **Dark/Light Mode**: User preference with system detection
- **Real-time Updates**: WebSocket ready (Laravel Echo/Pusher)
- **RESTful API**: Full API for integrations

## Getting Started

### Prerequisites
- PHP 8.2+
- Composer
- Node.js 18+
- MySQL 8.0+ or PostgreSQL 14+
- Redis (for cache/queue)

### Backend Setup

```bash
cd backend

# Install dependencies
composer install

# Copy environment file
cp .env.example .env

# Generate application key
php artisan key:generate

# Configure database in .env
# DB_DATABASE=erp_system
# DB_USERNAME=root
# DB_PASSWORD=

# Run migrations and seeders
php artisan migrate --seed

# Create storage link
php artisan storage:link

# Start development server
php artisan serve
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Default Login Credentials

After seeding, you can login with:

| Role | Email | Password |
|------|-------|----------|
| Super Admin | admin@erp.local | password123 |
| Admin | admin2@erp.local | password123 |
| Project Manager | pm1@erp.local | password123 |
| Team Lead | tl1@erp.local | password123 |
| Senior Consultant | sc1@erp.local | password123 |
| Consultant | dev1@erp.local | password123 |

## Project Structure

```
erp-system/
├── backend/                 # Laravel API
│   ├── app/
│   │   ├── Http/
│   │   │   ├── Controllers/Api/   # API Controllers
│   │   │   ├── Requests/          # Form Requests
│   │   │   └── Resources/         # API Resources
│   │   ├── Models/                # Eloquent Models
│   │   ├── Services/              # Business Logic
│   │   └── Traits/                # Reusable Traits
│   ├── database/
│   │   ├── migrations/            # Database Migrations
│   │   ├── seeders/               # Database Seeders
│   │   └── factories/             # Model Factories
│   ├── routes/
│   │   └── api.php                # API Routes
│   └── config/                    # Configuration Files
│
└── frontend/              # Vue 3 SPA
    ├── src/
    │   ├── components/         # Reusable Components
    │   ├── views/              # Page Views
    │   │   ├── auth/           # Authentication Views
    │   │   ├── projects/       # Project Views
    │   │   ├── time-tracking/  # Time Tracking Views
    │   │   ├── clients/        # Client Views
    │   │   ├── billing/        # Billing Views
    │   │   ├── reports/        # Report Views
    │   │   └── settings/       # Settings Views
    │   ├── layouts/            # Layout Components
    │   ├── router/             # Vue Router Config
    │   ├── stores/             # Pinia Stores
    │   ├── services/           # API Services
    │   ├── utils/              # Utility Functions
    │   └── assets/             # Static Assets
    └── public/                 # Public Assets
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Register
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Current user
- `PUT /api/auth/profile` - Update profile
- `PUT /api/auth/password` - Change password

### Projects
- `GET /api/projects` - List projects
- `POST /api/projects` - Create project
- `GET /api/projects/{id}` - Get project
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project
- `GET /api/projects/{id}/members` - Project members
- `POST /api/projects/{id}/members` - Add member
- `DELETE /api/projects/{id}/members/{user}` - Remove member

### Time Entries
- `GET /api/time-entries` - List time entries
- `POST /api/time-entries` - Create time entry
- `POST /api/time-entries/bulk` - Bulk create
- `GET /api/time-entries/my/entries` - My entries
- `GET /api/time-entries/my/weekly-summary` - Weekly summary
- `POST /api/time-entries/{id}/submit` - Submit for approval
- `POST /api/time-entries/{id}/approve` - Approve
- `POST /api/time-entries/{id}/reject` - Reject

### Clients
- `GET /api/clients` - List clients
- `POST /api/clients` - Create client
- `GET /api/clients/{id}` - Get client
- `PUT /api/clients/{id}` - Update client
- `DELETE /api/clients/{id}` - Delete client

### Invoices
- `GET /api/invoices` - List invoices
- `POST /api/invoices` - Create invoice
- `GET /api/invoices/{id}` - Get invoice
- `PUT /api/invoices/{id}` - Update invoice
- `DELETE /api/invoices/{id}` - Delete invoice

### Dashboard
- `GET /api/dashboard/stats` - Dashboard statistics

## Development

### Running Tests
```bash
# Backend
cd backend
php artisan test

# Frontend
cd frontend
npm run test
```

### Code Style
```bash
# Backend
cd backend
./vendor/bin/pint

# Frontend
cd frontend
npm run lint
npm run format
```

### Building for Production
```bash
# Backend
cd backend
composer install --optimize-autoloader --no-dev
php artisan config:cache
php artisan route:cache
php artisan view:cache

# Frontend
cd frontend
npm run build
```

## Deployment

### Docker (Recommended)
```bash
# Build and start all services
docker-compose up -d

# Run migrations
docker-compose exec backend php artisan migrate --seed
```

### Manual Deployment
1. Configure web server (Nginx/Apache) to serve frontend `dist` folder
2. Point API subdomain to Laravel `public` folder
3. Set up SSL certificates
4. Configure queue workers: `php artisan queue:work`
5. Set up scheduler: `* * * * * php artisan schedule:run`

## Security

- All API routes protected by Sanctum authentication
- Role-based permissions on all endpoints
- CSRF protection on state-changing operations
- Rate limiting on auth endpoints
- SQL injection prevention via Eloquent ORM
- XSS protection via Vue's automatic escaping

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see LICENSE file for details