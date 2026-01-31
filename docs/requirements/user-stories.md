# User Stories

## Developer Advocate Stories

### Capture Insights

**US-1: Quick insight capture**
As a Developer Advocate, I want to quickly capture an insight with minimal friction, so that I don't lose valuable feedback in the moment.

Acceptance Criteria:
- Can create an insight with just a title and description
- Optional fields don't block submission
- Insight is saved immediately

**US-2: Add source context**
As a Developer Advocate, I want to record where an insight came from, so that I can provide context for Product Managers.

Acceptance Criteria:
- Can select from predefined sources: Community forums/Discord, Conference feedback, Social media, Community Meetups
- Can add custom source if needed
- Source is optional but encouraged

**US-3: Link to product/feature**
As a Developer Advocate, I want to link insights to specific products or features, so that PMs can find relevant feedback easily.

Acceptance Criteria:
- Can select one or more products/features from a list
- Can create new product/feature if it doesn't exist
- Products/features are searchable

### Organize Insights

**US-4: Tag insights**
As a Developer Advocate, I want to add tags to insights, so that I can find related insights later.

Acceptance Criteria:
- Can add multiple tags to an insight
- Tags are suggested based on existing tags
- Can create new tags inline

**US-5: Edit insights**
As a Developer Advocate, I want to edit my insights after creation, so that I can add details or correct mistakes.

Acceptance Criteria:
- Can edit title, description, source, products, and tags
- Edit history is preserved
- Last modified date is visible

## Product Manager Stories

### Discover Insights

**US-6: Browse insights**
As a Product Manager, I want to browse all insights, so that I can discover feedback I might not have searched for.

Acceptance Criteria:
- Can view a list of all insights
- Most recent insights appear first
- Can see insight title, source, and linked products

**US-7: Filter by product**
As a Product Manager, I want to filter insights by product/feature, so that I can focus on feedback relevant to my area.

Acceptance Criteria:
- Can filter by one or more products
- Filter persists during session
- Shows count of matching insights

**US-8: Search insights**
As a Product Manager, I want to search insight content, so that I can find specific feedback.

Acceptance Criteria:
- Full-text search across title and description
- Search results highlight matching terms
- Can combine search with filters

### Track Patterns

**US-9: View insight count by product**
As a Product Manager, I want to see how many insights exist per product, so that I can identify areas with lots of feedback.

Acceptance Criteria:
- Shows product list with insight count
- Sorted by count (highest first)
- Can click to view insights for that product
