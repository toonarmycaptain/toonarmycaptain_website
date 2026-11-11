"""Universal fixtures"""

from tests.test_app_fixture import test_app, test_client
from tests.test_database import empty_sqlite_database

__all__ = ["empty_sqlite_database", "test_app", "test_client"]
