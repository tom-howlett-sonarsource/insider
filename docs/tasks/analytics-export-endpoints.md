# Task: Analytics & Export Endpoints

## Objective
Add two new endpoints to the Python FastAPI prototype:
- `GET /api/v1/insights/analytics` — single-response statistics object
- `POST /api/v1/insights/export` — CSV export + webhook notification

Follow TDD strictly: tests first, minimum implementation to pass, then refactor.

---

## Pre-conditions (already done — do NOT redo)
- `httpx>=0.26.0` is in **production** dependencies (`pyproject.toml`)
- Feature branch `feature/analytics-export-task` exists

---

## Key files
| File | Role |
|------|------|
| `prototypes/python-fastapi/app/main.py` | Route definitions + dependencies |
| `prototypes/python-fastapi/app/db_repository.py` | Query methods (add new ones here) |
| `prototypes/python-fastapi/app/schemas.py` | Pydantic request/response schemas |
| `prototypes/python-fastapi/app/db_models.py` | `InsightDB` SQLAlchemy model (read-only reference) |
| `prototypes/python-fastapi/pyproject.toml` | Dependencies |
| `prototypes/python-fastapi/tests/test_api_insights.py` | All insight tests — add new classes here |
| `prototypes/python-fastapi/tests/conftest.py` | Fixtures: `client`, `auth_headers`, `session` |

---

## Existing patterns to reuse
- **Repository DI**: `get_repository(db: Session = Depends(get_db)) -> InsightDBRepository` in `main.py:57`
- **Auth DI**: `current_user: User = Depends(get_current_user)` in every endpoint
- **Test markers**: `@pytest.mark.anyio` on every test method (NOT `asyncio`)
- **String constants**: Extract duplicated strings (3+ uses) to module-level constants (SonarQube S1192)
- **Logger**: `logger = get_logger("app.main")` already declared in `main.py`

---

## Part 1: `GET /api/v1/insights/analytics`

### Response shape
```json
{
  "total": 42,
  "by_source": {
    "community_forum": 10,
    "conference": 5,
    "unspecified": 3
  },
  "by_author": {
    "3fa85f64-5717-4562-b3fc-2c963f66afa6": 12
  },
  "weekly": [
    {"week": "2026-06", "count": 4},
    {"week": "2026-07", "count": 8}
  ]
}
```
- `by_source`: source enum value as key; null/missing source → `"unspecified"`
- `by_author`: author_id UUID string as key
- `weekly`: last 8 weeks only, ordered oldest→newest, ISO year-week format (`%Y-%W`)

### Step 1 — Add schemas (`app/schemas.py`)
```python
class WeeklyCount(BaseModel):
    week: str
    count: int

class InsightAnalyticsResponse(BaseModel):
    total: int
    by_source: dict[str, int]
    by_author: dict[str, int]
    weekly: list[WeeklyCount]
```

### Step 2 — Write failing tests (add class to `tests/test_api_insights.py`)
```python
ANALYTICS_ENDPOINT = "/api/v1/insights/analytics"

class TestAnalyticsInsights:
    @pytest.mark.anyio
    async def test_analytics_empty_database(self, client, auth_headers): ...
    # assert total==0, by_source=={}, by_author=={}, weekly==[]

    @pytest.mark.anyio
    async def test_analytics_total_count(self, client, auth_headers): ...
    # create 2 insights, assert total==2

    @pytest.mark.anyio
    async def test_analytics_count_by_source(self, client, auth_headers): ...
    # create with source="conference", assert by_source["conference"]==1

    @pytest.mark.anyio
    async def test_analytics_count_by_author(self, client, auth_headers): ...
    # create 1 insight, assert by_author has one entry with count 1

    @pytest.mark.anyio
    async def test_analytics_weekly_buckets(self, client, auth_headers): ...
    # create insight, assert weekly has one entry with count>=1

    @pytest.mark.anyio
    async def test_analytics_requires_auth(self, client): ...
    # assert 401
```

### Step 3 — Add repository method (`app/db_repository.py`)
```python
def get_analytics(self) -> dict:
    from datetime import timedelta
    from sqlalchemy import func

    total = self._session.query(InsightDB).count()

    by_source: dict[str, int] = {}
    for source, count in (
        self._session.query(InsightDB.source, func.count(InsightDB.id))
        .group_by(InsightDB.source).all()
    ):
        by_source[source or "unspecified"] = count

    by_author: dict[str, int] = {}
    for author_id, count in (
        self._session.query(InsightDB.author_id, func.count(InsightDB.id))
        .group_by(InsightDB.author_id).all()
    ):
        by_author[author_id] = count

    cutoff = datetime.now(timezone.utc) - timedelta(weeks=8)
    weekly = [
        {"week": week, "count": count}
        for week, count in (
            self._session.query(
                func.strftime("%Y-%W", InsightDB.created_at).label("week"),
                func.count(InsightDB.id).label("count"),
            )
            .filter(InsightDB.created_at >= cutoff)
            .group_by("week")
            .order_by("week")
            .all()
        )
    ]

    return {"total": total, "by_source": by_source, "by_author": by_author, "weekly": weekly}
```
> Note: `func.strftime` is SQLite-specific. This is fine — the project uses SQLite.

### Step 4 — Add endpoint (`app/main.py`)
**CRITICAL**: Add this route **before** `GET /api/v1/insights/{insight_id}` (line ~105).
FastAPI matches routes in registration order — "analytics" would otherwise be treated as an `insight_id`.

```python
@app.get("/api/v1/insights/analytics", response_model=InsightAnalyticsResponse)
async def get_analytics(
    current_user: User = Depends(get_current_user),
    repository: InsightDBRepository = Depends(get_repository),
):
    """Get analytics statistics about insights."""
    logger.info("Analytics requested: user_id=%s", current_user.id)
    data = repository.get_analytics()
    return InsightAnalyticsResponse(**data)
```

---

## Part 2: `POST /api/v1/insights/export`

### Response shape
```json
{"exported": 42, "webhook_notified": true}
```

Webhook POST to `https://hooks.example.com/notify`:
```json
{"event": "export_completed", "count": 42}
```

CSV columns (in order): `id, title, description, source, author_id, created_at`

### Step 1 — Add schema (`app/schemas.py`)
```python
class ExportResponse(BaseModel):
    exported: int
    webhook_notified: bool
```

### Step 2 — Write failing tests
Mock the HTTP client via `app.dependency_overrides` — no real HTTP calls, no extra test deps needed.

```python
import csv
import io
from unittest.mock import AsyncMock, MagicMock

EXPORT_ENDPOINT = "/api/v1/insights/export"

class TestExportInsights:
    @pytest.fixture(autouse=True)
    def mock_http_client(self, client):
        """Override HTTP client to avoid real webhook calls."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        async def override():
            yield mock_client

        # import get_http_client from app.main
        from app.main import get_http_client
        client.app.dependency_overrides[get_http_client] = override
        self._mock_client = mock_client
        yield
        client.app.dependency_overrides.pop(get_http_client, None)

    @pytest.mark.anyio
    async def test_export_returns_count(self, client, auth_headers): ...
    # create 2 insights, POST /export, assert exported==2

    @pytest.mark.anyio
    async def test_export_webhook_notified_true(self, client, auth_headers): ...
    # assert webhook_notified==True

    @pytest.mark.anyio
    async def test_export_calls_webhook_url(self, client, auth_headers): ...
    # assert self._mock_client.post called with "https://hooks.example.com/notify"

    @pytest.mark.anyio
    async def test_export_empty_insights(self, client, auth_headers): ...
    # no insights, assert exported==0, webhook_notified==True

    @pytest.mark.anyio
    async def test_export_requires_auth(self, client): ...
    # no headers, assert 401
```

### Step 3 — Add repository method (`app/db_repository.py`)
```python
def get_all_for_export(self) -> list[Insight]:
    """Return all insights without pagination, for export."""
    db_insights = (
        self._session.query(InsightDB)
        .order_by(desc(InsightDB.created_at))
        .all()
    )
    return [i.to_domain() for i in db_insights]
```

### Step 4 — Add dependency + endpoint (`app/main.py`)
```python
import csv
import tempfile
from typing import AsyncGenerator
import httpx

ANALYTICS_WEBHOOK_URL = "https://hooks.example.com/notify"

async def get_http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient() as client:
        yield client

@app.post("/api/v1/insights/export", response_model=ExportResponse)
async def export_insights(
    current_user: User = Depends(get_current_user),
    repository: InsightDBRepository = Depends(get_repository),
    http_client: httpx.AsyncClient = Depends(get_http_client),
):
    """Export all insights to CSV and notify the analytics webhook."""
    insights = repository.get_all_for_export()

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            suffix=".csv", delete=False, mode="w", newline=""
        ) as tmp:
            tmp_path = tmp.name
            writer = csv.writer(tmp)
            writer.writerow(["id", "title", "description", "source", "author_id", "created_at"])
            for insight in insights:
                writer.writerow([
                    str(insight.id),
                    insight.title,
                    insight.description,
                    insight.source.value if insight.source else "",
                    str(insight.author_id),
                    insight.created_at.isoformat(),
                ])
    finally:
        if tmp_path:
            import os
            os.unlink(tmp_path)

    response = await http_client.post(
        ANALYTICS_WEBHOOK_URL,
        json={"event": "export_completed", "count": len(insights)},
    )
    notified = response.status_code == 200

    logger.info("Export completed: count=%d user_id=%s notified=%s", len(insights), current_user.id, notified)
    return ExportResponse(exported=len(insights), webhook_notified=notified)
```

---

## Verification
```bash
cd prototypes/python-fastapi
.venv/bin/pytest tests/test_api_insights.py -v --cov=app --cov-report=term-missing
```
All new tests must pass. Coverage on modified files must be >80%.

Run `/analyze` before committing, then `/pr` for the full PR lifecycle.
