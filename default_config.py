"""Default application settings, to be overridden at runtime."""
SECRET_KEY: bytes = b'some secret key'

CONTACT_MESSAGE_MAX_LENGTH: int = 10000  # characters

SERVER_EMAIL_ADDRESS: str = 'some email to send contact emails from'
SERVER_EMAIL_PASSWORD: str = 'some good password'
CONTACT_EMAIL_ADDRESS: str = 'where to sent contact emails to'


CONTACT_CELL_NUMBER: str = 'some number'
