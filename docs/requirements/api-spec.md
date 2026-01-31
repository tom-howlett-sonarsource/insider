# API Specification

Base URL: `/api/v1`

## Authentication

All endpoints require authentication via Bearer token.

```
Authorization: Bearer <token>
```

## Endpoints

### Insights

#### List Insights
`GET /insights`

Query parameters:
| Parameter | Type | Description |
|-----------|------|-------------|
| product_id | UUID | Filter by product |
| source | string | Filter by source |
| tag | string | Filter by tag name |
| search | string | Full-text search |
| limit | int | Max results (default: 20, max: 100) |
| offset | int | Pagination offset |

Response: `200 OK`
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "string",
      "description": "string",
      "source": "community_forum | conference | social_media | meetup | other",
      "author": {
        "id": "uuid",
        "name": "string"
      },
      "products": [
        {"id": "uuid", "name": "string"}
      ],
      "tags": [
        {"id": "uuid", "name": "string"}
      ],
      "created_at": "ISO8601",
      "updated_at": "ISO8601"
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

#### Get Insight
`GET /insights/{id}`

Response: `200 OK` - Single insight object (same as list item)

Response: `404 Not Found` - Insight not found

#### Create Insight
`POST /insights`

Request body:
```json
{
  "title": "string (required, max 200)",
  "description": "string (required)",
  "source": "community_forum | conference | social_media | meetup | other (optional)",
  "product_ids": ["uuid"] (optional),
  "tags": ["string"] (optional, creates tags if needed)
}
```

Response: `201 Created` - Returns created insight

Response: `400 Bad Request` - Validation error
```json
{
  "detail": [
    {"field": "title", "message": "Title is required"}
  ]
}
```

#### Update Insight
`PUT /insights/{id}`

Request body: Same as create (all fields optional)

Response: `200 OK` - Returns updated insight

Response: `403 Forbidden` - Not the author

Response: `404 Not Found` - Insight not found

#### Delete Insight
`DELETE /insights/{id}`

Response: `204 No Content`

Response: `403 Forbidden` - Not the author

Response: `404 Not Found` - Insight not found

---

### Products

#### List Products
`GET /products`

Query parameters:
| Parameter | Type | Description |
|-----------|------|-------------|
| search | string | Search by name |

Response: `200 OK`
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "string",
      "description": "string | null",
      "insight_count": 5,
      "created_at": "ISO8601"
    }
  ]
}
```

#### Create Product
`POST /products`

Request body:
```json
{
  "name": "string (required)",
  "description": "string (optional)"
}
```

Response: `201 Created` - Returns created product

Response: `409 Conflict` - Product with name already exists

---

### Tags

#### List Tags
`GET /tags`

Query parameters:
| Parameter | Type | Description |
|-----------|------|-------------|
| search | string | Search by name |

Response: `200 OK`
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "string",
      "insight_count": 12,
      "created_at": "ISO8601"
    }
  ]
}
```

---

### Users

#### Get Current User
`GET /users/me`

Response: `200 OK`
```json
{
  "id": "uuid",
  "email": "string",
  "name": "string",
  "role": "advocate | product_manager",
  "created_at": "ISO8601"
}
```

---

## Error Responses

All errors follow this format:
```json
{
  "detail": "Error message"
}
```

| Status | Description |
|--------|-------------|
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing or invalid token |
| 403 | Forbidden - Not allowed to perform action |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Resource already exists |
| 500 | Internal Server Error |
