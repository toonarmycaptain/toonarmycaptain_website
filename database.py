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
            key 'alternate_names' TEXT <= 510 chars # comma sep str of alt names.

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
        Create empty database, create missing tables.

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
                         email TEXT UNIQUE NOT NULL CHECK(typeof("name") = 'text' AND
                                                          length("name") <= 255
                                                          ),
                         alternate_names TEXT CHECK(typeof("name") = 'text' AND
                                                    length("name") <= 510 
                                                    )                                                   
                         );
                         """)
            conn.cursor().execute(
                f"""CREATE TABLE IF NOT EXISTS message(
                         -- primary key must be INTEGER not INT, NOT NULL is implicit.
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         person_id INTEGER NOT NULL,
                         contents TEXT NOT NULL CHECK(typeof("contents") = 'text' AND
                                                      length("contents") <= {self._message_max_length}
                                                      ),
                         email_sent BOOLEAN NOT NULL CHECK (email_sent IN (0,1)) DEFAULT FALSE, -- Stored as 1/0.
                         sms_sent BOOLEAN NOT NULL CHECK (email_sent IN (0,1)) DEFAULT FALSE, -- Stored as 1/0.
                         FOREIGN KEY (person_id) REFERENCES person(id)
                         );
                         """)
        conn.commit()
        conn.close()

    def store_person(self, name: str, email: str) -> int:
        """
        Store contact details in database.

        If nonexistent based on email, add contact.
        If existent email, new name, add alternate name to
        alternate_names column.

        NB alternate_names column might have spurious commas if user submits
        data containing commas.

        :param name: str
        :param email: str
        :return: int person.id
        """
        with self._connection() as conn:
            cursor = conn.cursor()
            # Check if email already in db:
            existing_record = cursor.execute(
                """SELECT person.id, person.name, person.alternate_names
                   FROM person
                   WHERE email=?
                   LIMIT 1;
                   """, (email,)).fetchone()
            if existing_record:  # Update with any new data:
                person_id, person_name, alternate_names = existing_record

                if name != person_name and (not alternate_names  # Avoid str comparison to None.
                                            or name not in alternate_names):
                    alternate_names = name if not alternate_names else f'{alternate_names}, ' + name
                    cursor.execute(
                        """UPDATE person
                           SET alternate_names=?
                           WHERE person.id=?;
                           """, (alternate_names, person_id,))

            else:  # Create new record:
                cursor.execute(
                    """INSERT INTO person(name, email)
                       VALUES(?,?);
                       """, (name, email))
                person_id = cursor.lastrowid
        conn.commit()
        return person_id

    def store_message_text(self, person_id: int, message_text: str) -> int:
        """
        Store message text in database, return id of message.

        :param person_id: int
        :param message_text: str
        :return: int: message.id
        """
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO message(person_id, contents)
                   VALUES(?,?)
                   """, (person_id, message_text))
            message_id = cursor.lastrowid
        conn.commit()
        return message_id

    def store_contact(self, name: str, email: str, message: str) -> int:
        """

        :param name: str
        :param email: str
        :param message: str
        :return: int
        """
        person_id = self.store_person(name, email)
        message_id = self.store_message_text(person_id, message)
        return message_id
