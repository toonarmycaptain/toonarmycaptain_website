""" Send notification via email."""
from typing import Tuple
import ezgmail

from flask import Flask


def send_contact_email(app: Flask,
                       message_id: int,
                       contact_email: str, contact_name: str, message_body: str) -> None:
    """
    Forward contact via email, from server address to contact address.

    NB EZGmail requires pre-setup with a credentials.json and token.json, and
    previously run ezgmail.init(), which must be obtained on a personal machine,
    as PythonAnywhere's server does not permit operations needed to
    authenticate. These credentials are obtained from
    https://console.cloud.google.com/apis/dashboard and a Desktop application
    type credential must be selected (since the auth is being done on a personal
    machine). The credentials must be placed in the top folder, with
    README.md/requirements.txt etc.

    Then update message db entry with email_sent=True.

    :param app: Flask
    :param message_id: int
    :param contact_email: str
    :param contact_name: str
    :param message_body: str
    :return: None
    """

    to_address = app.config['CONTACT_EMAIL_ADDRESS']
    email_subject, email_body = compose_notification_email(contact_email,
                                                           contact_name,
                                                           message_body)

    try:
        assert ezgmail.EMAIL_ADDRESS == app.config['SERVER_EMAIL_ADDRESS']
        print(f"{ezgmail.EMAIL_ADDRESS == app.config['SERVER_EMAIL_ADDRESS']=}")
        ezgmail.send(recipient=to_address, subject=email_subject, body=email_body)
        app.DATABASE.email_sent(message_id)
    except Exception as e:
        print(e)
        # notify of error (eg with login), using sms


def compose_notification_email(contact_email: str, contact_name: str, message_body: str
                               ) -> Tuple[str, str]:
    """
    Compose notification email.

    :param contact_email: str - address of person submitting contact form
    :param contact_name: str
    :param message_body: str
    :return: EmailMessage
    """
    email_subject = f'Contact from {contact_name}'
    email_body = (f'{message_body}\n'
                  f'\n'
                  f'from {contact_name}\n'  # Option here to add ' a.k.a. {alternate_names}'
                  f'{contact_email}'
                  )

    return email_subject, email_body
