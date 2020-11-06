""" Tests for database.py """
from pathlib import Path
from random import randint

import pytest

from toonarmycaptain_website.database import ContactDatabase

TESTING_CONTACT_MESSAGE_MAX_LENGTH = 10000


def empty_sqlite_test_db(db_path) -> ContactDatabase:
    """
    Return empty ContactDatabase at path for testing.

    :param db_path: Path
    :return: ContactDatabase
    """
    # give random db ref to avoid having to drop the tables and recreate each time.
    num = randint(1, 1000000000)
    return ContactDatabase(database_path=Path(db_path, f'test_db{num}'),
                           message_max_length=TESTING_CONTACT_MESSAGE_MAX_LENGTH)


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


def test_get_person_from_email(empty_sqlite_database):
    pass


@pytest.mark.parametrize(
    'new_contact, existing_person, returned_id, resulting_person_row',
    [(('new contact', 'new@contact.com'), None,  # Brand new entry
      1, ('new contact', 'new@contact.com', None)),  # NB null alt name.
     # Existing email with same name.
     (('new contact', 'new@contact.com'), ('new contact', 'new@contact.com', None),
      1, ('new contact', 'new@contact.com', None)),
     # Existing email, different name, no initial alt names.
     (('new name', 'new@contact.com'), ('new contact', 'new@contact.com', None),
      1, ('new contact', 'new@contact.com', 'new name')),  # NB New alt name.
     # Existing email, existing alt name.
     (('new contact', 'new@contact.com'), ('new contact', 'new@contact.com', 'new name'),
      1, ('new contact', 'new@contact.com', 'new name')),  # NB New alt name.
     # Existing email, alt name, existing alt name.
     (('new name', 'new@contact.com'), ('new contact', 'new@contact.com', 'new name'),
      1, ('new contact', 'new@contact.com', 'new name')),  # NB No new alt name added.
     # Existing email, orig name, existing alt name.
     (('new contact', 'new@contact.com'), ('new contact', 'new@contact.com', 'new name'),
      1, ('new contact', 'new@contact.com', 'new name')),  # NB No new alt name added.
     # Existing email, 1st alt name, existing alt names.
     (('new name1', 'new@contact.com'), ('new contact', 'new@contact.com', 'new name1, new name2'),
      1, ('new contact', 'new@contact.com', 'new name1, new name2')),  # NB No new alt name added.
     # Existing email, 2nd alt name, existing alt names.
     (('new name2', 'new@contact.com'), ('new contact', 'new@contact.com', 'new name1'),
      1, ('new contact', 'new@contact.com', 'new name1, new name2')),  # NB No new alt name added.
     # Existing email, new name, existing alt names.
     (('new name3', 'new@contact.com'), ('new contact', 'new@contact.com', 'new name1, new name2'),
      1, ('new contact', 'new@contact.com', 'new name1, new name2, new name3')),  # NB New alt name.
     # New contact where there is existing.
     (('new contact', 'new@contact.com'), ('other contact', 'exists@contact.com', "whatever alt names"),
      2, ('new contact', 'new@contact.com', None)),  # New contact added.
     ])
def test_store_person(empty_sqlite_database,
                      new_contact, existing_person,
                      returned_id, resulting_person_row):
    test_db = empty_sqlite_database
    if existing_person:
        conn = test_db._connection()
        conn.cursor().execute(
            """INSERT INTO person(name, email, alternate_names)
               VALUES(?,?,?);
               """, (*existing_person,))
        conn.commit()

    assert test_db.store_person(*new_contact) == returned_id

    assert test_db._connection().cursor().execute(
        """SELECT * 
           FROM person
           WHERE id=?""", (returned_id,)).fetchone() == (returned_id, *resulting_person_row)
