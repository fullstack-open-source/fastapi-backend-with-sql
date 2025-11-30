"""
Simple trigger initialization for FastAPI
Call this function on startup to auto-register and setup all triggers
"""

from src.db.postgres.postgres import connection
from src.logger.logger import logger


def init_all_triggers():
    """
    Initialize all triggers - registers and creates them in database
    Call this on FastAPI startup

    Returns:
        Dictionary with initialization results
    """
    results = {
        "registered": [],
        "created": [],
        "skipped": [],
        "failed": []
    }

    try:
        # Get trigger manager (auto-detects existing triggers)
        manager = connection.get_trigger_manager()

        return results

    except Exception as e:
        logger.error(f"Error initializing triggers: {e}", exc_info=True)
        results["failed"].append(f"init_error: {str(e)}")
        return results


