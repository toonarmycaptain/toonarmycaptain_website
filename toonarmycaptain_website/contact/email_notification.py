""" Send notification via email."""
import ssl
import smtplib

from email.message import EmailMessage
from flask import current_app as app

"""NB Keep actual account data secret, do not commit to github."""

port = 465  # For SSL.
from_address = app.config['SERVER_EMAIL_ADDRESS']
to_address = app.config['CONTACT_EMAIL_ADDRESS']
password = app.config['SERVER_EMAIL_PASSWORD']


def send_contact_email(message_id: int, contact_email: str, contact_name: str, message_body: str):
    """
    Forward contact via email, from server address to contact address.

    Then update message db entry with email_sent=True.

    :param message_id: int
    :param contact_email: str
    :param contact_name: str
    :param message_body: str
    :return: None
    """
    # Create a secure SSL context
    context = ssl.create_default_context()

    email_msg = EmailMessage()
    email_msg['Subject'] = f'Contact from {contact_name}'
    email_msg['From'] = from_address
    email_msg['To'] = to_address
    message_body = (f'{message_body}\n'
                    f'\n'
                    f'from {contact_name}\n'  # Option here to add ' a.k.a. {alternate_names}'
                    f'{contact_email}'
                    )
    email_msg.set_content(message_body)

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(from_address, password)
        server.send_message(from_addr=from_address,
                            to_addrs=to_address,
                            msg=email_msg)
    app.DATABASE.email_sent(message_id)
