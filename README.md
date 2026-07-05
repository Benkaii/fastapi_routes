# FastAPI PostgreSQL Calculator

## Overview

This project was completed for Module 9 of IS601. The objective was to integrate a FastAPI application with a PostgreSQL database using Docker Compose and perform SQL operations through pgAdmin.

The project demonstrates:

- Docker containerization
- FastAPI application deployment
- PostgreSQL database integration
- pgAdmin database management
- SQL CRUD operations
- One-to-many relationships using foreign keys

---

## Project Structure

```
.
├── app/
├── templates/
├── tests/
├── docker-compose.yml
├── Dockerfile
├── main.py
├── requirements.txt
├── module9_queries.sql
└── README.md
```

---

## Technologies Used

- Python 3
- FastAPI
- PostgreSQL
- pgAdmin 4
- Docker
- Docker Compose
- Git
- GitHub

---

## Running the Project

Clone the repository:

```bash
git clone https://github.com/Benkaii/fastapi_postgres_calculator.git
```

Move into the project directory:

```bash
cd fastapi_postgres_calculator
```

Build and start the containers:

```bash
docker compose up --build
```

---

## Services

| Service | URL |
|----------|----------------------------|
| FastAPI | http://localhost:8000 |
| pgAdmin | http://localhost:5050 |
| PostgreSQL | localhost:5432 |

---

## Database Operations

The SQL commands used for this assignment are included in:

```
module9_queries.sql
```

The script demonstrates:

- Creating tables
- Inserting records
- Querying data
- Joining tables
- Updating records
- Deleting records

---

## Database Schema

### users

- id
- username
- email
- created_at

### calculations

- id
- operation
- operand_a
- operand_b
- result
- timestamp
- user_id

The `calculations.user_id` field references the `users.id` primary key, demonstrating a one-to-many relationship.

---

## Assignment Learning Outcomes

This project demonstrates:

- Containerizing applications with Docker
- Integrating Python applications with PostgreSQL
- Executing SQL CRUD operations
- Managing relational databases with pgAdmin
- Implementing foreign key relationships
