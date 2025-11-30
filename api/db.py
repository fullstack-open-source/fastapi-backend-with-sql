#!/usr/bin/env python3
"""
Database CLI - Similar to Prisma CLI
Usage:
    python3 db.py push          # Push schema to database (like prisma db push)
    python3 db.py pull          # Pull schema from database (like prisma db pull)
    python3 db.py migrate       # Create a new migration (like prisma migrate dev)
    python3 db.py upgrade       # Apply all pending migrations (like prisma migrate deploy)
    python3 db.py downgrade     # Rollback last migration
    python3 db.py history       # Show migration history
    python3 db.py current       # Show current migration
    python3 db.py seed          # Seed the database with default data
    python3 db.py reset         # Reset database (drop all tables and recreate)
"""
import os
import sys
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def _get_alembic_config():
    """Get Alembic configuration with correct paths"""
    from alembic.config import Config

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    alembic_ini_path = os.path.join(script_dir, "alembic.ini")

    if not os.path.exists(alembic_ini_path):
        print(f"❌ alembic.ini not found at: {alembic_ini_path}")
        print(f"💡 Current working directory: {os.getcwd()}")
        print(f"💡 Script directory: {script_dir}")
        sys.exit(1)

    # Change to script directory to ensure relative paths work
    # Alembic needs to be run from the directory containing alembic.ini
    original_cwd = os.getcwd()
    os.chdir(script_dir)

    try:
        alembic_cfg = Config("alembic.ini")  # Use relative path since we changed directory
        return alembic_cfg, original_cwd
    except Exception as e:
        os.chdir(original_cwd)  # Restore on error
        raise


def _test_db_connection():
    """Test database connection before running migrations"""
    try:
        from sqlalchemy import create_engine, text
        import os

        # Get database connection parameters
        DATABASE_HOST = os.environ.get('DATABASE_HOST')
        DATABASE_NAME = os.environ.get('DATABASE_NAME')
        DATABASE_USER = os.environ.get('DATABASE_USER')
        DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
        DATABASE_PORT = os.environ.get('DATABASE_PORT', '5432')

        if not all([DATABASE_HOST, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD]):
            print("❌ Database environment variables not set.")
            print("💡 Required: DATABASE_HOST, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD")
            sys.exit(1)

        # Build connection URL
        DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

        # Test connection
        test_engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("💡 Install dependencies: pip install sqlalchemy alembic psycopg2-binary")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Make sure DATABASE_HOST, DATABASE_NAME, DATABASE_USER, and DATABASE_PASSWORD are set correctly")
        sys.exit(1)


def push():
    """
    Push schema directly to database without creating a migration.
    Similar to `prisma db push`
    """
    print("🔄 Pushing schema to database...")

    from src.db.models.base import init_db, engine

    if not engine:
        print("❌ Database connection not configured. Check environment variables.")
        sys.exit(1)

    try:
        init_db()
        print("✅ Schema pushed successfully!")
    except Exception as e:
        print(f"❌ Failed to push schema: {e}")
        sys.exit(1)


def migrate(message: str = None):
    """
    Create a new migration based on model changes.
    Similar to `prisma migrate dev`
    """
    if not message:
        message = input("Enter migration message: ").strip()
        if not message:
            print("❌ Migration message is required")
            sys.exit(1)

    print(f"🔄 Creating migration: {message}")

    # Test database connection first
    _test_db_connection()

    # Use Alembic to create migration
    from alembic import command

    alembic_cfg, original_cwd = _get_alembic_config()

    try:
        command.revision(alembic_cfg, autogenerate=True, message=message)
        print("✅ Migration created successfully!")
        print("📝 Review the generated migration file in alembic/versions/")
    except Exception as e:
        print(f"❌ Failed to create migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        os.chdir(original_cwd)


def upgrade(revision: str = "head"):
    """
    Apply all pending migrations.
    Similar to `prisma migrate deploy`
    """
    print(f"🔄 Applying migrations (target: {revision})...")

    # Test database connection first
    _test_db_connection()

    from alembic import command

    alembic_cfg, original_cwd = _get_alembic_config()

    try:
        command.upgrade(alembic_cfg, revision)
        print("✅ Migrations applied successfully!")
    except Exception as e:
        print(f"❌ Failed to apply migrations: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        os.chdir(original_cwd)


def downgrade(revision: str = "-1"):
    """
    Rollback migrations.
    Use "-1" for last migration, or specific revision ID
    """
    print(f"🔄 Rolling back migration (target: {revision})...")

    # Test database connection first
    _test_db_connection()

    from alembic import command

    alembic_cfg, original_cwd = _get_alembic_config()

    try:
        command.downgrade(alembic_cfg, revision)
        print("✅ Migration rolled back successfully!")
    except Exception as e:
        print(f"❌ Failed to rollback migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        os.chdir(original_cwd)


def history():
    """
    Show migration history.
    """
    print("📜 Migration History:")
    print("-" * 50)

    from alembic import command

    alembic_cfg, original_cwd = _get_alembic_config()

    try:
        command.history(alembic_cfg)
    except Exception as e:
        print(f"❌ Failed to get history: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        os.chdir(original_cwd)


def current():
    """
    Show current migration status.
    """
    print("📍 Current Migration Status:")
    print("-" * 50)

    from alembic import command

    alembic_cfg, original_cwd = _get_alembic_config()

    try:
        command.current(alembic_cfg)
    except Exception as e:
        print(f"❌ Failed to get current status: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        os.chdir(original_cwd)


def seed():
    """
    Seed the database with default data.
    Similar to `prisma db seed`
    """
    print("🌱 Seeding database with default data...")

    from src.db.models.base import SessionLocal, engine
    from src.db.models import Permission, Group, GroupPermission

    if not engine:
        print("❌ Database connection not configured. Check environment variables.")
        sys.exit(1)

    db = SessionLocal()

    try:
        # ========================================================================
        # ENDPOINT PERMISSIONS MAPPING
        # ========================================================================
        # This section documents all API endpoints and their required permissions
        # for better access control management.
        #
        # Format: "METHOD /path" -> "permission_codename"
        # ========================================================================

        ENDPOINT_PERMISSIONS = {
            # ====================================================================
            # AUTHENTICATION ROUTER (/auth/*)
            # ====================================================================
            "POST /auth/login-with-password": None,  # Public endpoint
            "POST /auth/login-with-otp": None,  # Public endpoint
            "POST /auth/check-user-availability": None,  # Public endpoint
            "POST /auth/send-one-time-password": None,  # Public endpoint
            "POST /auth/verify-one-time-password": None,  # Public endpoint
            "POST /auth/verify": None,  # Public endpoint (signup)
            "POST /auth/forget-password": None,  # Public endpoint
            "POST /auth/refresh-token": None,  # Public endpoint (uses refresh token)
            "POST /auth/set-password": "edit_profile",
            "POST /auth/change-password": "edit_profile",
            "POST /auth/logout": "view_profile",
            "POST /auth/verify-email-and-phone": None,  # Public endpoint
            "GET /auth/token-info": None,  # Public endpoint (uses token validation)
            "POST /auth/token-info": None,  # Public endpoint (uses token validation)

            # ====================================================================
            # PROFILE ROUTER (/settings/*)
            # ====================================================================
            "GET /settings/profile": "view_profile",
            "GET /settings/profile/{user_id}": "view_user",
            "POST /settings/update-profile-picture": "edit_profile",
            "POST /settings/update-profile": "edit_profile",
            "POST /settings/profile-accessibility": "edit_profile",
            "POST /settings/profile-language": "edit_profile",
            "POST /settings/change-email": "edit_profile",
            "POST /settings/change-phone": "edit_profile",
            "POST /settings/send-phone-otp": "edit_profile",
            "POST /settings/update-theme": "edit_profile",
            "POST /settings/deactivate-account": "edit_profile",
            "POST /settings/delete-account": "edit_profile",
            "GET /settings/get-settings": "view_profile",
            "POST /settings/update-timezone": "edit_profile",

            # ====================================================================
            # PERMISSIONS ROUTER (/permissions/*, /groups/*, /users/*)
            # ====================================================================
            "GET /permissions": "view_permission",
            "GET /permissions/{permission_id}": "view_permission",
            "POST /permissions": "add_permission",
            "PUT /permissions/{permission_id}": "edit_permission",
            "DELETE /permissions/{permission_id}": "delete_permission",
            "GET /groups": "view_group",
            "GET /groups/{group_id}": "view_group",
            "POST /groups": "add_group",
            "PUT /groups/{group_id}": "edit_group",
            "DELETE /groups/{group_id}": "delete_group",
            "POST /groups/{group_id}/permissions": "edit_group",
            "GET /users/{user_id}/groups": "view_user",
            "GET /users/{user_id}/permissions": "view_user",
            "POST /users/{user_id}/groups": "assign_groups",
            "GET /users/me/groups": "view_profile",
            "GET /users/me/permissions": "view_profile",

            # ====================================================================
            # DASHBOARD ROUTER (/dashboard/*)
            # ====================================================================
            "GET /dashboard/overview": "view_dashboard",
            "GET /dashboard/users-by-status": "view_dashboard",
            "GET /dashboard/users-by-type": "view_dashboard",
            "GET /dashboard/users-by-auth-type": "view_dashboard",
            "GET /dashboard/users-by-country": "view_dashboard",
            "GET /dashboard/users-by-language": "view_dashboard",
            "GET /dashboard/user-growth": "view_dashboard",
            "GET /dashboard/recent-sign-ins": "view_dashboard",
            "GET /dashboard/all-statistics": "view_dashboard",

            # ====================================================================
            # ACTIVITY ROUTER (/activity/*)
            # ====================================================================
            "POST /activity/logs": "create_activity_log",
            "GET /activity/logs": "view_activity_log",
            "GET /activity/logs/{log_id}": "view_activity_log",
            "GET /activity/users/{user_id}/logs": "view_activity_log",
            "GET /activity/me/logs": "view_own_activity_log",
            "GET /activity/statistics": "view_activity_statistics",
            "DELETE /activity/logs/cleanup": "delete_activity_log",

            # ====================================================================
            # UPLOAD ROUTER (/upload-media, /delete-media)
            # ====================================================================
            "POST /upload-media": "add_upload",
            "DELETE /delete-media": "delete_upload",

            # ====================================================================
            # HEALTH ROUTER (/health/*)
            # ====================================================================
            "GET /health/database": "view_system_health",
            "GET /health/storage": "view_system_health",
            "GET /health/system": None,  # Public endpoint
            "GET /health/test-sentry": "test_sentry",
        }

        # ========================================================================
        # PERMISSION DEFINITIONS
        # ========================================================================
        # Comprehensive list of all permissions organized by category
        default_permissions = [
            # -----------------------------------
            # PROFILE
            # -----------------------------------
            {"name": "View Profile", "codename": "view_profile", "description": "Can view own profile", "category": "profile"},
            {"name": "Edit Profile", "codename": "edit_profile", "description": "Can edit own profile", "category": "profile"},
            {"name": "View User", "codename": "view_user", "description": "Can view other users", "category": "profile"},
            {"name": "Add User", "codename": "add_user", "description": "Can create new users", "category": "profile"},
            {"name": "Edit User", "codename": "edit_user", "description": "Can edit other users", "category": "profile"},
            {"name": "Delete User", "codename": "delete_user", "description": "Can delete users", "category": "profile"},
            {"name": "Suspend User", "codename": "suspend_user", "description": "Can suspend/block users", "category": "profile"},
            {"name": "Activate User", "codename": "activate_user", "description": "Can activate suspended users", "category": "profile"},
            {"name": "Reset User Password", "codename": "reset_user_password", "description": "Can reset password for users", "category": "profile"},
            {"name": "Force Logout User", "codename": "force_logout", "description": "Can force user to logout", "category": "profile"},

            # -----------------------------------
            # PERMISSIONS
            # -----------------------------------
            {"name": "View Permission", "codename": "view_permission", "description": "Can view permissions", "category": "permissions"},
            {"name": "Add Permission", "codename": "add_permission", "description": "Can add permissions", "category": "permissions"},
            {"name": "Edit Permission", "codename": "edit_permission", "description": "Can edit permissions", "category": "permissions"},
            {"name": "Delete Permission", "codename": "delete_permission", "description": "Can delete permissions", "category": "permissions"},
            {"name": "Assign Permissions", "codename": "assign_permissions", "description": "Can assign permissions to groups", "category": "permissions"},
            {"name": "Revoke Permissions", "codename": "revoke_permissions", "description": "Can remove permissions from groups", "category": "permissions"},

            # -----------------------------------
            # GROUPS / ROLES
            # -----------------------------------
            {"name": "View Group", "codename": "view_group", "description": "Can view groups", "category": "groups"},
            {"name": "Add Group", "codename": "add_group", "description": "Can add groups", "category": "groups"},
            {"name": "Edit Group", "codename": "edit_group", "description": "Can edit groups", "category": "groups"},
            {"name": "Delete Group", "codename": "delete_group", "description": "Can delete groups", "category": "groups"},
            {"name": "Assign Groups", "codename": "assign_groups", "description": "Can assign groups to users", "category": "groups"},

            # -----------------------------------
            # DASHBOARD
            # -----------------------------------
            {"name": "View Dashboard", "codename": "view_dashboard", "description": "Can view dashboard", "category": "dashboard"},

            # -----------------------------------
            # ACTIVITY LOGS
            # -----------------------------------
            {"name": "Create Activity Log", "codename": "create_activity_log", "description": "Can create activity logs", "category": "activity"},
            {"name": "View Activity Log", "codename": "view_activity_log", "description": "Can view activity logs", "category": "activity"},
            {"name": "View Own Activity Log", "codename": "view_own_activity_log", "description": "Can view own activity logs", "category": "activity"},
            {"name": "View Activity Statistics", "codename": "view_activity_statistics", "description": "Can view activity statistics", "category": "activity"},
            {"name": "Delete Activity Log", "codename": "delete_activity_log", "description": "Can delete activity logs", "category": "activity"},
            {"name": "Export Activity Log", "codename": "export_activity_log", "description": "Can export activity logs", "category": "activity"},
            {"name": "Monitor User Sessions", "codename": "monitor_user_sessions", "description": "Can view current user sessions", "category": "activity"},
            {"name": "Terminate User Session", "codename": "terminate_user_session", "description": "Can terminate active user sessions", "category": "activity"},

            # -----------------------------------
            # FILE UPLOAD
            # -----------------------------------
            {"name": "Add Upload", "codename": "add_upload", "description": "Can upload files", "category": "upload"},
            {"name": "Delete Upload", "codename": "delete_upload", "description": "Can delete uploaded files", "category": "upload"},

            # -----------------------------------
            # SYSTEM HEALTH
            # -----------------------------------
            {"name": "View System Health", "codename": "view_system_health", "description": "Can view system health status", "category": "system"},
            {"name": "Test Sentry", "codename": "test_sentry", "description": "Can test Sentry error tracking", "category": "system"},

            # -----------------------------------
            # SECURITY / AUTH
            # -----------------------------------
            {"name": "View Login Attempts", "codename": "view_login_attempts", "description": "Can view failed/success login attempts", "category": "security"},
            {"name": "Clear Login Attempts", "codename": "clear_login_attempts", "description": "Can clear login attempt records", "category": "security"},
            {"name": "Manage 2FA", "codename": "manage_2fa", "description": "Can enable/disable 2FA for users", "category": "security"},
            {"name": "View API Keys", "codename": "view_api_keys", "description": "Can view API keys", "category": "security"},
            {"name": "Generate API Key", "codename": "generate_api_key", "description": "Can create new API keys", "category": "security"},
            {"name": "Revoke API Key", "codename": "revoke_api_key", "description": "Can revoke API keys", "category": "security"},

            # -----------------------------------
            # SETTINGS
            # -----------------------------------
            {"name": "View Settings", "codename": "view_settings", "description": "Can view global settings", "category": "settings"},
            {"name": "Edit Settings", "codename": "edit_settings", "description": "Can update global system settings", "category": "settings"},

            # -----------------------------------
            # NOTIFICATIONS
            # -----------------------------------
            {"name": "View Notifications", "codename": "view_notifications", "description": "Can view notifications", "category": "notifications"},
            {"name": "Send Notifications", "codename": "send_notifications", "description": "Can send notifications", "category": "notifications"},
            {"name": "Delete Notifications", "codename": "delete_notifications", "description": "Can delete notifications", "category": "notifications"},

            # -----------------------------------
            # BILLING (if using SaaS)
            # -----------------------------------
            {"name": "View Billing", "codename": "view_billing", "description": "Can view billing information", "category": "billing"},
            {"name": "Edit Subscription", "codename": "edit_subscription", "description": "Can update subscription plans", "category": "billing"},
            {"name": "Refund Payment", "codename": "refund_payment", "description": "Can issue customer refunds", "category": "billing"},
            {"name": "View Invoices", "codename": "view_invoices", "description": "Can view invoices", "category": "billing"},

            # -----------------------------------
            # CONTENT MANAGEMENT
            # -----------------------------------
            {"name": "Add Content", "codename": "add_content", "description": "Can create content", "category": "content"},
            {"name": "Edit Content", "codename": "edit_content", "description": "Can edit content", "category": "content"},
            {"name": "Delete Content", "codename": "delete_content", "description": "Can delete content", "category": "content"},
            {"name": "Publish Content", "codename": "publish_content", "description": "Can publish content", "category": "content"},
            {"name": "Unpublish Content", "codename": "unpublish_content", "description": "Can unpublish content", "category": "content"},

            # -----------------------------------
            # API / DEVELOPER TOOLS
            # -----------------------------------
            {"name": "View API Usage", "codename": "view_api_usage", "description": "Can view API usage statistics", "category": "developer"},
            {"name": "Limit API Usage", "codename": "limit_api_usage", "description": "Can set API usage limits", "category": "developer"},
            {"name": "Delete API Client", "codename": "delete_api_client", "description": "Can delete API clients", "category": "developer"},
        ]

        # Create permissions (skip if already exists)
        print("\n📝 Processing Permissions...")
        permission_ids = {}
        created_perms = 0
        existing_perms = 0

        for perm_data in default_permissions:
            existing = db.query(Permission).filter(Permission.codename == perm_data["codename"]).first()
            if not existing:
                perm = Permission(**perm_data)
                db.add(perm)
                db.flush()
                permission_ids[perm_data["codename"]] = perm.permission_id
                created_perms += 1
                print(f"  ✅ Created permission: {perm_data['codename']}")
            else:
                permission_ids[perm_data["codename"]] = existing.permission_id
                existing_perms += 1
                print(f"  ⏭️  Skipped (exists): {perm_data['codename']}")

        print(f"\n  📊 Permissions: {created_perms} created, {existing_perms} already exist")

        # ========================================================================
        # GROUP DEFINITIONS
        # ========================================================================
        # Default Groups with their assigned permissions
        default_groups = [
            {
                "name": "User",
                "codename": "user",
                "description": "Regular user with basic permissions",
                "is_system": True,
                "permissions": [
                    # Profile management
                    "view_profile", "edit_profile",
                    # Own activity logs
                    "view_own_activity_log",
                    # Upload files
                    "add_upload", "delete_upload"
                ]
            },
            {
                "name": "Admin",
                "codename": "admin",
                "description": "Administrator with full access",
                "is_system": True,
                "permissions": [perm["codename"] for perm in default_permissions]  # All permissions
            },
            {
                "name": "Moderator",
                "codename": "moderator",
                "description": "Moderator with limited admin access",
                "is_system": True,
                "permissions": [
                    # Profile management
                    "view_profile", "edit_profile", "view_user",
                    # Dashboard access
                    "view_dashboard",
                    # Activity logs (view only, no create/delete)
                    "view_activity_log", "view_own_activity_log", "view_activity_statistics",
                    # System monitoring
                    "view_system_health",
                    # Upload files
                    "add_upload", "delete_upload"
                ]
            },
            {
                "name": "Super Admin",
                "codename": "super_admin",
                "description": "Super administrator with bypass permissions (all access)",
                "is_system": True,
                "permissions": [perm["codename"] for perm in default_permissions]  # All permissions
            },
            {
                "name": "Vendor",
                "codename": "vendor",
                "description": "Vendor with business-related permissions",
                "is_system": True,
                "permissions": [
                    # Profile management
                    "view_profile", "edit_profile",
                    # View other users (for business interactions)
                    "view_user",
                    # Dashboard access (for business analytics)
                    "view_dashboard",
                    # Activity logs (view own and create)
                    "view_own_activity_log", "create_activity_log", "view_activity_statistics",
                    # Upload files (for product images, documents)
                    "add_upload", "delete_upload",
                    # System health (for monitoring)
                    "view_system_health"
                ]
            },
        ]

        # Create groups and assign permissions (skip if already exists)
        print("\n👥 Processing Groups...")
        created_groups = 0
        existing_groups = 0

        for group_data in default_groups:
            permissions = group_data.pop("permissions")
            existing = db.query(Group).filter(Group.codename == group_data["codename"]).first()

            if not existing:
                group = Group(**group_data)
                db.add(group)
                db.flush()

                # Assign permissions to group
                assigned_count = 0
                for perm_codename in permissions:
                    if perm_codename in permission_ids:
                        # Check if permission is already assigned (avoid duplicates)
                        existing_gp = db.query(GroupPermission).filter(
                            GroupPermission.group_id == group.group_id,
                            GroupPermission.permission_id == permission_ids[perm_codename]
                        ).first()

                        if not existing_gp:
                            gp = GroupPermission(
                                group_id=group.group_id,
                                permission_id=permission_ids[perm_codename]
                            )
                            db.add(gp)
                            assigned_count += 1

                db.flush()
                created_groups += 1
                print(f"  ✅ Created group: {group_data['codename']} with {assigned_count} permissions")
            else:
                existing_groups += 1
                print(f"  ⏭️  Skipped (exists): {group_data['codename']}")

        print(f"\n  📊 Groups: {created_groups} created, {existing_groups} already exist")

        db.commit()
        print("\n" + "=" * 80)
        print("✅ Database seeded successfully!")
        print(f"   📝 Permissions: {created_perms} new, {existing_perms} existing")
        print(f"   👥 Groups: {created_groups} new, {existing_groups} existing")
        print("=" * 80)

    except Exception as e:
        db.rollback()
        print(f"❌ Failed to seed database: {e}")
        sys.exit(1)
    finally:
        db.close()


def list_endpoints():
    """
    List all API endpoints with their required permissions.
    Useful for documentation and access control management.
    """
    print("📋 API Endpoints and Permissions Mapping")
    print("=" * 80)

    ENDPOINT_PERMISSIONS = {
        # Authentication Router
        "POST /auth/login-with-password": None,
        "POST /auth/login-with-otp": None,
        "POST /auth/check-user-availability": None,
        "POST /auth/send-one-time-password": None,
        "POST /auth/verify-one-time-password": None,
        "POST /auth/verify": None,
        "POST /auth/forget-password": None,
        "POST /auth/refresh-token": None,
        "POST /auth/set-password": "edit_profile",
        "POST /auth/change-password": "edit_profile",
        "POST /auth/logout": "view_profile",
        "POST /auth/verify-email-and-phone": None,
        "GET /auth/token-info": None,
        "POST /auth/token-info": None,

        # Profile Router
        "GET /settings/profile": "view_profile",
        "GET /settings/profile/{user_id}": "view_user",
        "POST /settings/update-profile-picture": "edit_profile",
        "POST /settings/update-profile": "edit_profile",
        "POST /settings/profile-accessibility": "edit_profile",
        "POST /settings/profile-language": "edit_profile",
        "POST /settings/change-email": "edit_profile",
        "POST /settings/change-phone": "edit_profile",
        "POST /settings/send-phone-otp": "edit_profile",
        "POST /settings/update-theme": "edit_profile",
        "POST /settings/deactivate-account": "edit_profile",
        "POST /settings/delete-account": "edit_profile",
        "GET /settings/get-settings": "view_profile",
        "POST /settings/update-timezone": "edit_profile",

        # Permissions Router
        "GET /permissions": "view_permission",
        "GET /permissions/{permission_id}": "view_permission",
        "POST /permissions": "add_permission",
        "PUT /permissions/{permission_id}": "edit_permission",
        "DELETE /permissions/{permission_id}": "delete_permission",
        "GET /groups": "view_group",
        "GET /groups/{group_id}": "view_group",
        "POST /groups": "add_group",
        "PUT /groups/{group_id}": "edit_group",
        "DELETE /groups/{group_id}": "delete_group",
        "POST /groups/{group_id}/permissions": "edit_group",
        "GET /users/{user_id}/groups": "view_user",
        "GET /users/{user_id}/permissions": "view_user",
        "POST /users/{user_id}/groups": "assign_groups",
        "GET /users/me/groups": "view_profile",
        "GET /users/me/permissions": "view_profile",

        # Dashboard Router
        "GET /dashboard/overview": "view_dashboard",
        "GET /dashboard/users-by-status": "view_dashboard",
        "GET /dashboard/users-by-type": "view_dashboard",
        "GET /dashboard/users-by-auth-type": "view_dashboard",
        "GET /dashboard/users-by-country": "view_dashboard",
        "GET /dashboard/users-by-language": "view_dashboard",
        "GET /dashboard/user-growth": "view_dashboard",
        "GET /dashboard/recent-sign-ins": "view_dashboard",
        "GET /dashboard/all-statistics": "view_dashboard",

        # Activity Router
        "POST /activity/logs": "create_activity_log",
        "GET /activity/logs": "view_activity_log",
        "GET /activity/logs/{log_id}": "view_activity_log",
        "GET /activity/users/{user_id}/logs": "view_activity_log",
        "GET /activity/me/logs": "view_own_activity_log",
        "GET /activity/statistics": "view_activity_statistics",
        "DELETE /activity/logs/cleanup": "delete_activity_log",

        # Upload Router
        "POST /upload-media": "add_upload",
        "DELETE /delete-media": "delete_upload",

        # Health Router
        "GET /health/database": "view_system_health",
        "GET /health/storage": "view_system_health",
        "GET /health/system": None,
        "GET /health/test-sentry": "test_sentry",
    }

    # Group by router
    routers = {
        "Authentication": [],
        "Profile": [],
        "Permissions": [],
        "Dashboard": [],
        "Activity": [],
        "Upload": [],
        "Health": [],
    }

    for endpoint, permission in ENDPOINT_PERMISSIONS.items():
        method_path = endpoint.split(" ", 1)
        method = method_path[0]
        path = method_path[1] if len(method_path) > 1 else ""

        if path.startswith("/auth/"):
            routers["Authentication"].append((method, path, permission))
        elif path.startswith("/settings/"):
            routers["Profile"].append((method, path, permission))
        elif path.startswith("/permissions/") or path.startswith("/groups/") or path.startswith("/users/"):
            routers["Permissions"].append((method, path, permission))
        elif path.startswith("/dashboard/"):
            routers["Dashboard"].append((method, path, permission))
        elif path.startswith("/activity/"):
            routers["Activity"].append((method, path, permission))
        elif path.startswith("/upload") or path.startswith("/delete-media"):
            routers["Upload"].append((method, path, permission))
        elif path.startswith("/health/"):
            routers["Health"].append((method, path, permission))

    # Print organized list
    for router_name, endpoints in routers.items():
        if endpoints:
            print(f"\n📁 {router_name} Router")
            print("-" * 80)
            for method, path, permission in sorted(endpoints):
                perm_display = permission if permission else "PUBLIC"
                perm_color = "🔓" if permission is None else "🔒"
                print(f"  {perm_color} {method:6} {path:50} → {perm_display}")

    # Summary
    total_endpoints = len(ENDPOINT_PERMISSIONS)
    public_endpoints = sum(1 for p in ENDPOINT_PERMISSIONS.values() if p is None)
    protected_endpoints = total_endpoints - public_endpoints

    print("\n" + "=" * 80)
    print("📊 Summary:")
    print(f"   Total Endpoints: {total_endpoints}")
    print(f"   Public Endpoints: {public_endpoints}")
    print(f"   Protected Endpoints: {protected_endpoints}")
    print("=" * 80)


def list_permissions_with_endpoints():
    """
    List all permissions with the endpoints that use each permission.
    Organized by permission, showing which endpoints require it.
    """
    print("📋 Permissions and Their Endpoints")
    print("=" * 80)

    ENDPOINT_PERMISSIONS = {
        # Authentication Router
        "POST /auth/login-with-password": None,
        "POST /auth/login-with-otp": None,
        "POST /auth/check-user-availability": None,
        "POST /auth/send-one-time-password": None,
        "POST /auth/verify-one-time-password": None,
        "POST /auth/verify": None,
        "POST /auth/forget-password": None,
        "POST /auth/refresh-token": None,
        "POST /auth/set-password": "edit_profile",
        "POST /auth/change-password": "edit_profile",
        "POST /auth/logout": "view_profile",
        "POST /auth/verify-email-and-phone": None,
        "GET /auth/token-info": None,
        "POST /auth/token-info": None,

        # Profile Router
        "GET /settings/profile": "view_profile",
        "GET /settings/profile/{user_id}": "view_user",
        "POST /settings/update-profile-picture": "edit_profile",
        "POST /settings/update-profile": "edit_profile",
        "POST /settings/profile-accessibility": "edit_profile",
        "POST /settings/profile-language": "edit_profile",
        "POST /settings/change-email": "edit_profile",
        "POST /settings/change-phone": "edit_profile",
        "POST /settings/send-phone-otp": "edit_profile",
        "POST /settings/update-theme": "edit_profile",
        "POST /settings/deactivate-account": "edit_profile",
        "POST /settings/delete-account": "edit_profile",
        "GET /settings/get-settings": "view_profile",
        "POST /settings/update-timezone": "edit_profile",

        # Permissions Router
        "GET /permissions": "view_permission",
        "GET /permissions/{permission_id}": "view_permission",
        "POST /permissions": "add_permission",
        "PUT /permissions/{permission_id}": "edit_permission",
        "DELETE /permissions/{permission_id}": "delete_permission",
        "GET /groups": "view_group",
        "GET /groups/{group_id}": "view_group",
        "POST /groups": "add_group",
        "PUT /groups/{group_id}": "edit_group",
        "DELETE /groups/{group_id}": "delete_group",
        "POST /groups/{group_id}/permissions": "edit_group",
        "GET /users/{user_id}/groups": "view_user",
        "GET /users/{user_id}/permissions": "view_user",
        "POST /users/{user_id}/groups": "assign_groups",
        "GET /users/me/groups": "view_profile",
        "GET /users/me/permissions": "view_profile",

        # Dashboard Router
        "GET /dashboard/overview": "view_dashboard",
        "GET /dashboard/users-by-status": "view_dashboard",
        "GET /dashboard/users-by-type": "view_dashboard",
        "GET /dashboard/users-by-auth-type": "view_dashboard",
        "GET /dashboard/users-by-country": "view_dashboard",
        "GET /dashboard/users-by-language": "view_dashboard",
        "GET /dashboard/user-growth": "view_dashboard",
        "GET /dashboard/recent-sign-ins": "view_dashboard",
        "GET /dashboard/all-statistics": "view_dashboard",

        # Activity Router
        "POST /activity/logs": "create_activity_log",
        "GET /activity/logs": "view_activity_log",
        "GET /activity/logs/{log_id}": "view_activity_log",
        "GET /activity/users/{user_id}/logs": "view_activity_log",
        "GET /activity/me/logs": "view_own_activity_log",
        "GET /activity/statistics": "view_activity_statistics",
        "DELETE /activity/logs/cleanup": "delete_activity_log",

        # Upload Router
        "POST /upload-media": "add_upload",
        "DELETE /delete-media": "delete_upload",

        # Health Router
        "GET /health/database": "view_system_health",
        "GET /health/storage": "view_system_health",
        "GET /health/system": None,
        "GET /health/test-sentry": "test_sentry",
    }

    # Permission definitions with categories (must match default_permissions in seed function)
    PERMISSIONS = {
        # Profile
        "view_profile": {"name": "View Profile", "category": "profile"},
        "edit_profile": {"name": "Edit Profile", "category": "profile"},
        "view_user": {"name": "View User", "category": "profile"},
        "add_user": {"name": "Add User", "category": "profile"},
        "edit_user": {"name": "Edit User", "category": "profile"},
        "delete_user": {"name": "Delete User", "category": "profile"},
        "suspend_user": {"name": "Suspend User", "category": "profile"},
        "activate_user": {"name": "Activate User", "category": "profile"},
        "reset_user_password": {"name": "Reset User Password", "category": "profile"},
        "force_logout": {"name": "Force Logout User", "category": "profile"},
        # Permissions
        "view_permission": {"name": "View Permission", "category": "permissions"},
        "add_permission": {"name": "Add Permission", "category": "permissions"},
        "edit_permission": {"name": "Edit Permission", "category": "permissions"},
        "delete_permission": {"name": "Delete Permission", "category": "permissions"},
        "assign_permissions": {"name": "Assign Permissions", "category": "permissions"},
        "revoke_permissions": {"name": "Revoke Permissions", "category": "permissions"},
        # Groups
        "view_group": {"name": "View Group", "category": "groups"},
        "add_group": {"name": "Add Group", "category": "groups"},
        "edit_group": {"name": "Edit Group", "category": "groups"},
        "delete_group": {"name": "Delete Group", "category": "groups"},
        "assign_groups": {"name": "Assign Groups", "category": "groups"},
        # Dashboard
        "view_dashboard": {"name": "View Dashboard", "category": "dashboard"},
        # Activity
        "create_activity_log": {"name": "Create Activity Log", "category": "activity"},
        "view_activity_log": {"name": "View Activity Log", "category": "activity"},
        "view_own_activity_log": {"name": "View Own Activity Log", "category": "activity"},
        "view_activity_statistics": {"name": "View Activity Statistics", "category": "activity"},
        "delete_activity_log": {"name": "Delete Activity Log", "category": "activity"},
        "export_activity_log": {"name": "Export Activity Log", "category": "activity"},
        "monitor_user_sessions": {"name": "Monitor User Sessions", "category": "activity"},
        "terminate_user_session": {"name": "Terminate User Session", "category": "activity"},
        # Upload
        "add_upload": {"name": "Add Upload", "category": "upload"},
        "delete_upload": {"name": "Delete Upload", "category": "upload"},
        # System
        "view_system_health": {"name": "View System Health", "category": "system"},
        "test_sentry": {"name": "Test Sentry", "category": "system"},
        # Security
        "view_login_attempts": {"name": "View Login Attempts", "category": "security"},
        "clear_login_attempts": {"name": "Clear Login Attempts", "category": "security"},
        "manage_2fa": {"name": "Manage 2FA", "category": "security"},
        "view_api_keys": {"name": "View API Keys", "category": "security"},
        "generate_api_key": {"name": "Generate API Key", "category": "security"},
        "revoke_api_key": {"name": "Revoke API Key", "category": "security"},
        # Settings
        "view_settings": {"name": "View Settings", "category": "settings"},
        "edit_settings": {"name": "Edit Settings", "category": "settings"},
        # Notifications
        "view_notifications": {"name": "View Notifications", "category": "notifications"},
        "send_notifications": {"name": "Send Notifications", "category": "notifications"},
        "delete_notifications": {"name": "Delete Notifications", "category": "notifications"},
        # Billing
        "view_billing": {"name": "View Billing", "category": "billing"},
        "edit_subscription": {"name": "Edit Subscription", "category": "billing"},
        "refund_payment": {"name": "Refund Payment", "category": "billing"},
        "view_invoices": {"name": "View Invoices", "category": "billing"},
        # Content
        "add_content": {"name": "Add Content", "category": "content"},
        "edit_content": {"name": "Edit Content", "category": "content"},
        "delete_content": {"name": "Delete Content", "category": "content"},
        "publish_content": {"name": "Publish Content", "category": "content"},
        "unpublish_content": {"name": "Unpublish Content", "category": "content"},
        # Developer
        "view_api_usage": {"name": "View API Usage", "category": "developer"},
        "limit_api_usage": {"name": "Limit API Usage", "category": "developer"},
        "delete_api_client": {"name": "Delete API Client", "category": "developer"},
    }

    # Group endpoints by permission
    permission_to_endpoints = {}
    for endpoint, permission in ENDPOINT_PERMISSIONS.items():
        if permission:
            if permission not in permission_to_endpoints:
                permission_to_endpoints[permission] = []
            permission_to_endpoints[permission].append(endpoint)

    # Group by category
    categories = {}
    for perm_codename, perm_info in PERMISSIONS.items():
        category = perm_info["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append({
            "codename": perm_codename,
            "name": perm_info["name"],
            "endpoints": permission_to_endpoints.get(perm_codename, [])
        })

    # Print organized by category
    for category in sorted(categories.keys()):
        print(f"\n📁 {category.upper()} Permissions")
        print("-" * 80)

        for perm in sorted(categories[category], key=lambda x: x["codename"]):
            print(f"\n  🔑 {perm['name']} ({perm['codename']})")
            if perm["endpoints"]:
                for endpoint in sorted(perm["endpoints"]):
                    method, path = endpoint.split(" ", 1)
                    print(f"     {method:6} {path}")
            else:
                print("     ⚠️  No endpoints use this permission")

    # Summary
    total_permissions = len(PERMISSIONS)
    used_permissions = len([p for p in PERMISSIONS.keys() if p in permission_to_endpoints])
    unused_permissions = total_permissions - used_permissions

    print("\n" + "=" * 80)
    print("📊 Summary:")
    print(f"   Total Permissions: {total_permissions}")
    print(f"   Used Permissions: {used_permissions}")
    print(f"   Unused Permissions: {unused_permissions}")
    print("=" * 80)


def pull(output_file: str = None, format: str = "sql"):
    """
    Pull database schema from database.
    Similar to `prisma db pull` - introspects database and generates schema.

    Args:
        output_file: Output file path (default: schema.sql in current directory)
        format: Output format - 'sql' for SQL DDL, 'json' for JSON schema
    """
    print("🔄 Pulling database schema...")

    # Test database connection first
    _test_db_connection()

    from sqlalchemy import create_engine, inspect, text, MetaData
    from sqlalchemy.schema import CreateTable
    import os
    from datetime import datetime

    # Get database connection parameters
    DATABASE_HOST = os.environ.get('DATABASE_HOST')
    DATABASE_NAME = os.environ.get('DATABASE_NAME')
    DATABASE_USER = os.environ.get('DATABASE_USER')
    DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
    DATABASE_PORT = os.environ.get('DATABASE_PORT', '5432')

    # Build connection URL
    DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        inspector = inspect(engine)
        metadata = MetaData()
        metadata.reflect(bind=engine)

        # Get script directory for default output path
        script_dir = os.path.dirname(os.path.abspath(__file__))

        if not output_file:
            if format == "sql":
                output_file = os.path.join(script_dir, "schema.sql")
            else:
                output_file = os.path.join(script_dir, "schema.json")

        # Get all tables
        tables = inspector.get_table_names()

        if not tables:
            print("⚠️  No tables found in database")
            return

        print(f"📋 Found {len(tables)} table(s)")

        if format == "sql":
            # Generate SQL DDL
            sql_statements = []
            sql_statements.append("-- ============================================================================")
            sql_statements.append("-- Database Schema DDL")
            sql_statements.append(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            sql_statements.append(f"-- Database: {DATABASE_NAME}")
            sql_statements.append("-- ============================================================================\n")

            # Get all sequences first
            sequences = []
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT sequence_name, data_type, start_value, minimum_value, maximum_value, increment
                    FROM information_schema.sequences
                    WHERE sequence_schema = 'public'
                    ORDER BY sequence_name;
                """))
                sequences = [dict(row) for row in result]

            if sequences:
                sql_statements.append("-- ============================================================================")
                sql_statements.append("-- SEQUENCES")
                sql_statements.append("-- ============================================================================\n")
                for seq in sequences:
                    sql_statements.append(f"-- Sequence: {seq['sequence_name']}")
                    sql_statements.append(f"-- Type: {seq['data_type']}, Start: {seq['start_value']}, Increment: {seq['increment']}")
                    # Note: Sequences are usually auto-created with SERIAL/BIGSERIAL columns
                    sql_statements.append("")

            # Generate CREATE TABLE statements
            sql_statements.append("-- ============================================================================")
            sql_statements.append("-- TABLES")
            sql_statements.append("-- ============================================================================\n")

            for table_name in sorted(tables):
                table = metadata.tables[table_name]

                # Create table statement
                create_table_sql = str(CreateTable(table).compile(engine))
                sql_statements.append(f"-- Table: {table_name}")
                sql_statements.append(create_table_sql)
                sql_statements.append("")

                # Get indexes for this table
                indexes = inspector.get_indexes(table_name)
                if indexes:
                    sql_statements.append(f"-- Indexes for {table_name}")
                    for idx in indexes:
                        if not idx.get('unique', False):
                            # Regular index
                            cols = ', '.join(idx['column_names'])
                            idx_name = idx['name']
                            sql_statements.append(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name} ({cols});")
                        else:
                            # Unique constraint/index
                            cols = ', '.join(idx['column_names'])
                            idx_name = idx['name']
                            sql_statements.append(f"CREATE UNIQUE INDEX IF NOT EXISTS {idx_name} ON {table_name} ({cols});")
                    sql_statements.append("")

                # Get foreign keys
                foreign_keys = inspector.get_foreign_keys(table_name)
                if foreign_keys:
                    sql_statements.append(f"-- Foreign Keys for {table_name}")
                    for fk in foreign_keys:
                        fk_name = fk['name']
                        constrained_cols = ', '.join(fk['constrained_columns'])
                        referred_table = fk['referred_table']
                        referred_cols = ', '.join(fk['referred_columns'])
                        on_delete = fk.get('ondelete', 'NO ACTION')
                        on_update = fk.get('onupdate', 'NO ACTION')
                        sql_statements.append(
                            f"ALTER TABLE {table_name} "
                            f"ADD CONSTRAINT {fk_name} "
                            f"FOREIGN KEY ({constrained_cols}) "
                            f"REFERENCES {referred_table} ({referred_cols}) "
                            f"ON DELETE {on_delete} ON UPDATE {on_update};"
                        )
                    sql_statements.append("")

            # Get triggers
            sql_statements.append("-- ============================================================================")
            sql_statements.append("-- TRIGGERS")
            sql_statements.append("-- ============================================================================\n")

            with engine.connect() as conn:
                result = conn.execute(text("""
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
                    WHERE tgisinternal = false
                    ORDER BY tgrelid::regclass::text, tgname;
                """))
                triggers = [dict(row) for row in result]

            if triggers:
                for trigger in triggers:
                    sql_statements.append(
                        f"-- Trigger: {trigger['trigger_name']} on {trigger['table_name']} "
                        f"({trigger['timing']} {trigger['event']})"
                    )
                    sql_statements.append(
                        f"-- Function: {trigger['function_name']}"
                    )
                    sql_statements.append("")
            else:
                sql_statements.append("-- No triggers found")
                sql_statements.append("")

            # Get views
            sql_statements.append("-- ============================================================================")
            sql_statements.append("-- VIEWS")
            sql_statements.append("-- ============================================================================\n")

            views = inspector.get_view_names()
            if views:
                for view_name in sorted(views):
                    view_definition = inspector.get_view_definition(view_name)
                    sql_statements.append(f"-- View: {view_name}")
                    sql_statements.append(f"CREATE OR REPLACE VIEW {view_name} AS")
                    sql_statements.append(view_definition)
                    sql_statements.append("")
            else:
                sql_statements.append("-- No views found")
                sql_statements.append("")

            # Write to file
            sql_content = "\n".join(sql_statements)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(sql_content)

            print(f"✅ Schema pulled successfully!")
            print(f"📄 Output file: {output_file}")
            print(f"📊 Summary:")
            print(f"   - Tables: {len(tables)}")
            print(f"   - Sequences: {len(sequences)}")
            print(f"   - Triggers: {len(triggers)}")
            print(f"   - Views: {len(views)}")

        elif format == "json":
            # Generate JSON schema
            import json

            schema_data = {
                "database": DATABASE_NAME,
                "generated_at": datetime.now().isoformat(),
                "tables": []
            }

            for table_name in sorted(tables):
                table = metadata.tables[table_name]
                columns = inspector.get_columns(table_name)
                indexes = inspector.get_indexes(table_name)
                foreign_keys = inspector.get_foreign_keys(table_name)
                primary_keys = inspector.get_pk_constraint(table_name)

                table_info = {
                    "name": table_name,
                    "columns": [],
                    "indexes": [],
                    "foreign_keys": [],
                    "primary_key": primary_keys.get('constrained_columns', []) if primary_keys else []
                }

                # Columns
                for col in columns:
                    col_info = {
                        "name": col['name'],
                        "type": str(col['type']),
                        "nullable": col.get('nullable', True),
                        "default": str(col.get('default', '')) if col.get('default') else None,
                        "autoincrement": col.get('autoincrement', False)
                    }
                    table_info["columns"].append(col_info)

                # Indexes
                for idx in indexes:
                    idx_info = {
                        "name": idx['name'],
                        "columns": idx['column_names'],
                        "unique": idx.get('unique', False)
                    }
                    table_info["indexes"].append(idx_info)

                # Foreign Keys
                for fk in foreign_keys:
                    fk_info = {
                        "name": fk['name'],
                        "columns": fk['constrained_columns'],
                        "referred_table": fk['referred_table'],
                        "referred_columns": fk['referred_columns']
                    }
                    table_info["foreign_keys"].append(fk_info)

                schema_data["tables"].append(table_info)

            # Write JSON file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(schema_data, f, indent=2, default=str)

            print(f"✅ Schema pulled successfully!")
            print(f"📄 Output file: {output_file}")
            print(f"📊 Found {len(tables)} table(s)")

        else:
            print(f"❌ Unknown format: {format}. Use 'sql' or 'json'")
            sys.exit(1)

    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("💡 Install dependencies: pip install sqlalchemy psycopg2-binary")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to pull schema: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def reset():
    """
    Reset database - drop all tables and recreate.
    WARNING: This will delete all data!
    """
    confirm = input("⚠️  This will DELETE ALL DATA. Type 'yes' to confirm: ")
    if confirm.lower() != 'yes':
        print("Cancelled.")
        sys.exit(0)

    print("🔄 Resetting database...")

    from src.db.models.base import drop_db, init_db, engine

    if not engine:
        print("❌ Database connection not configured. Check environment variables.")
        sys.exit(1)

    try:
        drop_db()
        print("  ✅ Tables dropped")

        init_db()
        print("  ✅ Tables recreated")

        print("\n✅ Database reset successfully!")
        print("💡 Run 'python3 db.py seed' to add default data")
    except Exception as e:
        print(f"❌ Failed to reset database: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Database CLI - Similar to Prisma CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 db.py push                    # Push schema to database
    python3 db.py pull                    # Pull schema from database (SQL)
    python3 db.py pull -f json            # Pull schema as JSON
    python3 db.py pull -o custom.sql      # Pull to custom file
    python3 db.py migrate -m "add users"  # Create migration
    python3 db.py upgrade                 # Apply all migrations
    python3 db.py downgrade               # Rollback last migration
    python3 db.py seed                    # Seed with default data
    python3 db.py reset                   # Reset entire database
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Push command
    subparsers.add_parser("push", help="Push schema to database (like prisma db push)")

    # Pull command
    pull_parser = subparsers.add_parser("pull", help="Pull database schema (like prisma db pull)")
    pull_parser.add_argument("-o", "--output", help="Output file path (default: schema.sql)")
    pull_parser.add_argument("-f", "--format", choices=["sql", "json"], default="sql", help="Output format (default: sql)")

    # Migrate command
    migrate_parser = subparsers.add_parser("migrate", help="Create a new migration")
    migrate_parser.add_argument("-m", "--message", help="Migration message")

    # Upgrade command
    upgrade_parser = subparsers.add_parser("upgrade", help="Apply migrations")
    upgrade_parser.add_argument("-r", "--revision", default="head", help="Target revision (default: head)")

    # Downgrade command
    downgrade_parser = subparsers.add_parser("downgrade", help="Rollback migrations")
    downgrade_parser.add_argument("-r", "--revision", default="-1", help="Target revision (default: -1)")

    # History command
    subparsers.add_parser("history", help="Show migration history")

    # Current command
    subparsers.add_parser("current", help="Show current migration status")

    # Seed command
    subparsers.add_parser("seed", help="Seed database with default data")

    # List endpoints command
    subparsers.add_parser("list-endpoints", help="List all API endpoints with their permissions")

    # Reset command
    subparsers.add_parser("reset", help="Reset database (drop and recreate)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Execute command
    if args.command == "push":
        push()
    elif args.command == "pull":
        pull(args.output, args.format)
    elif args.command == "migrate":
        migrate(args.message)
    elif args.command == "upgrade":
        upgrade(args.revision)
    elif args.command == "downgrade":
        downgrade(args.revision)
    elif args.command == "history":
        history()
    elif args.command == "current":
        current()
    elif args.command == "seed":
        seed()
    elif args.command == "list-endpoints":
        list_endpoints()
    elif args.command == "reset":
        reset()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

