"""Default application settings, to be overridden at runtime."""
from pathlib import Path

SECRET_KEY: bytes = b'some secret key'

CONTACT_DATABASE_PATH = Path('some_instance.db')
CONTACT_MESSAGE_MAX_LENGTH: int = 10000  # characters

SERVER_EMAIL_ADDRESS: str = 'some email to send contact emails from'
CONTACT_EMAIL_ADDRESS: str = 'where to send contact emails to'

TURNSTILE_SITE_KEY: str = 'turnstile-site-key'       # public - rendered in the page
TURNSTILE_SECRET_KEY: str = 'turnstile-secret-key'   # private - server-side verification

CONTACT_CELL_NUMBER: str = 'some number'

BLOG_URL: str = 'https://some.blog.url'
