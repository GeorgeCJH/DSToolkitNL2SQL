import sys
import asyncio

# Fix for Windows psycopg async compatibility - CRITICAL: must be set before any imports
if sys.platform == "win32":
    try:
        # Force set the event loop policy immediately
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        print(f"Set event loop policy to WindowsSelectorEventLoopPolicy for Windows")
    except Exception as e:
        print(f"Warning: Could not set event loop policy: {e}")

from .nl2sql_run import AutoGenText2SqlRunner
from .autogen_nl2sql.autogen_text_2_sql import UserMessagePayload, AutoGenText2Sql

__all__ = ["AutoGenText2SqlRunner", "UserMessagePayload", "AutoGenText2Sql"]