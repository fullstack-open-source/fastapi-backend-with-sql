# PostgreSQL Triggers Management System

## Overview

This system provides a dynamic approach to manage PostgreSQL database triggers for automatic actions like:
- Auto-creating wallets when users are created
- Auto-updating timestamps
- Auto-updating post statistics
- And more...

## Quick Start

### 1. Setup All Triggers

```python
from src.db.postgres.setup_triggers import setup_all_triggers

# Setup all predefined triggers
results = setup_all_triggers()

print(f"Created {results['triggers_created']} triggers")
print(f"Success: {results['success']}")
print(f"Failed: {results['failed']}")
```

### 2. Setup Individual Triggers

```python
from src.db.postgres.postgres import connection
from src.db.postgres.triggers import setup_user_wallet_trigger

trigger_manager = connection.get_trigger_manager()

# Auto-create wallet when user is created
setup_user_wallet_trigger(trigger_manager)
```

## Available Triggers

### 1. Auto-Create Wallet on User Insert

Automatically creates a wallet with default values when a new user is created.

```python
from src.db.postgres.triggers import setup_user_wallet_trigger

trigger_manager = connection.get_trigger_manager()
setup_user_wallet_trigger(trigger_manager)
```

**Default Values:**
- `balance_credits`: 0.0
- `balance_points`: 20.0
- `ads_credits`: 0.0

### 2. Auto-Update Timestamp

Automatically updates the `last_updated` timestamp when a record is updated.

```python
from src.db.postgres.triggers import setup_updated_at_trigger

trigger_manager = connection.get_trigger_manager()
setup_updated_at_trigger(trigger_manager, "user")
setup_updated_at_trigger(trigger_manager, "posts")
```

### 3. Post Auto-Update Statistics

Automatically updates post-related statistics when posts are inserted or deleted.

```python
from src.db.postgres.triggers import setup_post_auto_update_trigger

trigger_manager = connection.get_trigger_manager()
setup_post_auto_update_trigger(trigger_manager, "posts")
```

## Creating Custom Triggers

### Example: Post Likes Counter

```python
from src.db.postgres.setup_triggers import create_custom_trigger
from src.db.postgres.triggers import TriggerEvent

function_body = """
-- Update post like count
IF TG_OP = 'INSERT' THEN
    UPDATE posts 
    SET likes_count = COALESCE(likes_count, 0) + 1 
    WHERE id = NEW.post_id;
ELSIF TG_OP = 'DELETE' THEN
    UPDATE posts 
    SET likes_count = GREATEST(COALESCE(likes_count, 0) - 1, 0) 
    WHERE id = OLD.post_id;
END IF;
RETURN COALESCE(NEW, OLD);
"""

create_custom_trigger(
    trigger_name="auto_update_post_likes_count",
    table_name="post_likes",
    function_body=function_body,
    event=TriggerEvent.AFTER_INSERT
)
```

### Example: Custom Trigger with Condition

```python
from src.db.postgres.triggers import TriggerManager, TriggerEvent

trigger_manager = connection.get_trigger_manager()

# Create function
function_body = """
-- Only update if status changed
IF OLD.status != NEW.status THEN
    INSERT INTO status_history (record_id, old_status, new_status, changed_at)
    VALUES (NEW.id, OLD.status, NEW.status, NOW());
END IF;
RETURN NEW;
"""

trigger_manager.create_trigger_function("track_status_changes", function_body)

# Create trigger with condition
trigger_manager.create_trigger(
    trigger_name="trigger_status_change",
    table_name="posts",
    function_name="track_status_changes",
    event=TriggerEvent.AFTER_UPDATE,
    condition="OLD.status IS DISTINCT FROM NEW.status"
)
```

## Managing Triggers

### List All Triggers

```python
from src.db.postgres.setup_triggers import list_all_triggers

# List all triggers
all_triggers = list_all_triggers()

# List triggers for specific table
user_triggers = list_all_triggers("user")

for trigger in user_triggers:
    print(f"{trigger['trigger_name']} on {trigger['table_name']}")
```

### Drop a Trigger

```python
from src.db.postgres.setup_triggers import drop_trigger

drop_trigger("trigger_auto_create_wallet_on_user_insert", "user")
```

### Using TriggerManager Directly

```python
from src.db.postgres.postgres import connection
from src.db.postgres.triggers import TriggerManager, TriggerEvent, TriggerFunctions

trigger_manager = connection.get_trigger_manager()

# Create custom function
function_body = TriggerFunctions.auto_update_updated_at()
trigger_manager.create_trigger_function("my_custom_function", function_body)

# Create trigger
trigger_manager.create_trigger(
    trigger_name="my_trigger",
    table_name="my_table",
    function_name="my_custom_function",
    event=TriggerEvent.BEFORE_UPDATE
)
```

## Trigger Events

Available trigger events from `TriggerEvent` enum:

- `BEFORE_INSERT` - Before a new row is inserted
- `AFTER_INSERT` - After a new row is inserted
- `BEFORE_UPDATE` - Before a row is updated
- `AFTER_UPDATE` - After a row is updated
- `BEFORE_DELETE` - Before a row is deleted
- `AFTER_DELETE` - After a row is deleted

## Predefined Trigger Functions

The `TriggerFunctions` class provides ready-to-use trigger functions:

1. `auto_create_wallet_on_user_insert()` - Creates wallet for new user
2. `auto_update_updated_at()` - Updates last_updated timestamp
3. `auto_update_post_stats()` - Updates post statistics
4. `log_audit_trail()` - Logs changes to audit table

## Best Practices

1. **Always check if trigger exists** before creating to avoid duplicates
2. **Use meaningful names** for triggers and functions
3. **Test triggers** in development before deploying to production
4. **Document custom triggers** in your codebase
5. **Use transactions** when creating multiple triggers

## Troubleshooting

### Trigger not firing

1. Check if trigger exists:
   ```python
   triggers = list_all_triggers("user")
   ```

2. Check trigger function:
   ```sql
   SELECT proname, prosrc FROM pg_proc WHERE proname = 'your_function_name';
   ```

3. Check for errors in PostgreSQL logs

### Trigger causing errors

1. Check the trigger function syntax
2. Ensure all referenced columns exist
3. Check data types match
4. Verify foreign key constraints

## Running Setup Script

You can run the setup script directly:

```bash
cd api
python -m src.db.postgres.setup_triggers
```

Or import and use:

```python
from src.db.postgres.setup_triggers import setup_all_triggers

if __name__ == "__main__":
    results = setup_all_triggers()
    print(f"Setup complete: {results}")
```

## Integration with Application Startup

You can initialize triggers when your application starts:

```python
# In your server.py or main application file
from src.db.postgres.setup_triggers import setup_all_triggers

@app.on_event("startup")
async def startup_event():
    """Initialize database triggers on startup"""
    logger.info("Setting up database triggers...")
    results = setup_all_triggers()
    logger.info(f"Database triggers setup complete: {results}")
```

