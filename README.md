# Insider

A product insights tracker for Developer Advocates to capture and share feedback with Product Managers.

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=tom-howlett-sonarsource_insider&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=tom-howlett-sonarsource_insider)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=tom-howlett-sonarsource_insider&metric=coverage)](https://sonarcloud.io/summary/new_code?id=tom-howlett-sonarsource_insider)

## Problem

Developer Advocates gather valuable product insights from community interactions, conferences, and social media. These insights often get lost across scattered documents and never reach the Product Managers who need them.

## Solution

Insider provides a centralized platform to:
- **Capture** insights quickly with minimal friction
- **Organize** feedback by product, source, and tags
- **Share** with Product Managers for decision-making

## Current Status

This is a learning project with prototypes in multiple languages. The first prototype is built with Python/FastAPI.

### Python Prototype

**Tech Stack:**
- FastAPI
- Pydantic v2
- pytest (28 tests, 97% coverage)

**Running locally:**

```bash
cd prototypes/python-fastapi
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest

# Start server
uvicorn app.main:app --reload
```

API available at http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/insights` | List all insights |
| POST | `/api/v1/insights` | Create an insight |
| GET | `/api/v1/insights/{id}` | Get insight by ID |
| PUT | `/api/v1/insights/{id}` | Update an insight |
| DELETE | `/api/v1/insights/{id}` | Delete an insight |

## Project Structure

```
insider/
├── docs/
│   └── requirements/       # Requirements documentation
├── prototypes/
│   └── python-fastapi/     # Python prototype
├── CLAUDE.md               # Development guidelines
└── README.md
```

## Development

This project follows **Test-First Development (TDD)**:
1. Write a failing test
2. Write minimum code to pass
3. Refactor

All code is analyzed by SonarCloud before merge. See [CLAUDE.md](CLAUDE.md) for full guidelines.

## License

Private - All rights reserved.
