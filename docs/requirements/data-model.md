# Data Model

## Entity Relationship Diagram

```
┌──────────────┐       ┌──────────────────┐       ┌──────────────┐
│    User      │       │     Insight      │       │   Product    │
├──────────────┤       ├──────────────────┤       ├──────────────┤
│ id           │       │ id               │       │ id           │
│ email        │──────<│ author_id        │>──────│ name         │
│ name         │       │ title            │       │ description  │
│ role         │       │ description      │       │ created_at   │
│ created_at   │       │ source           │       └──────────────┘
└──────────────┘       │ created_at       │              ▲
                       │ updated_at       │              │
                       └──────────────────┘              │
                              │    │                     │
                              │    │    ┌────────────────┘
                              │    │    │
                              ▼    │    │
                       ┌──────────────────┐
                       │ insight_products │
                       ├──────────────────┤
                       │ insight_id       │
                       │ product_id       │
                       └──────────────────┘
                              │
                              │
                              ▼
                       ┌──────────────────┐       ┌──────────────┐
                       │  insight_tags    │       │     Tag      │
                       ├──────────────────┤       ├──────────────┤
                       │ insight_id       │>──────│ id           │
                       │ tag_id           │       │ name         │
                       └──────────────────┘       │ created_at   │
                                                  └──────────────┘
```

## Entities

### User
Represents both Developer Advocates and Product Managers.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| email | string | unique, not null | User's email address |
| name | string | not null | Display name |
| role | enum | not null | 'advocate' or 'product_manager' |
| created_at | timestamp | not null | Account creation time |

### Insight
The core entity - a piece of product feedback or observation.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| author_id | UUID | FK -> User | Who created the insight |
| title | string | not null, max 200 | Brief summary |
| description | text | not null | Full insight details |
| source | enum | nullable | Where the insight came from |
| created_at | timestamp | not null | When insight was created |
| updated_at | timestamp | not null | Last modification time |

**Source enum values:**
- `community_forum` - Community forums/Discord
- `conference` - Conference feedback
- `social_media` - Social media (Twitter, LinkedIn, etc.)
- `meetup` - Community Meetups
- `other` - Other sources

### Product
A product or feature that insights can be linked to.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| name | string | unique, not null | Product/feature name |
| description | text | nullable | Optional description |
| created_at | timestamp | not null | When product was added |

### Tag
Freeform labels for organizing insights.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| name | string | unique, not null | Tag name (lowercase) |
| created_at | timestamp | not null | When tag was created |

## Junction Tables

### insight_products
Links insights to products (many-to-many).

| Field | Type | Constraints |
|-------|------|-------------|
| insight_id | UUID | FK -> Insight, PK |
| product_id | UUID | FK -> Product, PK |

### insight_tags
Links insights to tags (many-to-many).

| Field | Type | Constraints |
|-------|------|-------------|
| insight_id | UUID | FK -> Insight, PK |
| tag_id | UUID | FK -> Tag, PK |

## Indexes

- `insights.author_id` - Filter by author
- `insights.source` - Filter by source
- `insights.created_at` - Sort by date
- `products.name` - Search products
- `tags.name` - Search tags
