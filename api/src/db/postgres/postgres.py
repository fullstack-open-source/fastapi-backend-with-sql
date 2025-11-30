import os
import traceback
import psycopg2
from psycopg2.extras import DictCursor
from src.logger.logger import logger
from typing import Any, Dict, List, Optional, Union, Tuple
from enum import Enum


class JoinType(Enum):
    INNER = "INNER"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    FULL = "FULL OUTER"


class QueryResult:

    def __init__(self, data: List[Dict[str, Any]], count: Optional[int] = None):
        self.data = data
        self.count = count


class QueryBuilder:
    """Query builder for building SQL queries """

    def __init__(self, connection, table_name: str):
        self.connection = connection
        self.table_name = table_name
        self.query_type = None  # 'select', 'insert', 'update', 'delete'
        self.select_fields = []
        self.where_conditions = []
        self.join_clauses = []
        self.order_by_clauses = []
        self.group_by_fields = []
        self.having_conditions = []
        self.limit_value = None
        self.offset_value = None
        self.insert_data = None
        self.update_data = None
        self.returning_fields = []
        self._distinct = False
        self.search_fields = []
        self.search_term = None
        # Analytics features
        self.window_functions = []
        self.cte_clauses = []  # Common Table Expressions
        self.union_queries = []
        self.case_statements = []
        self.date_trunc_fields = []

    def select(self, *fields: Union[str, List[str]]) -> 'QueryBuilder':
        """Select fields from table"""
        self.query_type = 'select'
        if not fields:
            self.select_fields = ["*"]
        elif len(fields) == 1:
            if isinstance(fields[0], str):
                self.select_fields = [fields[0]]
            else:
                self.select_fields = fields[0]
        else:
            # Multiple string arguments
            self.select_fields = list(fields)
        return self

    def insert(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> 'QueryBuilder':
        """Insert data into table"""
        self.query_type = 'insert'
        self.insert_data = data
        return self

    def update(self, data: Dict[str, Any]) -> 'QueryBuilder':
        """Update table data"""
        self.query_type = 'update'
        self.update_data = data
        return self

    def delete(self) -> 'QueryBuilder':
        """Delete from table"""
        self.query_type = 'delete'
        return self

    # WHERE conditions
    def where(self, column: str, operator: str, value: Any) -> 'QueryBuilder':
        """Add a WHERE condition"""
        self.where_conditions.append((column, operator, value, 'AND'))
        return self

    def eq(self, column: str, value: Any) -> 'QueryBuilder':
        """Equals condition"""
        return self.where(column, '=', value)

    def neq(self, column: str, value: Any) -> 'QueryBuilder':
        """Not equals condition"""
        return self.where(column, '!=', value)

    def gt(self, column: str, value: Any) -> 'QueryBuilder':
        """Greater than condition"""
        return self.where(column, '>', value)

    def gte(self, column: str, value: Any) -> 'QueryBuilder':
        """Greater than or equal condition"""
        return self.where(column, '>=', value)

    def lt(self, column: str, value: Any) -> 'QueryBuilder':
        """Less than condition"""
        return self.where(column, '<', value)

    def lte(self, column: str, value: Any) -> 'QueryBuilder':
        """Less than or equal condition"""
        return self.where(column, '<=', value)

    def like(self, column: str, pattern: str) -> 'QueryBuilder':
        """LIKE condition"""
        return self.where(column, 'LIKE', pattern)

    def ilike(self, column: str, pattern: str) -> 'QueryBuilder':
        """ILIKE condition (case-insensitive)"""
        return self.where(column, 'ILIKE', pattern)

    def in_(self, column: str, values: List[Any]) -> 'QueryBuilder':
        """IN condition"""
        return self.where(column, 'IN', values)

    def not_in(self, column: str, values: List[Any]) -> 'QueryBuilder':
        """NOT IN condition"""
        return self.where(column, 'NOT IN', values)

    def is_null(self, column: str) -> 'QueryBuilder':
        """IS NULL condition"""
        return self.where(column, 'IS', None)

    def is_not_null(self, column: str) -> 'QueryBuilder':
        """IS NOT NULL condition"""
        return self.where(column, 'IS NOT', None)

    def between(self, column: str, start: Any, end: Any) -> 'QueryBuilder':
        """BETWEEN condition"""
        self.where_conditions.append((column, 'BETWEEN', (start, end), 'AND'))
        return self

    def or_(self, *conditions: str) -> 'QueryBuilder':
        """OR condition (filter string)"""
        # Parse filter strings like "column.operator.value"
        for condition in conditions:
            parts = condition.split('.')
            if len(parts) >= 3:
                col = parts[0]
                op = parts[1]
                val = '.'.join(parts[2:])
                # Remove quotes if present
                if val.startswith('"') and val.endswith('"'):
                    val = val[1:-1]
                elif val.startswith("'") and val.endswith("'"):
                    val = val[1:-1]

                # Map operators
                if op == 'eq':
                    self.where_conditions.append((col, '=', val, 'OR'))
                elif op == 'neq':
                    self.where_conditions.append((col, '!=', val, 'OR'))
                elif op == 'ilike':
                    self.where_conditions.append((col, 'ILIKE', f'%{val}%', 'OR'))

        return self

    def and_(self, *conditions: str) -> 'QueryBuilder':
        for condition in conditions:
            parts = condition.split('.')
            if len(parts) >= 3:
                col = parts[0]
                op = parts[1]
                val = '.'.join(parts[2:])
                if val.startswith('"') and val.endswith('"'):
                    val = val[1:-1]
                elif val.startswith("'") and val.endswith("'"):
                    val = val[1:-1]

                if op == 'eq':
                    self.where_conditions.append((col, '=', val, 'AND'))
                elif op == 'neq':
                    self.where_conditions.append((col, '!=', val, 'AND'))
                elif op == 'ilike':
                    self.where_conditions.append((col, 'ILIKE', f'%{val}%', 'AND'))

        return self

    # JOIN operations
    def join(self, table: str, on: str, join_type: JoinType = JoinType.INNER) -> 'QueryBuilder':
        """Add a JOIN clause"""
        self.join_clauses.append((join_type, table, on))
        return self

    def inner_join(self, table: str, on: str) -> 'QueryBuilder':
        """INNER JOIN"""
        return self.join(table, on, JoinType.INNER)

    def left_join(self, table: str, on: str) -> 'QueryBuilder':
        """LEFT JOIN"""
        return self.join(table, on, JoinType.LEFT)

    def right_join(self, table: str, on: str) -> 'QueryBuilder':
        """RIGHT JOIN"""
        return self.join(table, on, JoinType.RIGHT)

    def full_join(self, table: str, on: str) -> 'QueryBuilder':
        """FULL OUTER JOIN"""
        return self.join(table, on, JoinType.FULL)

    # ORDER BY
    def order(self, column: str, ascending: bool = True, nulls_first: bool = False) -> 'QueryBuilder':
        """Order by column"""
        direction = "ASC" if ascending else "DESC"
        nulls = "NULLS FIRST" if nulls_first else "NULLS LAST"
        self.order_by_clauses.append(f"{column} {direction} {nulls}")
        return self

    def order_by(self, column: str, ascending: bool = True) -> 'QueryBuilder':
        """Order by column (alias)"""
        return self.order(column, ascending)

    # LIMIT and OFFSET
    def limit(self, count: int) -> 'QueryBuilder':
        """Limit number of results"""
        self.limit_value = count
        return self

    def offset(self, count: int) -> 'QueryBuilder':
        """Offset results"""
        self.offset_value = count
        return self

    def range(self, from_index: int, to_index: int) -> 'QueryBuilder':
        self.limit_value = to_index - from_index + 1
        self.offset_value = from_index
        return self

    # GROUP BY and HAVING
    def group_by(self, *columns: str) -> 'QueryBuilder':
        """Group by columns"""
        self.group_by_fields.extend(columns)
        return self

    def having(self, column: str, operator: str, value: Any) -> 'QueryBuilder':
        """HAVING condition"""
        self.having_conditions.append((column, operator, value))
        return self

    # DISTINCT
    def distinct(self, value: bool = True) -> 'QueryBuilder':
        """Select distinct values"""
        self._distinct = value
        return self

    # COUNT
    def count(self, column: str = "*", alias: Optional[str] = None) -> 'QueryBuilder':
        """Count rows - can be used with other select fields"""
        self.query_type = 'select'
        alias = alias or "count"
        self.select_fields.append(f"COUNT({column}) as {alias}")
        return self

    # AGGREGATION FUNCTIONS (Analytics)
    def sum(self, column: str, alias: Optional[str] = None) -> 'QueryBuilder':
        """Sum aggregation"""
        alias = alias or f"{column}_sum"
        self.select_fields.append(f"SUM({column}) as {alias}")
        return self

    def avg(self, column: str, alias: Optional[str] = None) -> 'QueryBuilder':
        """Average aggregation"""
        alias = alias or f"{column}_avg"
        self.select_fields.append(f"AVG({column}) as {alias}")
        return self

    def min(self, column: str, alias: Optional[str] = None) -> 'QueryBuilder':
        """Minimum aggregation"""
        alias = alias or f"{column}_min"
        self.select_fields.append(f"MIN({column}) as {alias}")
        return self

    def max(self, column: str, alias: Optional[str] = None) -> 'QueryBuilder':
        """Maximum aggregation"""
        alias = alias or f"{column}_max"
        self.select_fields.append(f"MAX({column}) as {alias}")
        return self

    def count_distinct(self, column: str, alias: Optional[str] = None) -> 'QueryBuilder':
        """Count distinct values"""
        alias = alias or f"{column}_count_distinct"
        self.select_fields.append(f"COUNT(DISTINCT {column}) as {alias}")
        return self

    # DATE/TIME FUNCTIONS (Analytics)
    def date_trunc(self, field: str, column: str, alias: Optional[str] = None) -> 'QueryBuilder':
        """
        Truncate date/time field for time-series analysis
        field: 'year', 'quarter', 'month', 'week', 'day', 'hour', 'minute'
        """
        alias = alias or f"{column}_{field}"
        self.date_trunc_fields.append((field, column, alias))
        self.select_fields.append(f"DATE_TRUNC('{field}', {column}) as {alias}")
        return self

    def date_part(self, field: str, column: str, alias: Optional[str] = None) -> 'QueryBuilder':
        """Extract date part (year, month, day, etc.)"""
        alias = alias or f"{column}_{field}"
        self.select_fields.append(f"DATE_PART('{field}', {column}) as {alias}")
        return self

    def extract(self, field: str, column: str, alias: Optional[str] = None) -> 'QueryBuilder':
        """Extract date part (alias for date_part)"""
        return self.date_part(field, column, alias)

    # CASE STATEMENTS (Analytics)
    def case_when(self, condition: str, then_value: Union[str, int, float], else_value: Optional[Union[str, int, float]] = None, alias: str = "case_result") -> 'QueryBuilder':
        """
        Add CASE WHEN statement
        Example: case_when("status = 'active'", "'1'", "'0'", "is_active")
        Note: Values should be SQL expressions (strings with quotes, numbers, etc.)
        """
        # Handle then_value - if it's a string, wrap in quotes; if number, use as-is
        if isinstance(then_value, str) and not then_value.startswith("'"):
            then_val = f"'{then_value}'"
        else:
            then_val = str(then_value)

        case_expr = f"CASE WHEN {condition} THEN {then_val}"

        if else_value is not None:
            if isinstance(else_value, str) and not else_value.startswith("'"):
                else_val = f"'{else_value}'"
            else:
                else_val = str(else_value)
            case_expr += f" ELSE {else_val}"

        case_expr += f" END as {alias}"
        self.select_fields.append(case_expr)
        return self

    # WINDOW FUNCTIONS (Analytics)
    def window(self, function: str, partition_by: Optional[str] = None, order_by: Optional[str] = None, alias: str = "window_result") -> 'QueryBuilder':
        """
        Add window function
        Example: window("ROW_NUMBER()", partition_by="user_id", order_by="created_at DESC", alias="row_num")
        """
        window_expr = function
        if partition_by or order_by:
            window_expr += " OVER ("
            if partition_by:
                window_expr += f"PARTITION BY {partition_by}"
            if order_by:
                if partition_by:
                    window_expr += " "
                window_expr += f"ORDER BY {order_by}"
            window_expr += ")"
        window_expr += f" as {alias}"
        self.select_fields.append(window_expr)
        return self

    def row_number(self, partition_by: Optional[str] = None, order_by: Optional[str] = None, alias: str = "row_number") -> 'QueryBuilder':
        """ROW_NUMBER() window function"""
        return self.window("ROW_NUMBER()", partition_by, order_by, alias)

    def rank(self, partition_by: Optional[str] = None, order_by: Optional[str] = None, alias: str = "rank") -> 'QueryBuilder':
        """RANK() window function"""
        return self.window("RANK()", partition_by, order_by, alias)

    def dense_rank(self, partition_by: Optional[str] = None, order_by: Optional[str] = None, alias: str = "dense_rank") -> 'QueryBuilder':
        """DENSE_RANK() window function"""
        return self.window("DENSE_RANK()", partition_by, order_by, alias)

    def lag(self, column: str, offset: int = 1, partition_by: Optional[str] = None, order_by: Optional[str] = None, alias: Optional[str] = None) -> 'QueryBuilder':
        """LAG() window function"""
        alias = alias or f"{column}_lag"
        return self.window(f"LAG({column}, {offset})", partition_by, order_by, alias)

    def lead(self, column: str, offset: int = 1, partition_by: Optional[str] = None, order_by: Optional[str] = None, alias: Optional[str] = None) -> 'QueryBuilder':
        """LEAD() window function"""
        alias = alias or f"{column}_lead"
        return self.window(f"LEAD({column}, {offset})", partition_by, order_by, alias)

    # CTE (Common Table Expressions)
    def with_cte(self, name: str, query_builder: 'QueryBuilder') -> 'QueryBuilder':
        """Add a Common Table Expression (CTE)"""
        query, params = query_builder._build_select_query()
        self.cte_clauses.append((name, query, params))
        return self

    # UNION operations
    def union(self, query_builder: 'QueryBuilder', all: bool = False) -> 'QueryBuilder':
        """Add UNION query"""
        query, params = query_builder._build_select_query()
        self.union_queries.append(("UNION ALL" if all else "UNION", query, params))
        return self

    def union_all(self, query_builder: 'QueryBuilder') -> 'QueryBuilder':
        """Add UNION ALL query"""
        return self.union(query_builder, all=True)

    # SEARCH
    def search(self, term: str, *columns: str) -> 'QueryBuilder':
        """Search across multiple columns"""
        self.search_term = term
        self.search_fields = list(columns) if columns else []
        return self

    # RETURNING (for INSERT/UPDATE/DELETE)
    def returning(self, fields: Union[str, List[str]] = "*") -> 'QueryBuilder':
        """Return fields after INSERT/UPDATE/DELETE"""
        if isinstance(fields, str):
            self.returning_fields = [fields]
        else:
            self.returning_fields = fields
        return self

    # Build SQL
    def _build_select_query(self) -> Tuple[str, List[Any]]:
        """Build SELECT query"""
        params = []
        query_parts = []

        # CTE (WITH clauses) - must come first
        if self.cte_clauses:
            cte_parts = []
            for name, query, cte_params in self.cte_clauses:
                cte_parts.append(f"{name} AS ({query})")
                params.extend(cte_params)
            query_parts.append("WITH " + ", ".join(cte_parts))

        query_parts.append("SELECT")

        # DISTINCT
        if self._distinct:
            query_parts.append("DISTINCT")

        # SELECT fields
        if not self.select_fields:
            query_parts.append("*")
        else:
            query_parts.append(", ".join(self.select_fields))

        # FROM
        query_parts.append(f"FROM {self.table_name}")

        # JOINs
        for join_type, table, on in self.join_clauses:
            query_parts.append(f"{join_type.value} JOIN {table} ON {on}")

        # WHERE
        where_parts = []
        for i, (col, op, val, logic) in enumerate(self.where_conditions):
            if i > 0:
                where_parts.append(logic)

            if op == 'IN':
                placeholders = ','.join(['%s'] * len(val))
                where_parts.append(f"{col} IN ({placeholders})")
                params.extend(val)
            elif op == 'NOT IN':
                placeholders = ','.join(['%s'] * len(val))
                where_parts.append(f"{col} NOT IN ({placeholders})")
                params.extend(val)
            elif op == 'BETWEEN':
                where_parts.append(f"{col} BETWEEN %s AND %s")
                params.extend([val[0], val[1]])
            elif op == 'IS':
                where_parts.append(f"{col} IS NULL")
            elif op == 'IS NOT':
                where_parts.append(f"{col} IS NOT NULL")
            else:
                where_parts.append(f"{col} {op} %s")
                params.append(val)

        # SEARCH (adds OR conditions)
        if self.search_term and self.search_fields:
            search_conditions = []
            for i, col in enumerate(self.search_fields):
                if i > 0:  # Add OR before each field except the first one
                    search_conditions.append("OR")
                search_conditions.append(f"{col} ILIKE %s")
                params.append(f"%{self.search_term}%")

            if where_parts:
                where_parts.append("AND")
                where_parts.append("(" + " ".join(search_conditions) + ")")
            else:
                where_parts.extend(search_conditions)

        if where_parts:
            query_parts.append("WHERE " + " ".join(where_parts))

        # GROUP BY
        if self.group_by_fields:
            query_parts.append(f"GROUP BY {', '.join(self.group_by_fields)}")

        # HAVING
        if self.having_conditions:
            having_parts = []
            for col, op, val in self.having_conditions:
                having_parts.append(f"{col} {op} %s")
                params.append(val)
            query_parts.append("HAVING " + " AND ".join(having_parts))

        # ORDER BY
        if self.order_by_clauses:
            query_parts.append("ORDER BY " + ", ".join(self.order_by_clauses))

        # LIMIT
        if self.limit_value is not None:
            query_parts.append(f"LIMIT {self.limit_value}")

        # OFFSET
        if self.offset_value is not None:
            query_parts.append(f"OFFSET {self.offset_value}")

        # UNION queries
        if self.union_queries:
            base_query = " ".join(query_parts)
            for union_type, union_query, union_params in self.union_queries:
                base_query += f" {union_type} {union_query}"
                params.extend(union_params)
            return base_query, params

        return " ".join(query_parts), params

    def _build_insert_query(self) -> Tuple[str, List[Any]]:
        """Build INSERT query"""
        params = []

        if isinstance(self.insert_data, list):
            # Multiple rows
            if not self.insert_data:
                raise ValueError("Insert data cannot be empty")

            columns = list(self.insert_data[0].keys())
            values_list = []

            for row in self.insert_data:
                placeholders = ','.join(['%s'] * len(columns))
                values_list.append(f"({placeholders})")
                params.extend([row.get(col) for col in columns])

            query = f"INSERT INTO {self.table_name} ({', '.join(columns)}) VALUES {', '.join(values_list)}"
        else:
            # Single row
            columns = list(self.insert_data.keys())
            placeholders = ','.join(['%s'] * len(columns))
            values = [self.insert_data[col] for col in columns]
            params.extend(values)

            query = f"INSERT INTO {self.table_name} ({', '.join(columns)}) VALUES ({placeholders})"

        # RETURNING
        if self.returning_fields:
            if self.returning_fields == ['*']:
                query += " RETURNING *"
            else:
                query += f" RETURNING {', '.join(self.returning_fields)}"

        return query, params

    def _build_update_query(self) -> Tuple[str, List[Any]]:
        """Build UPDATE query"""
        if not self.update_data:
            raise ValueError("Update data cannot be empty")

        params = []
        set_parts = []

        for col, val in self.update_data.items():
            set_parts.append(f"{col} = %s")
            params.append(val)

        query = f"UPDATE {self.table_name} SET {', '.join(set_parts)}"

        # WHERE
        where_parts = []
        for i, (col, op, val, logic) in enumerate(self.where_conditions):
            if i > 0:
                where_parts.append(logic)

            if op == 'IN':
                placeholders = ','.join(['%s'] * len(val))
                where_parts.append(f"{col} IN ({placeholders})")
                params.extend(val)
            elif op == 'NOT IN':
                placeholders = ','.join(['%s'] * len(val))
                where_parts.append(f"{col} NOT IN ({placeholders})")
                params.extend(val)
            elif op == 'BETWEEN':
                where_parts.append(f"{col} BETWEEN %s AND %s")
                params.extend([val[0], val[1]])
            elif op == 'IS':
                where_parts.append(f"{col} IS NULL")
            elif op == 'IS NOT':
                where_parts.append(f"{col} IS NOT NULL")
            else:
                where_parts.append(f"{col} {op} %s")
                params.append(val)

        if where_parts:
            query += " WHERE " + " ".join(where_parts)
        else:
            raise ValueError("UPDATE query requires WHERE conditions for safety")

        # RETURNING
        if self.returning_fields:
            if self.returning_fields == ['*']:
                query += " RETURNING *"
            else:
                query += f" RETURNING {', '.join(self.returning_fields)}"

        return query, params

    def _build_delete_query(self) -> Tuple[str, List[Any]]:
        """Build DELETE query"""
        params = []
        query = f"DELETE FROM {self.table_name}"

        # WHERE
        where_parts = []
        for i, (col, op, val, logic) in enumerate(self.where_conditions):
            if i > 0:
                where_parts.append(logic)

            if op == 'IN':
                placeholders = ','.join(['%s'] * len(val))
                where_parts.append(f"{col} IN ({placeholders})")
                params.extend(val)
            elif op == 'NOT IN':
                placeholders = ','.join(['%s'] * len(val))
                where_parts.append(f"{col} NOT IN ({placeholders})")
                params.extend(val)
            elif op == 'BETWEEN':
                where_parts.append(f"{col} BETWEEN %s AND %s")
                params.extend([val[0], val[1]])
            elif op == 'IS':
                where_parts.append(f"{col} IS NULL")
            elif op == 'IS NOT':
                where_parts.append(f"{col} IS NOT NULL")
            else:
                where_parts.append(f"{col} {op} %s")
                params.append(val)

        if where_parts:
            query += " WHERE " + " ".join(where_parts)
        else:
            raise ValueError("DELETE query requires WHERE conditions for safety")

        # RETURNING
        if self.returning_fields:
            if self.returning_fields == ['*']:
                query += " RETURNING *"
            else:
                query += f" RETURNING {', '.join(self.returning_fields)}"

        return query, params

    def execute(self) -> QueryResult:
        """Execute the query"""
        if not self.query_type:
            raise ValueError("No query type specified. Use select(), insert(), update(), or delete()")

        try:
            cursor = self.connection.cursor(cursor_factory=DictCursor)

            if self.query_type == 'select':
                query, params = self._build_select_query()
            elif self.query_type == 'insert':
                query, params = self._build_insert_query()
            elif self.query_type == 'update':
                query, params = self._build_update_query()
            elif self.query_type == 'delete':
                query, params = self._build_delete_query()
            else:
                raise ValueError(f"Unknown query type: {self.query_type}")

            logger.debug(f"Executing query: {query}", module="Postgres")
            logger.debug(f"With params: {params}", module="Postgres")

            cursor.execute(query, params)

            # Fetch results
            if self.query_type in ['select', 'insert', 'update', 'delete'] and (
                self.returning_fields or self.query_type == 'select'
            ):
                rows = cursor.fetchall()
                data = [dict(row) for row in rows]

                # Get count for SELECT queries
                # If count was explicitly requested, extract from result
                count = None
                if self.query_type == 'select':
                    # Check if any select field contains COUNT
                    has_count = any('COUNT(' in str(field).upper() for field in self.select_fields)
                    if has_count:
                        # Extract count from result - look for 'count' key or first value
                        if data and len(data) > 0:
                            if 'count' in data[0]:
                                count = data[0]['count']
                            else:
                                # Try to get first value if it's a count query
                                count = list(data[0].values())[0] if data[0] else 0
                    else:
                        count = len(data)

                cursor.close()
                self.connection.commit()

                return QueryResult(data=data, count=count)
            else:
                # For INSERT/UPDATE/DELETE without RETURNING
                cursor.close()
                self.connection.commit()

                return QueryResult(data=[], count=None)

        except Exception as e:
            self.connection.rollback()
            logger.error(f"Query execution error: {e}", exc_info=True, module="Postgres")
            raise


class PostgresConnection:
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.connection = None
        self._cursor = None
        self._connect()

    def _connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port,
                connect_timeout=10  # 10 second connection timeout
            )
            # Set autocommit to False for transaction support
            self.connection.autocommit = False
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}", module="Postgres")
            raise

    def __enter__(self):
        self._cursor = self.connection.cursor(cursor_factory=DictCursor)
        return self._cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and issubclass(exc_type, psycopg2.Error):
            self.connection.rollback()
            logger.error(f"DB - {exc_type} - {exc_val} - {traceback.format_exc()}", module="Postgres")
            raise exc_type(exc_val)
        elif exc_type and issubclass(exc_type, Exception):
            self.connection.rollback()
            logger.error(f"DB Exception - {exc_type} - {exc_val} - {traceback.format_exc()}", module="Postgres")
        else:
            if self._cursor:
                self._cursor.close()
            self.connection.commit()

    def table(self, table_name: str) -> QueryBuilder:
        """Create a query builder for a table"""
        return QueryBuilder(self.connection, table_name)

    @property
    def cursor(self):
        """Get cursor for manual queries"""
        if not self._cursor:
            self._cursor = self.connection.cursor(cursor_factory=DictCursor)
        return self._cursor

    def get_trigger_manager(self):
        """
        Get trigger manager instance for this connection
        Uses the workflow initialization which auto-detects existing triggers
        """
        from src.db.postgres.triggers import initialize_trigger_workflow
        return initialize_trigger_workflow(self.connection)


# Lazy Database Connection Manager
# Connection is only created when first accessed, with retry logic
class LazyPostgresConnection:
    """Lazy connection manager that retries on failure"""
    _connection = None
    _connection_params = None
    _max_retries = 10
    _retry_delay = 2  # seconds

    @classmethod
    def _get_connection_params(cls):
        """Get and validate connection parameters"""
        if cls._connection_params:
            return cls._connection_params

        db_host = os.environ.get('DATABASE_HOST')
        db_name = os.environ.get('DATABASE_NAME')
        db_user = os.environ.get('DATABASE_USER')
        db_password = os.environ.get('DATABASE_PASSWORD')
        db_port = os.environ.get('DATABASE_PORT', '5432')

        # Validate required environment variables
        missing_vars = []
        if not db_host:
            missing_vars.append('DATABASE_HOST')
        if not db_name:
            missing_vars.append('DATABASE_NAME')
        if not db_user:
            missing_vars.append('DATABASE_USER')
        if not db_password:
            missing_vars.append('DATABASE_PASSWORD')

        if missing_vars:
            error_msg = f"Missing required database environment variables: {', '.join(missing_vars)}"
            try:
                logger.warning(error_msg, module="Postgres")
            except Exception:
                print(f"WARNING [Postgres]: {error_msg}")
            # Don't raise - allow lazy connection to retry later
            return None

        # Convert port to integer
        try:
            db_port = int(db_port)
        except (ValueError, TypeError):
            try:
                logger.warning(f"Invalid DATABASE_PORT value: {db_port}. Using default 5432.", module="Postgres")
            except Exception:
                print(f"WARNING [Postgres]: Invalid DATABASE_PORT value: {db_port}. Using default 5432.")
            db_port = 5432

        cls._connection_params = {
            'host': db_host,
            'database': db_name,
            'user': db_user,
            'password': db_password,
            'port': db_port
        }
        return cls._connection_params

    @classmethod
    def _create_connection(cls, retry_count=0):
        """Create connection with retry logic"""
        params = cls._get_connection_params()
        if not params:
            return None

        try:
            conn = PostgresConnection(**params)
            return conn
        except Exception as e:
            if retry_count < cls._max_retries:
                try:
                    logger.warning(
                        f"Database connection attempt {retry_count + 1}/{cls._max_retries} failed: {e}. Retrying in {cls._retry_delay}s...",
                        module="Postgres"
                    )
                except Exception:
                    print(f"WARNING [Postgres]: Database connection attempt {retry_count + 1}/{cls._max_retries} failed: {e}. Retrying in {cls._retry_delay}s...")
                import time
                time.sleep(cls._retry_delay)
                return cls._create_connection(retry_count + 1)
            else:
                try:
                    logger.error(
                        f"Failed to establish database connection after {cls._max_retries} attempts: {e}",
                        module="Postgres"
                    )
                    logger.error(
                        f"Connection details - Host: {params['host']}, Port: {params['port']}, Database: {params['database']}, User: {params['user']}",
                        module="Postgres"
                    )
                except Exception:
                    print(f"ERROR [Postgres]: Failed to establish database connection after {cls._max_retries} attempts: {e}")
                # Don't raise - return None to allow graceful degradation
                return None

    @classmethod
    def get_connection(cls):
        """Get or create connection (lazy initialization)"""
        if cls._connection is None:
            cls._connection = cls._create_connection()
        else:
            # Check if connection is still valid
            try:
                if cls._connection.connection and cls._connection.connection.closed:
                    # Reconnect if connection was closed
                    cls._connection = cls._create_connection()
                else:
                    # Test connection with a simple query
                    try:
                        test_cursor = cls._connection.connection.cursor()
                        test_cursor.execute("SELECT 1")
                        test_cursor.close()
                    except Exception:
                        # Connection is dead, reconnect
                        cls._connection = cls._create_connection()
            except AttributeError:
                # Connection object doesn't have connection attribute (shouldn't happen)
                cls._connection = cls._create_connection()
        return cls._connection

    @classmethod
    def reset_connection(cls):
        """Reset connection (force reconnect)"""
        if cls._connection:
            try:
                if cls._connection.connection:
                    cls._connection.connection.close()
            except Exception:
                pass
        cls._connection = None


# Lazy connection - only created when first accessed
def get_db_connection():
    """Get database connection (lazy, with retry)"""
    return LazyPostgresConnection.get_connection()


# For backward compatibility - create connection object that uses lazy connection
# This allows existing code like `with db as cursor:` to work
class _LazyConnectionWrapper:
    """Wrapper that provides lazy connection access with retry logic"""
    def __enter__(self):
        conn = LazyPostgresConnection.get_connection()
        if conn is None:
            raise ConnectionError("Failed to establish database connection after retries. Check database is running and accessible.")
        return conn.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        conn = LazyPostgresConnection.get_connection()
        if conn:
            return conn.__exit__(exc_type, exc_val, exc_tb)

    def table(self, table_name: str) -> QueryBuilder:
        """Create a query builder for a table"""
        conn = LazyPostgresConnection.get_connection()
        if conn is None:
            raise ConnectionError("Database connection not available. Check database is running and accessible.")
        return conn.table(table_name)

    @property
    def cursor(self):
        """Get cursor for manual queries"""
        conn = LazyPostgresConnection.get_connection()
        if conn is None:
            raise ConnectionError("Database connection not available. Check database is running and accessible.")
        return conn.cursor

    def get_trigger_manager(self):
        """
        Get trigger manager instance for this connection
        Uses the workflow initialization which auto-detects existing triggers
        """
        # from src.db.postgres.triggers import initialize_trigger_workflow
        # return initialize_trigger_workflow(self.connection)

        conn = LazyPostgresConnection.get_connection()
        if conn is None:
            raise ConnectionError("Database connection not available. Check database is running and accessible.")
        # Delegate to the PostgresConnection's get_trigger_manager method
        return conn.get_trigger_manager()

# Create connection object for backward compatibility
# Usage: with connection as cursor: ...
connection = _LazyConnectionWrapper()
