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


@pytest.mark.parametrize(
    'stored_contacts, test_email, returned_contact',
    [((), 'some@email.com', None),  # No contacts in db, email not found.
     ([('some contact', 'some@contact.com', None)], 'some@email.com', None),  # Email not found in contacts.
     ([('some contact', 'some@email.com', None)], 'some@email.com',
      (1, 'some contact', None)),  # Contact with no alt names
     ([('some contact', 'some@email.com', 'some, alt, names')
       ], 'some@email.com',
      (1, 'some contact', 'some, alt, names')),  # Contact with alt names
     ([('any contact', 'any@email.com', None),
       ('some contact', 'some@email.com', 'some, alt, names'),
       ('other contact', 'other@email.com', 'some, other, alt, names'),
       ], 'some@email.com',
      (2, 'some contact', 'some, alt, names')),  # Multiple contacts.
     ])
def test_get_person_from_email(empty_sqlite_database,
                               stored_contacts, test_email, returned_contact):
    test_db = empty_sqlite_database
    for stored_contact in stored_contacts:
        conn = test_db._connection()
        conn.cursor().execute(
            """INSERT INTO person(name, email, alternate_names)
               VALUES(?,?,?);
               """, (*stored_contact,))
        conn.commit()

    assert test_db.get_person_from_email(test_db._connection(),
                                         test_email) == returned_contact


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


def test_store_message_text(empty_sqlite_database):
    test_db = empty_sqlite_database
    test_contact_id = test_db.store_person('test subject', 'test@subject.com')
    test_message = 'some arbitrary message'

    message_id = test_db.store_message_text(test_contact_id, test_message)

    assert test_db._connection().cursor().execute(
        """SELECT * 
           FROM message
           WHERE id=?
           """, (message_id,)).fetchone() == (message_id, test_contact_id, test_message,
                                              False, False)  # Email, SMS not sent.


def test_store_contact(empty_sqlite_database):
    test_db = empty_sqlite_database

    test_name = 'name'
    test_email = 'name@email.com'
    test_contact_id = 17
    test_message_text = 'some message'
    test_message_id = 34

    called = {'mocked_store_person': False,
              'mocked_store_message_text': False}

    def mocked_store_person(name, email):
        """Mock db.store_person"""
        called['mocked_store_person'] = True
        assert (name, email) == (test_name, test_email)
        return test_contact_id

    def mocked_store_message_test(person_id, message):
        """Mock db.store_message_test"""
        called['mocked_store_message_text'] = True
        assert (person_id, message) == (test_contact_id, test_message_text)
        return test_message_id

    test_db.store_person = mocked_store_person
    test_db.store_message_text = mocked_store_message_test

    assert test_db.store_contact(test_name,
                                 test_email,
                                 test_message_text) == test_message_id
    assert all([called[mock] for mock in called])
