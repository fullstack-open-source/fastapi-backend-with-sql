# Quick Reference Guide

Quick reference for common query patterns.

## Basic Patterns

```python
from src.db.postgres.postgres import connection as db

# SELECT
db.table("users").select("*").execute()
db.table("users").select("id", "name").execute()

# INSERT
db.table("users").insert({"name": "John"}).execute()
db.table("users").insert([{"name": "John"}, {"name": "Jane"}]).execute()

# UPDATE
db.table("users").update({"status": "active"}).eq("id", 1).execute()

# DELETE
db.table("users").delete().eq("id", 1).execute()
```

## Filtering

```python
# Comparison
.eq("status", "active")
.neq("role", "admin")
.gt("total", 100)
.gte("total", 100)
.lt("total", 1000)
.lte("total", 1000)

# Pattern
.like("name", "John%")
.ilike("email", "%@gmail.com")

# Lists
.in_("id", [1, 2, 3])
.not_in("status", ["deleted"])

# Null
.is_null("deleted_at")
.is_not_null("email")

# Range
.between("total", 100, 500)
.between("created_at", start_date, end_date)

# Search
.search("term", "col1", "col2", "col3")
```

## Joins

```python
.inner_join("users", "posts.user_id = users.id")
.left_join("users", "posts.user_id = users.id")
.right_join("users", "posts.user_id = users.id")
.full_join("users", "posts.user_id = users.id")
```

## Sorting & Pagination

```python
.order_by("created_at", ascending=False)
.order("created_at", ascending=False, nulls_first=True)
.limit(10)
.offset(20)
.range(0, 9)  # First 10 items
```

## Aggregations

```python
.count("*")
.sum("total", "total_revenue")
.avg("total", "avg_order")
.min("price", "min_price")
.max("price", "max_price")
.count_distinct("user_id", "unique_users")
```

## Grouping

```python
.group_by("category")
.group_by("user_id", "status")
.having("total_revenue", ">", 1000)
```

## Date/Time

```python
.date_trunc("month", "created_at", "month")
.date_part("year", "created_at", "year")
.extract("month", "created_at", "month")
```

## Window Functions

```python
.row_number(partition_by="user_id", order_by="created_at DESC")
.rank(order_by="total DESC")
.dense_rank(order_by="total DESC")
.lag("revenue", offset=1, order_by="month")
.lead("revenue", offset=1, order_by="month")
```

## CASE Statements

```python
.case_when("status = 'active'", "'1'", "'0'", "is_active")
```

## Advanced

```python
# CTE
.with_cte("name", query_builder)

# UNION
.union(query_builder)
.union_all(query_builder)

# Distinct
.distinct()

# Returning
.returning("*")
.returning("id", "name")
```

## Common Query Patterns

### Get by ID
```python
result = db.table("users").select("*").eq("id", user_id).execute()
user = result.data[0] if result.data else None
```

### Get Latest
```python
result = db.table("orders").select("*")\
    .order_by("created_at", ascending=False)\
    .limit(1)\
    .execute()
latest = result.data[0] if result.data else None
```

### Pagination
```python
page = 1
page_size = 10
result = db.table("posts").select("*")\
    .range((page - 1) * page_size, page * page_size - 1)\
    .execute()
```

### Count with Filter
```python
result = db.table("users").count("*").eq("status", "active").execute()
count = result.data[0]['count']
```

### Sum with Filter
```python
result = db.table("orders").select("*")\
    .sum("total", "revenue")\
    .eq("status", "completed")\
    .execute()
revenue = result.data[0]['revenue']
```

### Group by Date
```python
result = db.table("orders").select("*")\
    .date_trunc("day", "created_at", "date")\
    .sum("total", "daily_revenue")\
    .group_by("date")\
    .order_by("date")\
    .execute()
```

### Top N
```python
result = db.table("orders").select("*")\
    .select("user_id")\
    .sum("total", "total_spent")\
    .group_by("user_id")\
    .order_by("total_spent", ascending=False)\
    .limit(10)\
    .execute()
```

### Join with Filter
```python
result = db.table("orders").select("*")\
    .inner_join("users", "orders.user_id = users.id")\
    .eq("users.status", "active")\
    .execute()
```

## Error Handling

```python
try:
    result = db.table("users").select("*").eq("id", user_id).execute()
    if result.data:
        return result.data[0]
    else:
        return None
except Exception as e:
    logger.error(f"Query failed: {e}")
    raise
```

## Result Access

```python
result = db.table("users").select("*").execute()

# Access data
users = result.data  # List of dicts
count = result.count  # Count of results

# Iterate
for user in result.data:
    print(user['name'])

# Check if empty
if result.data:
    first_user = result.data[0]
```

