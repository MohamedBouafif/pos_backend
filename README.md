# POS Backend

A modern, production-ready backend API for a Point of Sale (POS) system built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Important Services](#important-services)
- [Getting Started](#getting-started)
- [Best Practices](#best-practices)
- [Enhancements & Future Improvements](#enhancements--future-improvements)

---

## Overview

This backend API provides a comprehensive employee management and authentication system for a POS application. It supports user registration, account activation, password reset, role-based access control, and bulk employee imports via CSV files.

**Tech Stack:**
- **Framework:** FastAPI 0.115.12
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Authentication:** OAuth2 with JWT tokens
- **Email Service:** FastMail with HTML templates
- **Migration Tool:** Alembic
- **Password Hashing:** Bcrypt

---

## Key Features

### 1. **Authentication & Authorization**
- Secure login with OAuth2 and JWT tokens
- Account activation via email confirmation tokens
- Password reset functionality with time-limited tokens
- Bcrypt-based password hashing
- Token expiration management

### 2. **Employee Management**
- Create, read, and update employee records
- Support for multiple contract types (CDI, CDD, Apprenti, SIVP)
- Role-based access control (RBAC)
- Comprehensive employee data validation
- Pagination support for employee listings

### 3. **Bulk Import System**
- CSV-based employee bulk upload
- Multi-step validation with detailed error/warning reporting
- Duplicate detection (file-level and database-level)
- Conditional field validation based on contract type
- Background task email sending for account activation
- Batch database operations for optimal performance

### 4. **Email Service**
- HTML email templates for account activation and password reset
- Async email sending via FastMail
- SMTP configuration with SSL/TLS support
- Template rendering with dynamic data injection

### 5. **Error Tracking**
- Centralized error logging to database
- Error message mapping for user-friendly responses
- Constraint violation handling

---

## Project Structure

```
pos_backend/
├── alembic/                      # Database migrations
│   ├── env.py
│   ├── versions/                 # Migration scripts
│   └── script.py.mako
├── app/
│   ├── main.py                   # FastAPI app entry point
│   ├── config.py                 # Configuration settings (env vars)
│   ├── database.py               # SQLAlchemy setup
│   ├── OAuth2.py                 # JWT and authentication logic
│   ├── dependencies.py           # FastAPI dependencies (DB, auth, pagination)
│   ├── schemas.py                # Pydantic models for request/response
│   ├── crud/                     # Database operations
│   │   ├── auth.py               # Auth CRUD operations
│   │   ├── employee.py           # Employee CRUD operations
│   │   └── error.py              # Error logging
│   ├── enums/                    # Enumeration types
│   │   ├── accountStatus.py
│   │   ├── contractType.py
│   │   ├── emailTemplate.py
│   │   ├── gender.py
│   │   ├── roleType.py
│   │   ├── tokenStatus.py
│   │   └── ...
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── employee.py
│   │   ├── employeeRole.py
│   │   ├── accountActivation.py
│   │   ├── resetPassword.py
│   │   └── error.py
│   ├── routers/                  # API endpoint routes
│   │   ├── auth.py               # Authentication endpoints
│   │   └── employee.py           # Employee management endpoints
│   ├── external_services/        # Third-party integrations
│   │   ├── emailService.py       # Email sending logic
│   │   └── templates/            # Email HTML templates
│   └── service/
│       └── upload_employee.py    # CSV upload processing
├── requirements.txt              # Python dependencies
├── alembic.ini                   # Alembic configuration
└── .env                          # Environment variables (not in repo)
```

---

## Important Services

### 1. **Authentication Service** (`app/routers/auth.py`)

**Endpoints:**
- `POST /auth/login` - User login and access token generation
- `PATCH /auth/confirm_account` - Account activation via confirmation token
- `POST /auth/forgot_password` - Initiate password reset (sends email)
- `PATCH /auth/reset_password` - Reset password with valid reset token

**Key Features:**
- Time-limited tokens (default: 1 hour expiration)
- Token status tracking (Pending, Used)
- Email-based confirmation workflow

### 2. **Employee Management Service** (`app/routers/employee.py`)

**Endpoints:**
- `POST /employee/` - Create a new employee
- `PUT /employee/{id}` - Update employee information
- `GET /employee/all` - List all employees with pagination
- `POST /employee/csv` - Bulk import employees from CSV
- `GET /employee/possibleImportFields` - Get validation schema for CSV import

**Key Features:**
- Comprehensive data validation with custom validators
- Support for multiple contract types with conditional validation (e.g., CNSS number mandatory for CDI/CDD)
- Role assignment per employee
- Pagination with configurable page size
- Bulk import with detailed error/warning reporting

### 3. **Email Service** (`app/external_services/emailService.py`)

**Features:**
- Async email sending with FastMail
- HTML template rendering
- Support for multiple email templates (account activation, password reset)
- SMTP with SSL/TLS encryption

### 4. **CSV Import Service** (`app/routers/employee.py` & `app/service/upload_employee.py`)

**Validation Steps:**
1. Field-level validation (format, type, constraints)
2. Unique field validation within file
3. Database duplicate detection
4. Conditional field requirements based on contract type

**Features:**
- Batch database operations for performance
- Background email tasks for account activation
- Detailed error/warning feedback with cell coordinates
- Force upload option to bypass warnings

### 5. **Error Tracking Service** (`app/crud/error.py`)

**Features:**
- Centralized error logging to database
- Error message mapping for user-friendly responses
- Database constraint violation handling

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- pip or pip-tools

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd pos_backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables (.env file):**
   ```
   database_hostname=localhost
   database_port=5432
   database_username=postgres
   database_password=your_password
   database_name=pos_db
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   MAIL_FROM=noreply@pos.com
   MAIL_SERVER=smtp.gmail.com
   secret_key=your_secret_key_here
   algorithm=HS256
   access_token_expire_min=60
   ```

5. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Start the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

7. **Access API documentation:**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

---

## Best Practices

### 1. **Database Operations**

✅ **DO:**
- Use SQLAlchemy ORM for all database queries
- Implement proper transaction management with `db.commit()` and `db.rollback()`
- Use relationships instead of raw joins when possible
- Leverage database constraints (foreign keys, unique constraints, check constraints)
- Batch insert operations for performance: `db.add_all()` then `db.flush()` then `db.commit()`

❌ **DON'T:**
- Write raw SQL queries; use ORM methods
- Forget to rollback on exceptions
- Skip database validation; rely on ORM constraints

**Example:**
```python
try:
    db.add_all(employees_to_add)
    db.flush()  # Populate IDs before creating related records
    db.add_all(employee_roles_to_add)
    db.commit()
except Exception as e:
    db.rollback()
    raise HTTPException(status_code=500, detail=str(e))
```

### 2. **Authentication & Security**

✅ **DO:**
- Use bcrypt for password hashing (via passlib)
- Implement JWT with expiration times
- Validate tokens on protected endpoints
- Use OAuth2 with FastAPI security utilities
- Store sensitive data in environment variables

❌ **DON'T:**
- Store passwords in plain text
- Use weak secrets or hardcode keys
- Implement custom authentication logic

**Example:**
```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_pwd = pwd_context.hash(plain_password)
is_valid = pwd_context.verify(plain_password, hashed_pwd)
```

### 3. **API Design**

✅ **DO:**
- Return consistent response schemas
- Use HTTP status codes properly (200, 201, 400, 401, 404, 500)
- Implement pagination for list endpoints
- Provide user-friendly error messages
- Use dependency injection for database sessions

❌ **DON'T:**
- Mix response formats
- Return 500 errors for validation issues (use 400)
- Return unbounded lists

**Example:**
```python
@app.get("/employee/all", response_model=schemas.EmployeesResponse)
def get(db: DbDep, pagination_param: PaginationDep):
    employees, total_records, total_pages = employee.get_employees(db, pagination_param)
    return schemas.EmployeesResponse(
        status_code=200,
        detail="All employees",
        list=[...],
        page_number=pagination_param.page_number,
        total_pages=total_pages,
        total_records=total_records,
    )
```

### 4. **Data Validation**

✅ **DO:**
- Use Pydantic schemas for request validation
- Implement custom validators for complex logic
- Validate data at multiple levels (schema, business logic, database)
- Provide clear validation error messages
- Use regex patterns for format validation (email, phone, CNSS)

❌ **DON'T:**
- Skip validation on API inputs
- Rely only on database constraints
- Return generic validation error messages

**Example:**
```python
email_regex = r'^\S+@\S+\.\S+$'
cnss_regex = r'^\d{8}-\d{2}$'

fields_check = {
    "email": (lambda field: is_valid_email(field), "Wrong Email Format!"),
    "cnss_number": (lambda field: is_valid_cnss_number(field), "Format: {8 digits}-{2 digits}"),
}
```

### 5. **Error Handling**

✅ **DO:**
- Catch specific exceptions
- Log errors with context
- Return meaningful error messages to users
- Map database constraint errors to user-friendly messages
- Clean up resources (rollback) on error

❌ **DON'T:**
- Use generic exception handling
- Expose internal error details to users
- Forget to rollback database transactions

**Example:**
```python
error_keys = {
    "employees_email_key": "Email already used",
    "ck_employees_cnss_number": "CNSS number format invalid for CDI/CDD",
}

try:
    # operation
except Exception as e:
    db.rollback()
    raise HTTPException(status_code=500, detail=get_error_message(str(e), error_keys))
```

### 6. **Async Operations**

✅ **DO:**
- Use background tasks for long-running operations (email sending)
- Keep endpoint response times low
- Use `BackgroundTasks` for non-critical operations

❌ **DON'T:**
- Perform time-consuming operations synchronously
- Block request handlers on external service calls

**Example:**
```python
backgroundTasks.add_task(emailService.simple_send, email_schema, body, template)
```

### 7. **Code Organization**

✅ **DO:**
- Separate concerns: CRUD, services, routers, schemas
- Keep routers focused on HTTP logic only
- Place business logic in CRUD/service modules
- Use clear, descriptive naming conventions
- Document complex logic with comments

❌ **DON'T:**
- Mix database, business, and HTTP logic in routers
- Use ambiguous variable names
- Skip code comments for complex algorithms

### 8. **Environment & Configuration**

✅ **DO:**
- Use `.env` files for environment variables
- Use Pydantic Settings for configuration management
- Never commit `.env` to version control
- Validate required environment variables on startup

❌ **DON'T:**
- Hardcode configuration values
- Commit sensitive data to repository
- Ignore missing environment variables

---

## Enhancements & Future Improvements

### Critical Fixes

1. **⚠️ CORS Configuration** (`app/main.py`)
   ```python
   # Current: Allows all origins (security risk)
   allow_origins=["*"]
   
   # Recommended:
   allow_origins=[
       "http://localhost:3000",
       "http://localhost:3001",
       "https://yourdomain.com",
   ]
   ```
   **Impact:** Prevents unauthorized cross-origin requests

2. **⚠️ Token Extraction in OAuth2** (`app/OAuth2.py`)
   ```python
   # Issue: Token payload extraction expects "email" key
   email: str = payload.get("email")  # But token is created with "sub"
   
   # Should be:
   email: str = payload.get("sub")
   ```
   **Impact:** May cause token validation failures

### Security Enhancements

3. **Rate Limiting**
   - Add rate limiting to prevent brute force attacks on login/password reset
   - Install: `pip install slowapi`
   - Implement per-IP and per-email rate limits

4. **Input Sanitization**
   - Validate and sanitize all string inputs
   - Implement CSRF protection for state-changing operations

5. **Audit Logging**
   - Log all authentication attempts
   - Track employee data modifications with timestamps and user information
   - Implement audit trail for sensitive operations

6. **Two-Factor Authentication (2FA)**
   - Add optional 2FA for enhanced security
   - Support TOTP (Time-based One-Time Password)

### Performance Improvements

7. **Database Indexing**
   - Add indexes on frequently queried fields (email, number)
   - Use composite indexes for common filter combinations
   - Monitor slow queries using PostgreSQL logs

8. **Caching**
   - Implement Redis caching for employee lists
   - Cache role definitions and enums
   - Use cache invalidation strategies

9. **Pagination Optimization**
   - Implement cursor-based pagination for large datasets
   - Use `LIMIT` and `OFFSET` efficiently
   - Consider keyset pagination for better performance

10. **Query Optimization**
    - Use eager loading for relationships: `joinedload()`
    - Avoid N+1 query problems
    - Profile queries using SQLAlchemy's logging

### Feature Enhancements

11. **Soft Deletes**
    - Add `deleted_at` timestamp to track deleted records
    - Implement soft delete instead of hard deletes
    - Filter out soft-deleted records in queries

12. **Batch Operations Improvements**
    - Return detailed import statistics (created, updated, skipped)
    - Support partial upload with skip errors option
    - Add import history/audit trail

13. **Advanced Search & Filtering**
    - Implement full-text search for employee names
    - Add advanced filtering (date range, contract type, status)
    - Implement sorting options

14. **Data Export**
    - Add endpoint to export employees to CSV with filters
    - Support multiple export formats (Excel, PDF)

15. **Notification System**
    - Add in-app notifications for account activation
    - Implement notification preferences per employee
    - Support SMS notifications as alternative

### Testing & Quality

16. **Unit & Integration Tests**
    - Add pytest test suite
    - Implement test fixtures for database
    - Achieve >80% code coverage
    - Test edge cases and error scenarios

17. **API Documentation**
    - Add detailed endpoint descriptions
    - Include request/response examples
    - Document validation rules in OpenAPI schema

18. **Logging & Monitoring**
    - Implement structured logging (JSON format)
    - Use logging levels appropriately (DEBUG, INFO, WARNING, ERROR)
    - Integrate with monitoring tools (Sentry, DataDog)

### Infrastructure

19. **Docker Containerization**
    - Create Dockerfile for easy deployment
    - Use docker-compose for development environment
    - Add health check endpoints

20. **API Versioning**
    - Implement API versioning (`/v1/employee`, `/v2/employee`)
    - Plan for backward compatibility
    - Document breaking changes

### Documentation

21. **Developer Documentation**
    - Add setup guide for new developers
    - Document API endpoints with examples
    - Create database schema documentation
    - Add architecture decision records (ADRs)

22. **OpenAPI/Swagger Enhancement**
    - Add detailed descriptions to all endpoints
    - Include request/response examples
    - Document authentication requirements
    - Add deprecation warnings for old endpoints

---

## Common Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL service
psql -U postgres -h localhost -d pos_db

# Verify credentials in .env
# Run migrations
alembic upgrade head
```

### Email Sending Issues
```bash
# Check SMTP credentials
# Enable "Less secure app access" for Gmail
# Use app-specific password for Gmail accounts
```

### CORS Errors
- Update `allow_origins` in `app/main.py`
- Verify frontend URL matches configuration

### Token Validation Errors
- Check token expiration settings
- Verify secret key consistency
- Ensure algorithm matches (HS256)

---


## Contact

For issues or questions, contact: [your-email@example.com]
