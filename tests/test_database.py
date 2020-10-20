""" Tests for database.py """
from pathlib import Path
from random import randint

import pytest

from app import CONTACT_MESSAGE_MAX_LENGTH
from database import ContactDatabase


def empty_sqlite_test_db(db_path) -> ContactDatabase:
    """
    Return empty ContactDatabase at path for testing.

    :param db_path: Path
    :return: ContactDatabase
    """
    # give random db ref to avoid having to drop the tables and recreate each time.
    num = randint(1, 1000000000)
    return ContactDatabase(database_path=Path(db_path, f'test_db{num}'),
                           message_max_length=CONTACT_MESSAGE_MAX_LENGTH)


@pytest.fixture
def empty_sqlite_database(tmpdir) -> ContactDatabase:
    """
    Initialised empty ContactDatabase.
    Basing in tmpdir works where basing in a 'file:' fails on linux,
    and also ensures test atomicity, each test starting with a fresh,
    empty database.

    :param tmpdir: temporary directory path (fixture)
    :return: ContactDatabase
    """
    test_db = empty_sqlite_test_db(tmpdir)
    return test_db


def test_empty_sqlite_database_fixture(empty_sqlite_database):
    """Ensure test db can be connected to and tables exist."""
    assert empty_sqlite_database
    tables = ['person', 'message']
    test_db_tables = empty_sqlite_database._connection().execute(
        """SELECT name from sqlite_master WHERE type='table' """).fetchall()
    for table in tables:
        assert (table,) in test_db_tables

# test db.store_person
# - should store a null alternate_names for a new entry
# should return existing id if existing email with same name
# should return existing id if existing email and add new alternate name if no alternate names
# should return existing id if existing email and add new alternate name to existing alternate names
# should return existing id if existing email and not add existing alternate name to existing alternate names
