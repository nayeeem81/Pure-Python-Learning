# Database Setup & Migration Guide

## Overview
The `ImageMetadata` model requires a PostgreSQL table to be created. This guide provides several approaches to set up the database.

## Approach 1: Automatic SQLModel Migration (Recommended)

### Option A: Using SQLModel's create_all()
Add this to your FastAPI startup event:

```python
# In main.py or app initialization
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from data.database import engine
from data.model import ImageMetadata  # Ensure model is imported

@asynccontextmanager
async def lifespan(app: FastAPI):
	# Startup: Create tables
	async with engine.begin() as conn:
		await conn.run_sync(SQLModel.metadata.create_all)
	yield
	# Shutdown: Cleanup if needed

app = FastAPI(lifespan=lifespan)
```

### Option B: Using Alembic (for production)
1. Initialize Alembic in your project:
```bash
alembic init migrations
```

2. Edit `migrations/env.py` to use SQLModel metadata:
```python
from data.model import Base  # or SQLModel
target_metadata = Base.metadata
```

3. Create migration:
```bash
alembic revision --autogenerate -m "Add ImageMetadata table"
```

4. Review generated migration in `migrations/versions/`

5. Apply migration:
```bash
alembic upgrade head
```

## Approach 2: Manual SQL (Development)

Run this SQL directly in PostgreSQL:

```sql
-- Create image_metadata table
CREATE TABLE IF NOT EXISTS image_metadata (
	id SERIAL PRIMARY KEY,
	title TEXT NOT NULL DEFAULT '',
	short_brief TEXT NOT NULL DEFAULT '',
	version INTEGER NOT NULL DEFAULT 1,
	created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
	modified_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
	modified_by VARCHAR(100),
	CONSTRAINT image_metadata_pkey PRIMARY KEY (id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_image_metadata_modified_at 
	ON image_metadata(modified_at DESC);

-- Set proper permissions (adjust user as needed)
GRANT ALL PRIVILEGES ON image_metadata TO your_postgres_user;
```

## Approach 3: Docker Compose (for local development)

```yaml
version: '3.8'

services:
  postgres:
	image: postgres:15
	environment:
	  POSTGRES_USER: ${DB_USER:-postgres}
	  POSTGRES_PASSWORD: ${DB_PASSWORD:-password}
	  POSTGRES_DB: ${DB_NAME:-webfastapi}
	ports:
	  - "5432:5432"
	volumes:
	  - postgres_data:/var/lib/postgresql/data
	  - ./init.sql:/docker-entrypoint-initdb.d/init.sql

volumes:
  postgres_data:
```

## Verification

### Check Table Creation
```sql
-- Connect to your database
psql -U postgres -d webfastapi

-- List tables
\dt

-- Describe image_metadata table
\d image_metadata

-- Expected output:
-- Column      |           Type           | Collation | Nullable |      Default
-- -----------|--------------------------+-----------+----------+------------------
-- id          | integer                  |           | not null | nextval('image_metadata_id_seq'::regclass)
-- title       | text                     |           | not null | ''::text
-- short_brief | text                     |           | not null | ''::text
-- version     | integer                  |           | not null | 1
-- created_at  | timestamp with time zone |           | not null | CURRENT_TIMESTAMP
-- modified_at | timestamp with time zone |           | not null | CURRENT_TIMESTAMP
-- modified_by | character varying(100)   |           |          |
```

### Test with Python
```python
import asyncio
from sqlmodel import Session, select
from data.database import async_session, engine
from data.model import ImageMetadata

async def test_table():
	# Check if table exists
	async with async_session() as session:
		statement = select(ImageMetadata)
		result = await session.execute(statement)
		records = result.scalars().all()
		print(f"Table exists and contains {len(records)} records")

asyncio.run(test_table())
```

## Configuration

### Environment Variables
Ensure your `.env` file has:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/webfastapi
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_NAME=webfastapi
```

### config.py Setup
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
	DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/webfastapi"

	class Config:
		env_file = ".env"

config = Settings()
```

## Testing API After Setup

### Test Save Endpoint
```bash
curl -X POST http://localhost:8000/api/metadata/save \
  -H "Content-Type: application/json" \
  -d '{
	"title": "My First Slide",
	"short_brief": "This is a test description for the image overlay."
  }'
```

Expected Response:
```json
{
  "id": 1,
  "title": "My First Slide",
  "short_brief": "This is a test description for the image overlay.",
  "version": 1,
  "modified_at": "2024-01-15T10:30:00+00:00"
}
```

### Test Retrieve Endpoint
```bash
curl http://localhost:8000/api/metadata/current
```

Expected Response:
```json
{
  "id": 1,
  "title": "My First Slide",
  "short_brief": "This is a test description for the image overlay.",
  "version": 1,
  "modified_at": "2024-01-15T10:30:00+00:00"
}
```

### Test Clear Endpoint
```bash
curl -X POST http://localhost:8000/api/metadata/clear
```

Expected Response:
```json
{
  "status": "success",
  "message": "Metadata cleared."
}
```

## Troubleshooting

### Error: "relation 'image_metadata' does not exist"

**Solution:** Run the table creation SQL or migration scripts.

```bash
# Quick fix for development:
psql -U postgres -d webfastapi -f create_table.sql
```

### Error: "Could not connect to database"

**Solution:** Check PostgreSQL is running and connection string is correct.

```bash
# Test connection
psql postgresql://user:password@localhost:5432/webfastapi

# Check running services
psql -U postgres -l  # List databases
```

### Error: "Column does not exist"

**Solution:** Drop and recreate the table (development only):

```sql
DROP TABLE IF EXISTS image_metadata CASCADE;
-- Then run table creation SQL again
```

### Error: "permission denied for schema public"

**Solution:** Grant permissions:

```sql
GRANT USAGE ON SCHEMA public TO your_username;
GRANT CREATE ON SCHEMA public TO your_username;
GRANT ALL ON ALL TABLES IN SCHEMA public TO your_username;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO your_username;
```

## Table Structure Details

### Columns Explained

| Column | Type | Purpose | Notes |
|--------|------|---------|-------|
| `id` | SERIAL | Primary key | Auto-increment |
| `title` | TEXT | Slide title | Max 200 chars in frontend |
| `short_brief` | TEXT | Description | Max 500 chars in frontend |
| `version` | INTEGER | Version tracking | Increments on update |
| `created_at` | TIMESTAMP with TZ | Creation time | Auto-set on insert |
| `modified_at` | TIMESTAMP with TZ | Modification time | Updates on every change |
| `modified_by` | VARCHAR(100) | User who modified | Optional |

### Indexes

For best performance, consider adding:

```sql
-- Speed up current metadata retrieval
CREATE INDEX idx_image_metadata_created_at ON image_metadata(created_at DESC);

-- Speed up updates by ID
CREATE INDEX idx_image_metadata_id ON image_metadata(id);

-- Speed up filtering by user
CREATE INDEX idx_image_metadata_user ON image_metadata(modified_by);
```

## Backup & Restore

### Backup Database
```bash
# Single table backup
pg_dump -t image_metadata webfastapi > image_metadata_backup.sql

# Full database backup
pg_dump webfastapi > full_backup.sql
```

### Restore Database
```bash
# Restore single table
psql webfastapi < image_metadata_backup.sql

# Restore full database
psql webfastapi < full_backup.sql
```

## Production Deployment

### Pre-deployment Checklist

- [ ] Database is running and accessible
- [ ] Connection credentials are correct
- [ ] `image_metadata` table is created
- [ ] Indexes are created for performance
- [ ] Backups are tested
- [ ] User permissions are set correctly
- [ ] SSL/TLS is configured if required
- [ ] Database logs are enabled
- [ ] Monitoring is set up

### Connection Pool Configuration

For production, configure connection pooling:

```python
# In data/database.py
engine = create_async_engine(
	config.DATABASE_URL,
	pool_size=20,  # Number of connections to maintain
	max_overflow=10,  # Max connections beyond pool_size
	pool_pre_ping=True,  # Check connection health
	pool_recycle=3600,  # Recycle connections every hour
	echo=False  # Disable logging in production
)
```

## Monitoring

### Check Table Size
```sql
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE tablename = 'image_metadata';
```

### Check Record Count
```sql
SELECT COUNT(*) FROM image_metadata;
```

### Check Slow Queries
```sql
SELECT query, calls, mean_time 
FROM pg_stat_statements 
WHERE query LIKE '%image_metadata%'
ORDER BY mean_time DESC;
```

## Next Steps

1. **Choose Setup Approach**
   - Use Approach 1 for automatic setup (fastest)
   - Use Approach 2 for manual migration
   - Use Approach 3 for Docker deployment

2. **Execute Setup**
   - Run the appropriate commands for your chosen approach
   - Verify table creation with verification steps

3. **Test the Feature**
   - Start your FastAPI application
   - Navigate to `/editimage`
   - Test the floating panel functionality
   - Verify data persists after page reload

4. **Monitor Performance**
   - Check application logs
   - Monitor database queries
   - Verify text downloads work correctly

5. **Deploy to Production**
   - Follow pre-deployment checklist
   - Configure connection pooling
   - Set up monitoring and alerts
   - Test thoroughly before going live

---

## Support

If you encounter issues:

1. Check the Troubleshooting section above
2. Review application logs for error messages
3. Verify PostgreSQL is running: `psql --version`
4. Check database connection: `psql -U postgres`
5. Verify table exists: `\d image_metadata`
6. Check API responses in browser network tab (F12)

**Database Setup Guide Version:** 1.0
**Status:** Complete
