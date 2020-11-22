""" Send notification via email."""
import ssl
import smtplib

from email.message import EmailMessage
from flask import Flask


def send_contact_email(app: Flask,
                       message_id: int,
                       contact_email: str, contact_name: str, message_body: str) -> None:
    """
    Forward contact via email, from server address to contact address.

    Then update message db entry with email_sent=True.

    :param app: Flask
    :param message_id: int
    :param contact_email: str
    :param contact_name: str
    :param message_body: str
    :return: None
    """
    host_url = app.config['EMAIL_SERVER_HOST_URL']
    ssl_port = app.config['SSL_PORT']  # For SSL.
    from_address = app.config['SERVER_EMAIL_ADDRESS']
    to_address = app.config['CONTACT_EMAIL_ADDRESS']
    password = app.config['SERVER_EMAIL_PASSWORD']

    # Create a secure SSL context
    context = ssl.create_default_context()

    email_msg = compose_notification_email(from_address, to_address,
                                           contact_email, contact_name, message_body)

    with smtplib.SMTP_SSL(host_url, ssl_port, context=context) as server:
        server.login(from_address, password)
        server.send_message(from_addr=from_address,
                            to_addrs=to_address,
                            msg=email_msg)
    app.DATABASE.email_sent(message_id)


def compose_notification_email(from_address: str, to_address: str,
                               contact_email: str, contact_name: str, message_body: str
                               ) -> EmailMessage:
    """
    Compose notification email.

    :param from_address: str - notification sent from address
    :param to_address: str - notification sent to address
    :param contact_email: str - address of person submitting contact form
    :param contact_name: str
    :param message_body: str
    :return: EmailMessage
    """
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

    return email_msg
