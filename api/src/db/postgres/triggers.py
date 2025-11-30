from psycopg2.extras import DictCursor
from typing import Dict, List, Optional
from src.logger.logger import logger
from enum import Enum
import psycopg2
from dataclasses import dataclass



class TriggerEvent(Enum):
    """Trigger event types"""
    BEFORE_INSERT = "BEFORE INSERT"
    AFTER_INSERT = "AFTER INSERT"
    BEFORE_UPDATE = "BEFORE UPDATE"
    AFTER_UPDATE = "AFTER UPDATE"
    BEFORE_DELETE = "BEFORE DELETE"
    AFTER_DELETE = "AFTER DELETE"


@dataclass
class TriggerDefinition:
    """Definition of a trigger to be registered"""
    name: str
    table_name: str
    function_name: str
    function_body: str
    event: TriggerEvent
    condition: Optional[str] = None
    description: Optional[str] = None


class TriggerRegistry:
    """
    Registry for trigger definitions
    Allows dynamic registration of new triggers
    """

    def __init__(self):
        self.triggers: Dict[str, TriggerDefinition] = {}

    def register(self, trigger_def: TriggerDefinition) -> bool:
        """
        Register a new trigger definition

        Args:
            trigger_def: TriggerDefinition object

        Returns:
            True if registered successfully
        """
        if trigger_def.name in self.triggers:
            logger.warning(f"Trigger '{trigger_def.name}' already registered, overwriting...", module="Trigger")

        self.triggers[trigger_def.name] = trigger_def
        return True

    def get(self, trigger_name: str) -> Optional[TriggerDefinition]:
        """Get a registered trigger definition"""
        return self.triggers.get(trigger_name)

    def list_all(self) -> List[TriggerDefinition]:
        """List all registered triggers"""
        return list(self.triggers.values())

    def list_for_table(self, table_name: str) -> List[TriggerDefinition]:
        """List triggers for a specific table"""
        return [t for t in self.triggers.values() if t.table_name == table_name]

    def remove(self, trigger_name: str) -> bool:
        """Remove a trigger from registry"""
        if trigger_name in self.triggers:
            del self.triggers[trigger_name]
            return True
        return False


class TriggerManager:
    """
    Dynamic PostgreSQL Trigger Management System
    Workflow:
    1. Initialize manager with database connection
    2. Auto-detect existing triggers in database
    3. Register new trigger definitions
    4. Create and manage triggers
    """

    def __init__(self, connection):
        self.connection = connection
        self.registered_triggers: Dict[str, Dict] = {}
        self.registry = TriggerRegistry()
        self.detected_triggers: Dict[str, Dict] = {}

        # Auto-detect existing triggers on initialization
        self._detect_existing_triggers()

    def _detect_existing_triggers(self) -> Dict[str, Dict]:
        """
        Step 3: Auto-detect existing triggers in the database
        This is called automatically on initialization

        Returns:
            Dictionary of detected triggers by table and operation
        """
        try:
            cursor = self.connection.cursor(cursor_factory=DictCursor)

            sql = """
            SELECT
                tgname as trigger_name,
                tgrelid::regclass as table_name,
                proname as function_name,
                CASE
                    WHEN tgtype & 2 = 2 THEN 'BEFORE'
                    ELSE 'AFTER'
                END as timing,
                CASE
                    WHEN tgtype & 4 = 4 THEN 'INSERT'
                    WHEN tgtype & 8 = 8 THEN 'DELETE'
                    WHEN tgtype & 16 = 16 THEN 'UPDATE'
                END as event,
                tgqual::text as condition
            FROM pg_trigger t
            JOIN pg_proc p ON t.tgfoid = p.oid
            WHERE tgisinternal = false
            ORDER BY tgrelid::regclass::text, tgname;
            """

            cursor.execute(sql)
            triggers = [dict(row) for row in cursor.fetchall()]
            cursor.close()

            # Organize by table and operation
            for trigger in triggers:
                table = trigger['table_name']
                event = f"{trigger['timing']} {trigger['event']}"
                key = f"{table}_{event}"

                if key not in self.detected_triggers:
                    self.detected_triggers[key] = []

                self.detected_triggers[key].append(trigger)
                self.registered_triggers[trigger['trigger_name']] = trigger

            return self.detected_triggers

        except Exception as e:
            logger.error(f"Error detecting triggers: {e}", exc_info=True, module="Trigger")
            return {}

    def get_triggers_for_operation(self, table_name: str, event: TriggerEvent) -> List[Dict]:
        """
        Get all triggers for a specific table and operation

        Args:
            table_name: Name of the table
            event: Trigger event type

        Returns:
            List of trigger dictionaries
        """
        key = f"{table_name}_{event.value}"
        return self.detected_triggers.get(key, [])

    def has_trigger(self, table_name: str, event: TriggerEvent, trigger_name: Optional[str] = None) -> bool:
        """
        Check if a trigger exists for a table and operation

        Args:
            table_name: Name of the table
            event: Trigger event type
            trigger_name: Optional specific trigger name to check

        Returns:
            True if trigger exists
        """
        triggers = self.get_triggers_for_operation(table_name, event)

        if trigger_name:
            return any(t['trigger_name'] == trigger_name for t in triggers)

        return len(triggers) > 0

    def register_trigger(self, trigger_def: TriggerDefinition) -> bool:
        """
        Step 4: Register a new trigger definition

        Args:
            trigger_def: TriggerDefinition object

        Returns:
            True if registered successfully
        """
        return self.registry.register(trigger_def)

    def create_trigger_from_registry(self, trigger_name: str) -> bool:
        """
        Create a trigger from registry

        Args:
            trigger_name: Name of registered trigger

        Returns:
            True if successful
        """
        trigger_def = self.registry.get(trigger_name)
        if not trigger_def:
            logger.error(f"Trigger '{trigger_name}' not found in registry", module="Trigger")
            return False

        # Create function
        if not self.create_trigger_function(trigger_def.function_name, trigger_def.function_body):
            return False

        # Create trigger
        return self.create_trigger(
            trigger_name=trigger_def.name,
            table_name=trigger_def.table_name,
            function_name=trigger_def.function_name,
            event=trigger_def.event,
            condition=trigger_def.condition
        )

    def setup_all_registered_triggers(self) -> Dict[str, bool]:
        """
        Set up all registered triggers

        Returns:
            Dictionary with trigger names and success status
        """
        results = {}
        for trigger_def in self.registry.list_all():
            results[trigger_def.name] = self.create_trigger_from_registry(trigger_def.name)
        return results

    def function_exists(self, function_name: str) -> bool:
        """
        Check if a trigger function already exists in the database

        Args:
            function_name: Name of the function to check

        Returns:
            True if function exists, False otherwise
        """
        try:
            cursor = self.connection.cursor(cursor_factory=DictCursor)
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_proc
                    WHERE proname = %s
                )
            """, (function_name,))
            exists = cursor.fetchone()[0]
            cursor.close()
            return exists
        except Exception as e:
            logger.error(f"Error checking if function '{function_name}' exists: {e}", module="Trigger")
            return False

    def create_trigger_function(self, function_name: str, function_body: str, replace: bool = True, max_retries: int = 3, skip_if_exists: bool = True) -> bool:
        """
        Create or replace a PostgreSQL trigger function with concurrency handling

        Args:
            function_name: Name of the function
            function_body: SQL function body
            replace: If True, uses CREATE OR REPLACE
            max_retries: Maximum number of retry attempts for concurrent updates
            skip_if_exists: If True, skip creation if function already exists (idempotent mode)

        Returns:
            True if successful or already exists, False otherwise
        """
        import time
        import random

        # First, check if function already exists (fast path for idempotent operations)
        if skip_if_exists and self.function_exists(function_name):
            return True

        cursor = None
        for attempt in range(max_retries):
            try:
                cursor = self.connection.cursor(cursor_factory=DictCursor)

                # Use advisory lock to prevent concurrent execution
                # Hash the function name to get a unique lock ID
                lock_id = hash(function_name) % (2**31)  # PostgreSQL advisory lock range

                # Try to acquire advisory lock (non-blocking)
                cursor.execute("SELECT pg_try_advisory_lock(%s)", (lock_id,))
                lock_acquired = cursor.fetchone()[0]

                if not lock_acquired:
                    # Another process is creating this function
                    cursor.close()
                    # Check if function exists now (another process may have created it)
                    if self.function_exists(function_name):
                        return True

                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) + random.uniform(0, 0.5)  # Shorter wait times
                        time.sleep(wait_time)
                        continue
                    else:
                        # Final attempt - check one more time if function exists
                        if self.function_exists(function_name):
                            return True
                        logger.error(f"Could not acquire lock for '{function_name}' after {max_retries} attempts", module="Trigger")
                        return False

                # Double-check if function exists (another process may have created it while we waited)
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM pg_proc
                        WHERE proname = %s
                    )
                """, (function_name,))
                function_exists = cursor.fetchone()[0]

                # If function exists and we're in skip mode, just return success
                if skip_if_exists and function_exists:
                    cursor.execute("SELECT pg_advisory_unlock(%s)", (lock_id,))
                    cursor.close()
                    return True

                create_or_replace = "CREATE OR REPLACE FUNCTION" if replace else "CREATE FUNCTION"

                # Check if function_body already has DECLARE (means it has its own BEGIN/END block)
                function_body_clean = function_body.strip()
                function_body_upper = function_body_clean.upper()
                has_declare = function_body_upper.startswith('DECLARE')
                has_begin = 'BEGIN' in function_body_upper
                has_end = 'END;' in function_body_clean or 'END ;' in function_body_clean
                has_return = 'RETURN' in function_body_upper

                # If function has DECLARE, it must have its own BEGIN/END structure
                # Also check if it already has a complete BEGIN...END block
                if has_declare or (has_begin and has_end):
                    # Function body already has complete structure with DECLARE/BEGIN/END
                    # Use it as-is, just ensure it has RETURN if needed
                    if not has_return:
                        # Add RETURN NEW if not present
                        function_body = f"{function_body}\n                RETURN NEW;"

                    # Strip leading whitespace from each line to avoid indentation issues
                    lines = function_body.split('\n')
                    # Find minimum indentation (excluding empty lines)
                    min_indent = min((len(line) - len(line.lstrip()) for line in lines if line.strip()), default=0)
                    if min_indent > 0:
                        # Remove the minimum indentation from all lines
                        function_body = '\n'.join(line[min_indent:] if len(line) > min_indent else line for line in lines)

                    sql = f"""
                    {create_or_replace} {function_name}()
                    RETURNS TRIGGER AS $$
                    {function_body}
                    $$ LANGUAGE plpgsql;
                    """
                else:
                    # Function body needs to be wrapped in BEGIN/END
                    if not has_return:
                        # Add RETURN NEW if not present
                        function_body = f"{function_body}\n                RETURN NEW;"

                    sql = f"""
                    {create_or_replace} {function_name}()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        {function_body}
                    END;
                    $$ LANGUAGE plpgsql;
                    """

                cursor.execute(sql)
                self.connection.commit()

                # Release advisory lock
                cursor.execute("SELECT pg_advisory_unlock(%s)", (lock_id,))
                cursor.close()

                return True

            except psycopg2.errors.InternalError_ as e:
                # Handle "tuple concurrently updated" error
                error_msg = str(e)
                if "tuple concurrently updated" in error_msg.lower():
                    self.connection.rollback()
                    if cursor:
                        try:
                            cursor.close()
                        except Exception:
                            pass

                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
                        time.sleep(wait_time)
                        continue
                    else:
                        # Last attempt failed, check if function exists (another process may have succeeded)
                        try:
                            cursor = self.connection.cursor(cursor_factory=DictCursor)
                            cursor.execute("""
                                SELECT EXISTS (
                                    SELECT 1 FROM pg_proc
                                    WHERE proname = %s
                                )
                            """, (function_name,))
                            exists = cursor.fetchone()[0]
                            cursor.close()
                            if exists:
                                return True
                        except Exception:
                            pass
                        logger.error(f"Failed to create trigger function '{function_name}' after {max_retries} attempts: {e}", module="Trigger")
                        return False
                else:
                    # Other InternalError, re-raise
                    raise

            except Exception as e:
                self.connection.rollback()
                if cursor:
                    try:
                        cursor.close()
                    except Exception:
                        pass

                # For non-concurrency errors, don't retry
                if "tuple concurrently updated" not in str(e).lower():
                    logger.error(f"Error creating trigger function '{function_name}': {e}", exc_info=True, module="Trigger")
                    return False

                # Retry for concurrent update errors
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Failed to create trigger function '{function_name}' after {max_retries} attempts: {e}", module="Trigger")
                    return False

        return False

    def create_trigger(
        self,
        trigger_name: str,
        table_name: str,
        function_name: str,
        event: TriggerEvent,
        condition: Optional[str] = None
    ) -> bool:
        """
        Create a PostgreSQL trigger

        Args:
            trigger_name: Name of the trigger
            table_name: Table to attach trigger to
            function_name: Function to call
            event: Trigger event (BEFORE/AFTER INSERT/UPDATE/DELETE)
            condition: Optional WHEN condition for the trigger

        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor(cursor_factory=DictCursor)

            # Check if trigger already exists
            check_sql = """
            SELECT EXISTS (
                SELECT 1 FROM pg_trigger
                WHERE tgname = %s
            );
            """
            cursor.execute(check_sql, (trigger_name,))
            exists = cursor.fetchone()[0]

            # Quote table name to handle reserved words like "user"
            quoted_table_name = f'"{table_name}"'

            if exists:
                # Drop existing trigger
                drop_sql = f'DROP TRIGGER IF EXISTS {trigger_name} ON {quoted_table_name};'
                cursor.execute(drop_sql)

            # Create trigger
            if condition:
                create_sql = f"""
                CREATE TRIGGER {trigger_name}
                {event.value} ON {quoted_table_name}
                WHEN ({condition})
                FOR EACH ROW
                EXECUTE FUNCTION {function_name}();
                """
            else:
                create_sql = f"""
                CREATE TRIGGER {trigger_name}
                {event.value} ON {quoted_table_name}
                FOR EACH ROW
                EXECUTE FUNCTION {function_name}();
                """

            cursor.execute(create_sql)
            self.connection.commit()

            # Register trigger in manager
            self.registered_triggers[trigger_name] = {
                "table": table_name,
                "function": function_name,
                "event": event,
                "condition": condition,
                "timing": event.value.split()[0],
                "operation": event.value.split()[1]
            }

            # Update detected triggers
            key = f"{table_name}_{event.value}"
            if key not in self.detected_triggers:
                self.detected_triggers[key] = []

            self.detected_triggers[key].append({
                "trigger_name": trigger_name,
                "table_name": table_name,
                "function_name": function_name,
                "timing": event.value.split()[0],
                "event": event.value.split()[1],
                "condition": condition
            })

            cursor.close()
            return True

        except Exception as e:
            logger.error(f"Error creating trigger '{trigger_name}' on table '{table_name}' ({event.value}): {e}", exc_info=True, module="Trigger")
            self.connection.rollback()
            return False

    def drop_trigger(self, trigger_name: str, table_name: str) -> bool:
        """
        Drop a PostgreSQL trigger

        Args:
            trigger_name: Name of the trigger
            table_name: Table the trigger is attached to

        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor(cursor_factory=DictCursor)
            # Quote table name to handle reserved words
            quoted_table_name = f'"{table_name}"'
            cursor.execute(f'DROP TRIGGER IF EXISTS {trigger_name} ON {quoted_table_name};')
            self.connection.commit()
            cursor.close()

            # Remove from registry
            if trigger_name in self.registered_triggers:
                del self.registered_triggers[trigger_name]

            return True

        except Exception as e:
            logger.error(f"Error dropping trigger '{trigger_name}' from table '{table_name}': {e}", exc_info=True, module="Trigger")
            self.connection.rollback()
            return False

    def list_triggers(self, table_name: Optional[str] = None) -> List[Dict]:
        """
        List all triggers or triggers for a specific table

        Args:
            table_name: Optional table name to filter by

        Returns:
            List of trigger dictionaries
        """
        try:
            cursor = self.connection.cursor(cursor_factory=DictCursor)

            if table_name:
                sql = """
                SELECT
                    tgname as trigger_name,
                    tgrelid::regclass as table_name,
                    proname as function_name,
                    CASE
                        WHEN tgtype & 2 = 2 THEN 'BEFORE'
                        ELSE 'AFTER'
                    END as timing,
                    CASE
                        WHEN tgtype & 4 = 4 THEN 'INSERT'
                        WHEN tgtype & 8 = 8 THEN 'DELETE'
                        WHEN tgtype & 16 = 16 THEN 'UPDATE'
                    END as event
                FROM pg_trigger t
                JOIN pg_proc p ON t.tgfoid = p.oid
                WHERE tgrelid = %s::regclass
                AND tgisinternal = false;
                """
                cursor.execute(sql, (table_name,))
            else:
                sql = """
                SELECT
                    tgname as trigger_name,
                    tgrelid::regclass as table_name,
                    proname as function_name,
                    CASE
                        WHEN tgtype & 2 = 2 THEN 'BEFORE'
                        ELSE 'AFTER'
                    END as timing,
                    CASE
                        WHEN tgtype & 4 = 4 THEN 'INSERT'
                        WHEN tgtype & 8 = 8 THEN 'DELETE'
                        WHEN tgtype & 16 = 16 THEN 'UPDATE'
                    END as event
                FROM pg_trigger t
                JOIN pg_proc p ON t.tgfoid = p.oid
                WHERE tgisinternal = false;
                """
                cursor.execute(sql)

            triggers = [dict(row) for row in cursor.fetchall()]
            cursor.close()

            return triggers

        except Exception as e:
            logger.error(f"Error listing triggers for table '{table_name or 'all'}': {e}", exc_info=True, module="Trigger")
            return []


class TriggerFunctions:
    """
    Predefined trigger functions for common operations
    Add new functions here as needed
    """
    pass

# ============================================================================
# WORKFLOW FUNCTIONS - Step 4: Register and setup triggers
# ============================================================================

def initialize_trigger_workflow(connection) -> TriggerManager:
    """
    Complete workflow initialization:
    1. Create trigger manager
    2. Auto-detect existing triggers
    3. Ready to register new triggers

    Args:
        connection: Database connection

    Returns:
        TriggerManager instance
    """
    manager = TriggerManager(connection)
    return manager

