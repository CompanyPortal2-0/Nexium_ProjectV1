# Nexus API - Employee Management System

A clean and simple Flask-based REST API for employee management with role-based access control.

## 📁 Project Structure

```
nexus/
├── app.py                  # Main application entry point
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # PostgreSQL setup
├── .env.example           # Environment variables template
│
├── config/                # Configuration module
│   ├── __init__.py
│   └── config.py          # App configuration classes
│
├── models/                # Database models
│   ├── __init__.py
│   ├── database.py        # Database initialization
│   └── user.py            # User model
│
├── routes/                # API routes/blueprints
│   ├── __init__.py
│   ├── auth.py            # Authentication routes
│   └── hr.py              # HR management routes
│
└── utils/                 # Utility functions
    ├── __init__.py
    ├── validators.py      # Input validation
    └── decorators.py      # Custom decorators
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone the repository
cd nexus

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example environment file
copy .env.example .env

# Edit .env with your settings
```

### 3. Start PostgreSQL Database

```bash
# Using Docker Compose
docker-compose up -d
```

### 4. Initialize Database

```bash
# Run migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 5. Run the Application

```bash
# Development server
python app.py

# Or using Flask CLI
flask run
```

The API will be available at `http://localhost:5000`

## 📡 API Endpoints

### Authentication (`/auth`)

- **POST** `/auth/register` - Register new user
- **POST** `/auth/login` - Login and get JWT token

### HR Management (`/hr`)

- **POST** `/hr/employees` - Create new employee (HR only)
- **GET** `/hr/employees` - List employees (HR sees all, Manager sees team)
- **GET** `/hr/employees/<id>` - Get employee details
- **PUT** `/hr/employees/<id>` - Update employee (HR only)
- **DELETE** `/hr/employees/<id>` - Delete employee (HR only)

## 🔐 User Roles

- **hr** - Full access to all employee management
- **manager** - Can view their team members
- **employee** - Basic access

## 🛠️ Development

### Database Migrations

```bash
# Create new migration
flask db migrate -m "Description"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.
```

## 📝 Environment Variables

See `.env.example` for all available configuration options.

## 🐳 Docker

The `docker-compose.yml` file provides a PostgreSQL database:

```bash
# Start database
docker-compose up -d

# Stop database
docker-compose down

# View logs
docker-compose logs -f
```

## 📦 Dependencies

- **Flask** - Web framework
- **Flask-SQLAlchemy** - ORM
- **Flask-Migrate** - Database migrations
- **Flask-JWT-Extended** - JWT authentication
- **psycopg2-binary** - PostgreSQL adapter
- **python-dotenv** - Environment configuration

## 🔒 Security Notes

- Always change default secret keys in production
- Use strong passwords
- Enable HTTPS in production
- Keep dependencies updated

## 📄 License

MIT License
