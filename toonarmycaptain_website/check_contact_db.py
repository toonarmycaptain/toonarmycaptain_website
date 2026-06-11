from pathlib import Path

try:
    from database import ContactDatabase  # ty: ignore[unresolved-import]
except ImportError:
    from toonarmycaptain_website.database import ContactDatabase

db = ContactDatabase(database_path=Path('contact.db'), message_max_length=50000)

with db._connection() as conn:

    for table in ['message', 'person']:
        data =  conn.cursor().execute(f"""SELECT * FROM {table}""").fetchall()
        print(f'\n\n{table}')
        for row in data: print(row)
