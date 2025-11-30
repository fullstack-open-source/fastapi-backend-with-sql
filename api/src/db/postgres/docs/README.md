# Postgres Query Builder Documentation

A powerful, Supabase-inspired query builder for PostgreSQL with comprehensive analytics capabilities.

## Table of Contents

- [Quick Start](#quick-start)
- [Basic CRUD Operations](#basic-crud-operations)
- [Filtering & Conditions](#filtering--conditions)
- [Joins](#joins)
- [Analytics & Aggregations](#analytics--aggregations)
- [Date/Time Functions](#datetime-functions)
- [Window Functions](#window-functions)
- [Advanced Features](#advanced-features)
- [Examples](#examples)
- [API Reference](#api-reference)

## Quick Start

```python
from src.db.postgres.postgres import connection as db

# Basic query
result = db.table("users").select("*").execute()
users = result.data  # List of dictionaries
count = result.count  # Number of results
```

## Basic CRUD Operations

### SELECT

```python
# Select all columns
result = db.table("users").select("*").execute()

# Select specific columns
result = db.table("users").select("id", "name", "email").execute()

# Select with list
result = db.table("users").select(["id", "name"]).execute()

# Select distinct
result = db.table("users").select("email").distinct().execute()

# Select with limit and offset
result = db.table("users").select("*").limit(10).offset(20).execute()

# Select with range (Supabase-style)
result = db.table("users").select("*").range(0, 9).execute()  # First 10 items
```

### INSERT

```python
# Insert single row
result = db.table("users").insert({
    "name": "John Doe",
    "email": "john@example.com",
    "status": "active"
}).execute()

# Insert multiple rows
result = db.table("users").insert([
    {"name": "John", "email": "john@example.com"},
    {"name": "Jane", "email": "jane@example.com"}
]).execute()

# Insert and return data
result = db.table("users").insert({
    "name": "John",
    "email": "john@example.com"
}).returning("*").execute()

inserted_user = result.data[0]
```

### UPDATE

```python
# Update single row (requires WHERE for safety)
result = db.table("users").update({
    "status": "inactive",
    "updated_at": "NOW()"
}).eq("id", user_id).execute()

# Update multiple rows
result = db.table("users").update({
    "status": "active"
}).in_("id", [1, 2, 3]).execute()

# Update and return data
result = db.table("users").update({
    "status": "active"
}).eq("id", user_id).returning("*").execute()

updated_user = result.data[0]
```

### DELETE

```python
# Delete single row (requires WHERE for safety)
result = db.table("users").delete().eq("id", user_id).execute()

# Delete multiple rows
result = db.table("users").delete().in_("id", [1, 2, 3]).execute()

# Delete and return data
result = db.table("users").delete().eq("id", user_id).returning("*").execute()

deleted_user = result.data[0]
```

## Filtering & Conditions

### Basic Operators

```python
# Equals
result = db.table("users").select("*").eq("status", "active").execute()

# Not equals
result = db.table("users").select("*").neq("role", "admin").execute()

# Greater than
result = db.table("orders").select("*").gt("total", 100).execute()

# Greater than or equal
result = db.table("orders").select("*").gte("total", 100).execute()

# Less than
result = db.table("orders").select("*").lt("total", 1000).execute()

# Less than or equal
result = db.table("orders").select("*").lte("total", 1000).execute()
```

### Pattern Matching

```python
# LIKE (case-sensitive)
result = db.table("users").select("*").like("name", "John%").execute()

# ILIKE (case-insensitive)
result = db.table("users").select("*").ilike("email", "%@gmail.com").execute()
```

### List Operations

```python
# IN
result = db.table("users").select("*").in_("id", [1, 2, 3, 4, 5]).execute()

# NOT IN
result = db.table("users").select("*").not_in("status", ["deleted", "banned"]).execute()
```

### Null Checks

```python
# IS NULL
result = db.table("users").select("*").is_null("deleted_at").execute()

# IS NOT NULL
result = db.table("users").select("*").is_not_null("email").execute()
```

### Range Queries

```python
# BETWEEN
result = db.table("orders").select("*").between("total", 100, 500).execute()

# Date range
from datetime import datetime
result = db.table("orders").select("*").between(
    "created_at",
    datetime(2024, 1, 1),
    datetime(2024, 12, 31)
).execute()
```

### Multiple Conditions

```python
# Multiple conditions (AND by default)
result = db.table("users").select("*")\
    .eq("status", "active")\
    .neq("role", "admin")\
    .is_not_null("email")\
    .execute()

# Custom WHERE
result = db.table("orders").select("*")\
    .where("total", ">", 100)\
    .where("status", "=", "completed")\
    .execute()
```

### Search

```python
# Search across multiple columns
result = db.table("users").select("*")\
    .search("john", "first_name", "last_name", "email")\
    .execute()
```

## Joins

### INNER JOIN

```python
result = db.table("posts").select("*")\
    .inner_join("users", "posts.user_id = users.id")\
    .execute()
```

### LEFT JOIN

```python
result = db.table("orders").select("*")\
    .left_join("customers", "orders.customer_id = customers.id")\
    .execute()
```

### RIGHT JOIN

```python
result = db.table("orders").select("*")\
    .right_join("customers", "orders.customer_id = customers.id")\
    .execute()
```

### FULL OUTER JOIN

```python
result = db.table("orders").select("*")\
    .full_join("customers", "orders.customer_id = customers.id")\
    .execute()
```

### Multiple Joins

```python
result = db.table("orders").select("*")\
    .left_join("customers", "orders.customer_id = customers.id")\
    .left_join("products", "orders.product_id = products.id")\
    .execute()
```

## Analytics & Aggregations

### Basic Aggregations

```python
# Count
result = db.table("users").count("*").execute()
total_count = result.data[0]['count']

# Count with condition
result = db.table("users").count("*").eq("status", "active").execute()

# Sum
result = db.table("orders").select("SUM(total) as total_revenue").execute()
# OR
result = db.table("orders").select("*").sum("total", "total_revenue").execute()
revenue = result.data[0]['total_revenue']

# Average
result = db.table("orders").select("*").avg("total", "avg_order_value").execute()
avg_value = result.data[0]['avg_order_value']

# Minimum
result = db.table("orders").select("*").min("total", "min_order").execute()

# Maximum
result = db.table("orders").select("*").max("total", "max_order").execute()

# Count distinct
result = db.table("orders").select("*").count_distinct("user_id", "unique_customers").execute()
```

### GROUP BY

```python
# Group by single column
result = db.table("orders").select("user_id", "SUM(total) as total_spent")\
    .group_by("user_id")\
    .execute()

# Group by multiple columns
result = db.table("orders").select("user_id", "status", "COUNT(*) as count")\
    .group_by("user_id", "status")\
    .execute()

# Group by with aggregations
result = db.table("orders").select("user_id")\
    .sum("total", "total_spent")\
    .count("*", "order_count")\
    .avg("total", "avg_order")\
    .group_by("user_id")\
    .order_by("total_spent", ascending=False)\
    .execute()
```

### HAVING

```python
# Having clause (filter aggregated results)
result = db.table("orders").select("user_id", "SUM(total) as total_spent")\
    .group_by("user_id")\
    .having("total_spent", ">", 1000)\
    .execute()
```

### CASE Statements

```python
# Simple CASE WHEN
result = db.table("users").select("*")\
    .case_when("status = 'active'", "'1'", "'0'", "is_active")\
    .execute()

# Multiple CASE statements
result = db.table("orders").select("*")\
    .case_when("total > 1000", "'high'", "'normal'", "order_category")\
    .case_when("status = 'completed'", "1", "0", "is_completed")\
    .execute()

# CASE with COUNT
result = db.table("orders").select(
    "COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count",
    "COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_count"
).execute()
```

## Date/Time Functions

### DATE_TRUNC (Time-Series Analysis)

```python
# Group by day
result = db.table("orders").select("*")\
    .date_trunc("day", "created_at", "order_date")\
    .sum("total", "daily_revenue")\
    .group_by("order_date")\
    .order_by("order_date")\
    .execute()

# Group by month
result = db.table("orders").select("*")\
    .date_trunc("month", "created_at", "order_month")\
    .sum("total", "monthly_revenue")\
    .count("*", "order_count")\
    .group_by("order_month")\
    .order_by("order_month")\
    .execute()

# Group by week
result = db.table("orders").select("*")\
    .date_trunc("week", "created_at", "order_week")\
    .sum("total", "weekly_revenue")\
    .group_by("order_week")\
    .execute()

# Available truncation periods:
# 'year', 'quarter', 'month', 'week', 'day', 'hour', 'minute'
```

### DATE_PART / EXTRACT

```python
# Extract year
result = db.table("orders").select("*")\
    .date_part("year", "created_at", "order_year")\
    .execute()

# Extract month
result = db.table("orders").select("*")\
    .extract("month", "created_at", "order_month")\
    .execute()

# Extract day of week
result = db.table("orders").select("*")\
    .date_part("dow", "created_at", "day_of_week")\
    .execute()
```

### Date Filtering

```python
from datetime import datetime, timedelta

# Last 30 days
thirty_days_ago = datetime.now() - timedelta(days=30)
result = db.table("orders").select("*")\
    .gte("created_at", thirty_days_ago)\
    .execute()

# Date range
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)
result = db.table("orders").select("*")\
    .gte("created_at", start_date)\
    .lte("created_at", end_date)\
    .execute()
```

## Window Functions

### ROW_NUMBER

```python
# Number rows within partition
result = db.table("orders").select("*")\
    .row_number(partition_by="user_id", order_by="created_at DESC", alias="row_num")\
    .execute()

# Get latest order per user
result = db.table("orders").select("*")\
    .row_number(partition_by="user_id", order_by="created_at DESC", alias="rn")\
    .execute()

# Filter to get only row_num = 1
latest_orders = [row for row in result.data if row['rn'] == 1]
```

### RANK and DENSE_RANK

```python
# Rank orders by total
result = db.table("orders").select("*")\
    .rank(order_by="total DESC", alias="order_rank")\
    .execute()

# Dense rank (no gaps)
result = db.table("orders").select("*")\
    .dense_rank(order_by="total DESC", alias="order_dense_rank")\
    .execute()
```

### LAG and LEAD

```python
# Previous value
result = db.table("sales").select("*")\
    .lag("revenue", offset=1, partition_by="region", order_by="month", alias="prev_revenue")\
    .execute()

# Next value
result = db.table("sales").select("*")\
    .lead("revenue", offset=1, partition_by="region", order_by="month", alias="next_revenue")\
    .execute()

# Calculate growth
result = db.table("sales").select("*")\
    .date_trunc("month", "date", "month")\
    .sum("revenue", "monthly_revenue")\
    .lag("monthly_revenue", offset=1, order_by="month", alias="prev_month")\
    .group_by("month")\
    .execute()
```

### Custom Window Functions

```python
# Custom window function
result = db.table("orders").select("*")\
    .window(
        "SUM(total) OVER (PARTITION BY user_id ORDER BY created_at)",
        alias="running_total"
    )\
    .execute()
```

## Advanced Features

### Common Table Expressions (CTE)

```python
# Single CTE
recent_users = db.table("users").select("*").gte("created_at", "2024-01-01")
result = db.table("orders").select("*")\
    .with_cte("recent_users", recent_users)\
    .inner_join("recent_users", "orders.user_id = recent_users.id")\
    .execute()

# Multiple CTEs
active_users = db.table("users").select("*").eq("status", "active")
recent_orders = db.table("orders").select("*").gte("created_at", "2024-01-01")
result = db.table("payments").select("*")\
    .with_cte("active_users", active_users)\
    .with_cte("recent_orders", recent_orders)\
    .execute()
```

### UNION

```python
# UNION
query1 = db.table("users").select("id", "name", "email")
query2 = db.table("admins").select("id", "name", "email")
result = query1.union(query2).execute()

# UNION ALL (keeps duplicates)
result = query1.union_all(query2).execute()
```

### Complex Queries

```python
# Complex analytics query
result = db.table("orders").select("*")\
    .date_trunc("month", "created_at", "month")\
    .sum("total", "monthly_revenue")\
    .count("*", "order_count")\
    .count_distinct("user_id", "unique_customers")\
    .avg("total", "avg_order_value")\
    .group_by("month")\
    .having("monthly_revenue", ">", 10000)\
    .order_by("month")\
    .execute()
```

## Examples

### Example 1: User Analytics

```python
# Get user statistics
result = db.table("users").select("*")\
    .count("*", "total_users")\
    .count_distinct("country", "countries")\
    .sum("CASE WHEN status = 'active' THEN 1 ELSE 0 END", "active_users")\
    .execute()

stats = result.data[0]
```

### Example 2: Revenue Analysis

```python
# Monthly revenue with growth
result = db.table("orders").select("*")\
    .date_trunc("month", "created_at", "month")\
    .sum("total", "revenue")\
    .lag("revenue", offset=1, order_by="month", alias="prev_revenue")\
    .case_when("prev_revenue > 0", 
               "((revenue - prev_revenue) / prev_revenue * 100)", 
               "0", 
               "growth_percent")\
    .group_by("month")\
    .order_by("month")\
    .execute()
```

### Example 3: Top Customers

```python
# Top 10 customers by spending
result = db.table("orders").select("user_id")\
    .sum("total", "total_spent")\
    .count("*", "order_count")\
    .group_by("user_id")\
    .order_by("total_spent", ascending=False)\
    .limit(10)\
    .execute()
```

### Example 4: Time-Series Dashboard

```python
# Daily metrics for dashboard
result = db.table("orders").select("*")\
    .date_trunc("day", "created_at", "date")\
    .sum("total", "daily_revenue")\
    .count("*", "order_count")\
    .count_distinct("user_id", "unique_customers")\
    .avg("total", "avg_order")\
    .group_by("date")\
    .order_by("date")\
    .limit(30)\
    .execute()
```

### Example 5: Cohort Analysis

```python
# User cohort by signup month
cohort_query = db.table("users").select("*")\
    .date_trunc("month", "created_at", "signup_month")

result = db.table("orders").select("*")\
    .with_cte("cohorts", cohort_query)\
    .inner_join("cohorts", "orders.user_id = cohorts.id")\
    .date_trunc("month", "orders.created_at", "order_month")\
    .select("signup_month", "order_month")\
    .count("*", "orders")\
    .sum("total", "revenue")\
    .group_by("signup_month", "order_month")\
    .order_by("signup_month", "order_month")\
    .execute()
```

## API Reference

### QueryBuilder Methods

#### CRUD Operations
- `select(*fields)` - Select columns
- `insert(data)` - Insert rows
- `update(data)` - Update rows
- `delete()` - Delete rows
- `returning(fields)` - Return data after insert/update/delete

#### Filtering
- `where(column, operator, value)` - Custom WHERE condition
- `eq(column, value)` - Equals
- `neq(column, value)` - Not equals
- `gt(column, value)` - Greater than
- `gte(column, value)` - Greater than or equal
- `lt(column, value)` - Less than
- `lte(column, value)` - Less than or equal
- `like(column, pattern)` - LIKE pattern match
- `ilike(column, pattern)` - Case-insensitive LIKE
- `in_(column, values)` - IN list
- `not_in(column, values)` - NOT IN list
- `is_null(column)` - IS NULL
- `is_not_null(column)` - IS NOT NULL
- `between(column, start, end)` - BETWEEN range
- `search(term, *columns)` - Search across columns

#### Joins
- `inner_join(table, on)` - INNER JOIN
- `left_join(table, on)` - LEFT JOIN
- `right_join(table, on)` - RIGHT JOIN
- `full_join(table, on)` - FULL OUTER JOIN

#### Sorting & Pagination
- `order(column, ascending, nulls_first)` - ORDER BY
- `order_by(column, ascending)` - ORDER BY alias
- `limit(count)` - LIMIT
- `offset(count)` - OFFSET
- `range(from_index, to_index)` - Range (Supabase-style)

#### Aggregations
- `count(column)` - COUNT
- `sum(column, alias)` - SUM
- `avg(column, alias)` - AVG
- `min(column, alias)` - MIN
- `max(column, alias)` - MAX
- `count_distinct(column, alias)` - COUNT DISTINCT

#### Grouping
- `group_by(*columns)` - GROUP BY
- `having(column, operator, value)` - HAVING clause

#### Date/Time
- `date_trunc(field, column, alias)` - DATE_TRUNC
- `date_part(field, column, alias)` - DATE_PART
- `extract(field, column, alias)` - EXTRACT

#### Window Functions
- `window(function, partition_by, order_by, alias)` - Custom window function
- `row_number(partition_by, order_by, alias)` - ROW_NUMBER
- `rank(partition_by, order_by, alias)` - RANK
- `dense_rank(partition_by, order_by, alias)` - DENSE_RANK
- `lag(column, offset, partition_by, order_by, alias)` - LAG
- `lead(column, offset, partition_by, order_by, alias)` - LEAD

#### Advanced
- `case_when(condition, then_value, else_value, alias)` - CASE WHEN
- `distinct(value)` - DISTINCT
- `with_cte(name, query_builder)` - Common Table Expression
- `union(query_builder, all)` - UNION
- `union_all(query_builder)` - UNION ALL

#### Execution
- `execute()` - Execute query and return QueryResult

### QueryResult

```python
class QueryResult:
    data: List[Dict[str, Any]]  # Query results as list of dictionaries
    count: Optional[int]        # Result count (for SELECT queries)
```

## Best Practices

1. **Always use WHERE for UPDATE/DELETE** - Prevents accidental mass updates
2. **Use parameterized queries** - All values are automatically parameterized
3. **Use aliases for aggregations** - Makes result access easier
4. **Group related operations** - Use GROUP BY for analytics
5. **Use CTEs for complex queries** - Improves readability
6. **Index frequently filtered columns** - Improves query performance
7. **Use date_trunc for time-series** - More efficient than date extraction

## Performance Tips

1. **Limit result sets** - Always use `.limit()` for large datasets
2. **Use indexes** - Ensure columns in WHERE, JOIN, ORDER BY are indexed
3. **Avoid SELECT *** - Select only needed columns
4. **Use EXPLAIN** - Analyze query plans for optimization
5. **Batch operations** - Use bulk INSERT for multiple rows

## Error Handling

```python
try:
    result = db.table("users").select("*").eq("id", user_id).execute()
    if result.data:
        user = result.data[0]
    else:
        print("User not found")
except Exception as e:
    logger.error(f"Query failed: {e}")
    raise
```

## License

This query builder is part of the KLIKYAI-V3 project.

