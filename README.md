# FastAPI User & Calculation Routes

## Overview

This project builds on the secure FastAPI application developed in previous modules by implementing complete BREAD (Browse, Read, Edit, Add, Delete) calculation routes and user authentication. The application uses FastAPI, SQLAlchemy, PostgreSQL, and Pydantic to securely manage users and calculation records while validating all incoming requests and responses.

Users can register and log in using securely hashed passwords. Authenticated users can create, browse, read, update, and delete calculation records stored in a PostgreSQL database. The project also includes automated unit and integration testing, Docker containerization, GitHub Actions CI/CD, and Docker Hub deployment.

---

## Features

- User Registration with secure password hashing
- User Login with password verification
- Browse all calculations
- Read a calculation by ID
- Add new calculations
- Update existing calculations
- Delete calculations
- SQLAlchemy ORM models
- PostgreSQL database integration
- Pydantic request and response validation
- Factory pattern for performing calculations
- Unit and integration testing
- Docker containerization
- GitHub Actions CI/CD pipeline
- Trivy container security scanning
- Automatic Docker Hub deployment

---

## Clone the Repository

```bash
git clone https://github.com/Benkaii/fastapi_routes.git
cd fastapi_routes
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run the Application

Build and start the application using Docker Compose:

```bash
docker compose up --build
```

The application will be available at:

```
http://localhost:8000
```

Swagger API documentation:

```
http://localhost:8000/docs
```

---

## Run Tests Locally

Run all tests:

```bash
pytest
```

Run only unit tests:

```bash
pytest tests/unit -v
```

Run only integration tests:

```bash
pytest tests/integration -v
```

Run tests with code coverage:

```bash
pytest --cov=app --cov-report=term-missing
```

---

## Docker Hub

Docker image:

https://hub.docker.com/r/benkaii/fastapi_calculations

Pull the latest image:

```bash
docker pull benkaii/fastapi_calculations:latest
```

---

## GitHub Repository

Repository:

https://github.com/Benkaii/fastapi_routes

---

## CI/CD Pipeline

GitHub Actions automatically performs the following tasks whenever code is pushed to the repository:

- Builds the Docker containers
- Starts a PostgreSQL service
- Runs unit tests
- Runs integration tests
- Verifies API functionality
- Performs Trivy security scanning on the Docker image
- Pushes the Docker image to Docker Hub after all tests pass successfully

---

## API Endpoints

### User Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users/register` | Register a new user |
| POST | `/users/login` | Authenticate a user |
| GET | `/users/{username}` | Retrieve a user by username |

### Calculation Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/calculations` | Browse all calculations |
| POST | `/calculations` | Create a new calculation |
| GET | `/calculations/{calculation_id}` | Read a calculation by ID |
| PUT | `/calculations/{calculation_id}` | Update an existing calculation |
| DELETE | `/calculations/{calculation_id}` | Delete a calculation |

---

## Technologies Used

- Python 3.10
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- bcrypt
- Pytest
- Docker
- Docker Compose
- GitHub Actions
- Trivy

---

## Author

**Ismael Albilal**

Master of Science in Cybersecurity & Privacy  
New Jersey Institute of Technology