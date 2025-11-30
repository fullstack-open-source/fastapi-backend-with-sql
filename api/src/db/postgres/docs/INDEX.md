# Postgres Query Builder Documentation Index

Welcome to the Postgres Query Builder documentation. This query builder provides a Supabase-inspired API for building PostgreSQL queries with comprehensive analytics capabilities.

## Documentation Files

### 📚 [README.md](./README.md)
Complete documentation covering:
- Quick start guide
- Basic CRUD operations
- Filtering and conditions
- Joins
- Analytics and aggregations
- Date/time functions
- Window functions
- Advanced features
- Full API reference

**Start here** if you're new to the query builder.

### 📊 [ANALYTICS.md](./ANALYTICS.md)
Comprehensive analytics guide with examples:
- Time-series analysis
- Revenue analytics
- User analytics
- Cohort analysis
- Funnel analysis
- Retention analysis
- Performance metrics

**Use this** for building analytics dashboards and reports.

### ⚡ [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
Quick reference for common patterns:
- Common query patterns
- Method signatures
- Usage examples
- Error handling

**Keep this handy** for quick lookups.

## Quick Navigation

### I want to...

- **Learn the basics** → [README.md](./README.md#quick-start)
- **Build analytics queries** → [ANALYTICS.md](./ANALYTICS.md)
- **Find a quick example** → [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
- **See all methods** → [README.md](./README.md#api-reference)
- **Understand joins** → [README.md](./README.md#joins)
- **Do time-series analysis** → [ANALYTICS.md](./ANALYTICS.md#time-series-analysis)
- **Calculate metrics** → [ANALYTICS.md](./ANALYTICS.md#performance-metrics)

## Features

### ✅ Core Features
- ✅ Full CRUD operations (SELECT, INSERT, UPDATE, DELETE)
- ✅ Comprehensive filtering (eq, gt, like, in, etc.)
- ✅ Multiple join types (INNER, LEFT, RIGHT, FULL)
- ✅ Sorting and pagination
- ✅ Search across multiple columns

### 📊 Analytics Features
- ✅ Aggregation functions (SUM, AVG, MIN, MAX, COUNT)
- ✅ Date/time functions (DATE_TRUNC, DATE_PART, EXTRACT)
- ✅ Window functions (ROW_NUMBER, RANK, LAG, LEAD)
- ✅ CASE statements
- ✅ GROUP BY and HAVING
- ✅ Common Table Expressions (CTE)
- ✅ UNION operations

## Installation

The query builder is part of the KLIKYAI-V3 API. Import it like this:

```python
from src.db.postgres.postgres import connection as db
```

## Environment Variables

Make sure these environment variables are set:

```bash
DATABASE_HOST=your_host
DATABASE_NAME=your_database
DATABASE_USER=your_user
DATABASE_PASSWORD=your_password
DATABASE_PORT=5432
```

## Basic Usage

```python
from src.db.postgres.postgres import connection as db

# Simple query
result = db.table("users").select("*").execute()
users = result.data

# Filtered query
result = db.table("users").select("*").eq("status", "active").execute()

# Analytics query
result = db.table("orders").select("*")\
    .date_trunc("month", "created_at", "month")\
    .sum("total", "monthly_revenue")\
    .group_by("month")\
    .execute()
```

## Examples by Use Case

### User Management
```python
# Get active users
result = db.table("users").select("*").eq("status", "active").execute()

# Get user by ID
result = db.table("users").select("*").eq("id", user_id).execute()

# Create user
result = db.table("users").insert({
    "name": "John",
    "email": "john@example.com"
}).returning("*").execute()
```

### Analytics Dashboard
```python
# Daily revenue
result = db.table("orders").select("*")\
    .date_trunc("day", "created_at", "date")\
    .sum("total", "revenue")\
    .group_by("date")\
    .order_by("date")\
    .execute()
```

### Reports
```python
# Top customers
result = db.table("orders").select("*")\
    .select("user_id")\
    .sum("total", "total_spent")\
    .group_by("user_id")\
    .order_by("total_spent", ascending=False)\
    .limit(10)\
    .execute()
```

## Contributing

When adding new features:
1. Update the main implementation in `postgres.py`
2. Add examples to `README.md`
3. Add analytics examples to `ANALYTICS.md` if applicable
4. Update `QUICK_REFERENCE.md` with new methods
5. Update this index if adding new documentation files

## Support

For issues or questions:
1. Check the [README.md](./README.md) for basic usage
2. Check [ANALYTICS.md](./ANALYTICS.md) for analytics examples
3. Check [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) for quick examples

## Version

This documentation is for Postgres Query Builder v1.0.0

## License

Part of the KLIKYAI-V3 project.

