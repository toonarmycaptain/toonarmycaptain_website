""" Send notification via email."""
import ssl
import smtplib

from email.message import EmailMessage
from flask import current_app as app

"""NB Keep actual account data secret, do not commit to github."""

SSL_PORT = 465  # For SSL.
FROM_ADDRESS = app.config['SERVER_EMAIL_ADDRESS']
TO_ADDRESS = app.config['CONTACT_EMAIL_ADDRESS']
PASSWORD = app.config['SERVER_EMAIL_PASSWORD']


def send_contact_email(message_id: int, contact_email: str, contact_name: str, message_body: str) -> None:
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

    email_msg = compose_notification_email(contact_email, contact_name, message_body)

    with smtplib.SMTP_SSL("smtp.gmail.com", SSL_PORT, context=context) as server:
        server.login(FROM_ADDRESS, PASSWORD)
        server.send_message(from_addr=FROM_ADDRESS,
                            to_addrs=TO_ADDRESS,
                            msg=email_msg)
    app.DATABASE.email_sent(message_id)


def compose_notification_email(contact_email: str, contact_name: str, message_body: str) -> EmailMessage:
    """
    Compose notification email.

    :param contact_email: str
    :param contact_name: str
    :param message_body: str
    :return: EmailMessage
    """
    email_msg = EmailMessage()
    email_msg['Subject'] = f'Contact from {contact_name}'
    email_msg['From'] = FROM_ADDRESS
    email_msg['To'] = TO_ADDRESS

    message_body = (f'{message_body}\n'
                    f'\n'
                    f'from {contact_name}\n'  # Option here to add ' a.k.a. {alternate_names}'
                    f'{contact_email}'
                    )
    email_msg.set_content(message_body)

    return email_msg
