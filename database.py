""" Contact form submission database. """

import sqlite3

from pathlib import Path


class ContactDatabase:
    """
    ContactDatabase object.

    Hold contact form submissions.

    Schema:
        Table: `person`
            key `id` - INTEGER primary key
            key `name` TEXT <= 255 chars
            key `email` TEXT <= 255 chars

        Table: `message`
            key `id` - INTEGER primary key
            key `person_id` - TEXT <= 255 chars ie person.id
            key `contents` - TEXT <= max_message_length

    """

    def __init__(self,
                 database_path: Path,
                 message_max_length: int,
                 ):
        """
        :param database_path: Path
        :param message_max_length: int
        """

        self.database_path: Path = (database_path
                                    or Path(Path.cwd(), 'contact.db'))
        self._message_max_length: int = message_max_length
        # check if db file exists/db has appropriate tables etc
        self._init_db()

    def _connection(self) -> sqlite3.Connection:
        """
        Return connection to database.

        Execute command enforcing foreign key support in SQLite.
        :return: sqlite3.Connection
        """
        connection = sqlite3.connect(self.database_path)
        # Ensure foreign key constraint enforcement.
        connection.cursor().execute("""PRAGMA foreign_keys=ON;""")
        # print("Connection to SQLite DB successful")
        return connection
        # handle case where connection fails?
        # or should it fail, since on disk db connection should not fail?

    def _init_db(self):
        """
        Create empty database.
        Function could have better name.
        :return: None
        """

        with self._connection() as conn:
            conn.cursor().execute(
                """CREATE TABLE IF NOT EXISTS person(
                         -- primary key must be INTEGER not INT, NOT NULL is implicit.
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         name TEXT NOT NULL CHECK(typeof("name") = 'text' AND
                                                  length("name") <= 255
                                                  ),
                         email TEXT NOT NULL CHECK(typeof("name") = 'text' AND
                                                   length("name") <= 255
                                                   )
                         );
                         """)
            conn.cursor().execute(
                f"""CREATE TABLE IF NOT EXISTS message(
                         -- primary key must be INTEGER not INT, NOT NULL is implicit.
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         person_id INTEGER NOT NULL,
                         contents TEXT NOT NULL CHECK(typeof("contents") = 'text' AND
                                                      length("contents") <= ?
                                                      ),
                         FOREIGN KEY (person_id) REFERENCES person(id)
                         );
                         """,
                (self._message_max_length,))
        conn.commit()
        conn.close()
