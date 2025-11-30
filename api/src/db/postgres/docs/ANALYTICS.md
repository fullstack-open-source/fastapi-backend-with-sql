# Analytics Query Guide

Comprehensive guide for building analytics queries with the Postgres Query Builder.

## Table of Contents

- [Time-Series Analysis](#time-series-analysis)
- [Revenue Analytics](#revenue-analytics)
- [User Analytics](#user-analytics)
- [Cohort Analysis](#cohort-analysis)
- [Funnel Analysis](#funnel-analysis)
- [Retention Analysis](#retention-analysis)
- [Performance Metrics](#performance-metrics)

## Time-Series Analysis

### Daily Metrics

```python
# Daily revenue and order count
result = db.table("orders").select("*")\
    .date_trunc("day", "created_at", "date")\
    .sum("total", "daily_revenue")\
    .count("*", "order_count")\
    .count_distinct("user_id", "unique_customers")\
    .group_by("date")\
    .order_by("date")\
    .limit(30)\
    .execute()

for row in result.data:
    print(f"{row['date']}: ${row['daily_revenue']} ({row['order_count']} orders)")
```

### Monthly Trends

```python
# Monthly revenue with month-over-month growth
result = db.table("orders").select("*")\
    .date_trunc("month", "created_at", "month")\
    .sum("total", "monthly_revenue")\
    .count("*", "order_count")\
    .lag("monthly_revenue", offset=1, order_by="month", alias="prev_month_revenue")\
    .case_when(
        "prev_month_revenue > 0",
        "((monthly_revenue - prev_month_revenue) / prev_month_revenue * 100)",
        "0",
        "growth_percent"
    )\
    .group_by("month")\
    .order_by("month")\
    .execute()
```

### Weekly Aggregation

```python
# Weekly metrics
result = db.table("orders").select("*")\
    .date_trunc("week", "created_at", "week")\
    .sum("total", "weekly_revenue")\
    .avg("total", "avg_order_value")\
    .count("*", "order_count")\
    .group_by("week")\
    .order_by("week")\
    .execute()
```

### Hourly Distribution

```python
# Hourly order distribution
result = db.table("orders").select("*")\
    .date_part("hour", "created_at", "hour")\
    .count("*", "order_count")\
    .group_by("hour")\
    .order_by("hour")\
    .execute()
```

## Revenue Analytics

### Revenue by Category

```python
# Revenue grouped by product category
result = db.table("orders").select("*")\
    .inner_join("products", "orders.product_id = products.id")\
    .select("products.category")\
    .sum("orders.total", "category_revenue")\
    .count("*", "order_count")\
    .avg("orders.total", "avg_order_value")\
    .group_by("products.category")\
    .order_by("category_revenue", ascending=False)\
    .execute()
```

### Revenue by Payment Method

```python
# Revenue by payment method
result = db.table("orders").select("*")\
    .select("payment_method")\
    .sum("total", "revenue")\
    .count("*", "transaction_count")\
    .group_by("payment_method")\
    .order_by("revenue", ascending=False)\
    .execute()
```

### Revenue by Status

```python
# Revenue breakdown by order status
result = db.table("orders").select("*")\
    .select("status")\
    .sum("total", "revenue")\
    .count("*", "order_count")\
    .case_when("status = 'completed'", "1", "0", "is_completed")\
    .group_by("status")\
    .execute()
```

### Top Revenue Customers

```python
# Top 10 customers by revenue
result = db.table("orders").select("*")\
    .inner_join("users", "orders.user_id = users.id")\
    .select("users.name", "users.email")\
    .sum("orders.total", "total_spent")\
    .count("*", "order_count")\
    .avg("orders.total", "avg_order_value")\
    .group_by("users.id", "users.name", "users.email")\
    .order_by("total_spent", ascending=False)\
    .limit(10)\
    .execute()
```

## User Analytics

### User Growth Over Time

```python
# New user signups by month
result = db.table("users").select("*")\
    .date_trunc("month", "created_at", "month")\
    .count("*", "new_users")\
    .group_by("month")\
    .order_by("month")\
    .execute()
```

### Active Users

```python
# Active users (users who made orders in last 30 days)
from datetime import datetime, timedelta
thirty_days_ago = datetime.now() - timedelta(days=30)

result = db.table("orders").select("*")\
    .select("user_id")\
    .gte("created_at", thirty_days_ago)\
    .count_distinct("user_id", "active_users")\
    .execute()

active_count = result.data[0]['active_users']
```

### User Segmentation

```python
# Segment users by order value
result = db.table("orders").select("*")\
    .select("user_id")\
    .sum("total", "user_total_spent")\
    .count("*", "order_count")\
    .case_when("user_total_spent > 1000", "'high_value'", "'regular'", "segment")\
    .group_by("user_id")\
    .execute()
```

### User Lifetime Value

```python
# Calculate user lifetime value
result = db.table("orders").select("*")\
    .select("user_id")\
    .sum("total", "lifetime_value")\
    .count("*", "total_orders")\
    .min("created_at", "first_order_date")\
    .max("created_at", "last_order_date")\
    .avg("total", "avg_order_value")\
    .group_by("user_id")\
    .order_by("lifetime_value", ascending=False)\
    .execute()
```

## Cohort Analysis

### User Cohort by Signup Month

```python
# Create user cohorts
cohorts = db.table("users").select("*")\
    .date_trunc("month", "created_at", "signup_month")\
    .select("id", "signup_month")

# Get orders with cohort info
result = db.table("orders").select("*")\
    .with_cte("cohorts", cohorts)\
    .inner_join("cohorts", "orders.user_id = cohorts.id")\
    .date_trunc("month", "orders.created_at", "order_month")\
    .select("signup_month", "order_month")\
    .count("*", "orders")\
    .sum("orders.total", "revenue")\
    .group_by("signup_month", "order_month")\
    .order_by("signup_month", "order_month")\
    .execute()
```

### Cohort Retention

```python
# Calculate retention by cohort
cohorts = db.table("users").select("*")\
    .date_trunc("month", "created_at", "signup_month")\
    .select("id", "signup_month")

result = db.table("orders").select("*")\
    .with_cte("cohorts", cohorts)\
    .inner_join("cohorts", "orders.user_id = cohorts.id")\
    .date_part("month", "orders.created_at", "order_month")\
    .date_part("month", "cohorts.signup_month", "signup_month")\
    .select("signup_month", "order_month")\
    .count_distinct("orders.user_id", "retained_users")\
    .group_by("signup_month", "order_month")\
    .order_by("signup_month", "order_month")\
    .execute()
```

## Funnel Analysis

### Conversion Funnel

```python
# Multi-step funnel analysis
funnel_steps = [
    ("views", "page_views"),
    ("signups", "users"),
    ("trials", "trials"),
    ("purchases", "orders")
]

results = {}
for step_name, table_name in funnel_steps:
    result = db.table(table_name).count("*").execute()
    results[step_name] = result.data[0]['count']

# Calculate conversion rates
conversion_rates = {}
prev_count = results['views']
for step in ['signups', 'trials', 'purchases']:
    if step in results:
        conversion_rates[step] = (results[step] / prev_count) * 100
        prev_count = results[step]
```

### Order Funnel

```python
# Order status funnel
result = db.table("orders").select("*")\
    .select("status")\
    .count("*", "count")\
    .group_by("status")\
    .order_by("count", ascending=False)\
    .execute()

# Calculate drop-off rates
status_counts = {row['status']: row['count'] for row in result.data}
total = sum(status_counts.values())
funnel = {}
for status, count in status_counts.items():
    funnel[status] = {
        'count': count,
        'percentage': (count / total) * 100
    }
```

## Retention Analysis

### Day-N Retention

```python
# Calculate D1, D7, D30 retention
user_signups = db.table("users").select("*")\
    .select("id", "created_at")\
    .date_trunc("day", "created_at", "signup_date")

first_orders = db.table("orders").select("*")\
    .select("user_id", "created_at")\
    .row_number(partition_by="user_id", order_by="created_at ASC", alias="rn")\
    .eq("rn", 1)

result = db.table("orders").select("*")\
    .with_cte("signups", user_signups)\
    .with_cte("first_orders", first_orders)\
    .inner_join("signups", "orders.user_id = signups.id")\
    .inner_join("first_orders", "orders.user_id = first_orders.user_id")\
    .date_part("day", "(orders.created_at - signups.created_at)", "days_since_signup")\
    .select("days_since_signup")\
    .count_distinct("orders.user_id", "retained_users")\
    .in_("days_since_signup", [1, 7, 30])\
    .group_by("days_since_signup")\
    .execute()
```

### Monthly Retention

```python
# Monthly active users retention
result = db.table("orders").select("*")\
    .date_trunc("month", "created_at", "month")\
    .count_distinct("user_id", "mau")\
    .group_by("month")\
    .order_by("month")\
    .execute()
```

## Performance Metrics

### Average Order Value Trends

```python
# AOV by month
result = db.table("orders").select("*")\
    .date_trunc("month", "created_at", "month")\
    .avg("total", "avg_order_value")\
    .sum("total", "total_revenue")\
    .count("*", "order_count")\
    .group_by("month")\
    .order_by("month")\
    .execute()
```

### Order Frequency

```python
# Orders per user
result = db.table("orders").select("*")\
    .select("user_id")\
    .count("*", "order_count")\
    .group_by("user_id")\
    .order_by("order_count", ascending=False)\
    .execute()

# Calculate average orders per user
total_orders = sum(row['order_count'] for row in result.data)
unique_users = len(result.data)
avg_orders_per_user = total_orders / unique_users if unique_users > 0 else 0
```

### Revenue per Customer

```python
# Revenue per customer (RPC)
result = db.table("orders").select("*")\
    .select("user_id")\
    .sum("total", "customer_revenue")\
    .count("*", "order_count")\
    .group_by("user_id")\
    .execute()

avg_rpc = sum(row['customer_revenue'] for row in result.data) / len(result.data)
```

### Repeat Customer Rate

```python
# Percentage of customers with multiple orders
result = db.table("orders").select("*")\
    .select("user_id")\
    .count("*", "order_count")\
    .group_by("user_id")\
    .having("order_count", ">", 1)\
    .execute()

repeat_customers = len(result.data)

# Get total unique customers
total_result = db.table("orders").select("*").count_distinct("user_id").execute()
total_customers = total_result.data[0]['count_distinct']

repeat_rate = (repeat_customers / total_customers) * 100 if total_customers > 0 else 0
```

## Advanced Analytics Patterns

### Moving Averages

```python
# 7-day moving average of revenue
result = db.table("orders").select("*")\
    .date_trunc("day", "created_at", "date")\
    .sum("total", "daily_revenue")\
    .window(
        "AVG(daily_revenue) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)",
        alias="moving_avg_7d"
    )\
    .group_by("date")\
    .order_by("date")\
    .execute()
```

### Year-over-Year Comparison

```python
# Compare current year to previous year
current_year = db.table("orders").select("*")\
    .date_part("year", "created_at", "year")\
    .eq("year", 2024)\
    .sum("total", "revenue")\
    .group_by("year")

previous_year = db.table("orders").select("*")\
    .date_part("year", "created_at", "year")\
    .eq("year", 2023)\
    .sum("total", "revenue")\
    .group_by("year")

result = current_year.union(previous_year).execute()
```

### Percentile Analysis

```python
# Revenue percentiles using window functions
result = db.table("orders").select("*")\
    .select("user_id")\
    .sum("total", "user_revenue")\
    .window(
        "PERCENT_RANK() OVER (ORDER BY SUM(total))",
        alias="percentile"
    )\
    .group_by("user_id")\
    .execute()
```

## Best Practices for Analytics Queries

1. **Use indexes** on date columns used in WHERE clauses
2. **Limit date ranges** for better performance
3. **Use DATE_TRUNC** instead of DATE() for time-series
4. **Aggregate before joining** when possible
5. **Use CTEs** for complex multi-step queries
6. **Cache results** for frequently accessed analytics
7. **Monitor query performance** with EXPLAIN ANALYZE

## Performance Optimization

```python
# Good: Aggregated before join
result = db.table("orders").select("*")\
    .select("user_id")\
    .sum("total", "total_spent")\
    .group_by("user_id")\
    .inner_join("users", "orders.user_id = users.id")\
    .execute()

# Better: Use CTE for pre-aggregation
user_totals = db.table("orders").select("*")\
    .select("user_id")\
    .sum("total", "total_spent")\
    .group_by("user_id")

result = db.table("users").select("*")\
    .with_cte("user_totals", user_totals)\
    .inner_join("user_totals", "users.id = user_totals.user_id")\
    .execute()
```

