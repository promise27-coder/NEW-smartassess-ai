# SmartAssess AI

SmartAssess AI is an adaptive AI-powered interview intelligence platform for students, colleges, placement cells, and recruiters.

This sprint contains project scaffolding only. It does not include authentication, AI workflows, resume parsing, dashboards, or business logic.

## Tech Stack

- Frontend: Next.js 15, TypeScript, Tailwind CSS
- Backend: FastAPI, Python 3.12, SQLAlchemy 2.0
- Database: PostgreSQL
- Development: Docker, Docker Compose, environment variables

## Project Structure

```text
smartassess-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── app/
│   ├── public/
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

## Getting Started

Create a local environment file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Start the development stack:

```bash
docker compose up --build
```

Services:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Backend API docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432

## Current Sprint Scope

Implemented:

- Professional full-stack folder structure
- Backend FastAPI project scaffold
- Frontend Next.js project scaffold
- PostgreSQL service in Docker Compose
- Environment variable example file
- Basic FastAPI root endpoint
- Basic Next.js homepage

Not implemented in this sprint:

- Authentication
- AI features
- Resume parsing
- Dashboards
- Business logic
