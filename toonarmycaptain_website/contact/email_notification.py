"""Send notification via email."""

import json
import logging

# import smtplib
# from email.message import EmailMessage
from threading import Thread
from urllib import request

from flask import Flask

logger = logging.getLogger(__name__)

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_TIMEOUT = 10  # seconds, per socket operation


def send_contact_email(
    app: Flask,
    message_id: int,
    contact_email: str,
    contact_name: str,
    message_body: str,
) -> None:
    """
    Forward contact via email, from server address to contact address.

    Sent via the mailer (config MAILER_URL/MAILER_KEY).
    On success, marks the message email_sent=True.

    Message is stored, failed send is logged and email_sent is not updated to True.

    :param app: Flask
    :param message_id: int
    :param contact_email: str
    :param contact_name: str
    :param message_body: str
    :return: None
    """
    DATABASE = app.config["DATABASE"]
    # from_address = app.config["SERVER_EMAIL_ADDRESS"]
    # to_address = app.config["CONTACT_EMAIL_ADDRESS"]
    email_subject, email_body = compose_notification_email(
        contact_email, contact_name, message_body
    )

    # message = EmailMessage()
    # message["From"] = from_address
    # message["To"] = to_address
    # message["Subject"] = email_subject
    # message["Reply-To"] = contact_email
    # message.set_content(email_body)
    #
    try:
        # with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT) as smtp:
        #     smtp.starttls()
        #     smtp.login(from_address, app.config["SMTP_APP_PASSWORD"])
        #     smtp.send_message(message)
        # DATABASE.email_sent(message_id)
        # logger.info(f"Contact email sent for message {message_id}")
        with request.urlopen(
            request.Request(
                app.config["MAILER_URL"],
                data=json.dumps(
                    {
                        "site": "toonarmycaptain.com",
                        "subject": email_subject,
                        "text": email_body,
                        "reply_to": contact_email,
                    }
                ).encode(),
                method="POST",
                headers={
                    "Authorization": f"Bearer {app.config['MAILER_KEY']}",
                    "Content-Type": "application/json",
                    # the default Python-urllib agent can be blocked
                    "User-Agent": "toonarmycaptain-website contact form",
                },
            ),
            timeout=10,  # seconds
        ) as response:
            mailer_id = json.load(response)["messageId"]
        DATABASE.email_sent(message_id)
        logger.info(
            f"Contact email sent for message {message_id} (mailer id {mailer_id})"
        )
    except Exception:
        logger.exception(f"Contact email send failed for message {message_id}")
        # notify of error (eg with login), using sms


def send_contact_email_async(
    app: Flask,
    message_id: int,
    contact_email: str,
    contact_name: str,
    message_body: str,
) -> None:
    """
    Dispatch send_contact_email on a background thread so the request doesn't
    block on the SMTP round-trip. Pass the real app object (not the current_app
    proxy, which is unbound outside the request thread).

    :param app: Flask
    :param message_id: int
    :param contact_email: str
    :param contact_name: str
    :param message_body: str
    :return: None
    """
    Thread(
        target=send_contact_email,
        args=(app, message_id, contact_email, contact_name, message_body),
        daemon=True,
    ).start()


def compose_notification_email(
    contact_email: str, contact_name: str, message_body: str
) -> tuple[str, str]:
    """
    Compose notification email.

    :param contact_email: str - address of person submitting contact form
    :param contact_name: str
    :param message_body: str
    :return: EmailMessage
    """
    email_subject = f"Contact from {contact_name}"
    email_body = (
        f"{message_body}\n"
        f"\n"
        f"from {contact_name}\n"  # Option here to add ' a.k.a. {alternate_names}'
        f"{contact_email}"
    )

    return email_subject, email_body
