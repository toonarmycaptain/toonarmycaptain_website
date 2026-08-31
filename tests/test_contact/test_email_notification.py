""" Test email_notification.py """
import smtplib

import pytest

from flask import Flask

from toonarmycaptain_website.contact import email_notification
from toonarmycaptain_website.contact.email_notification import (send_contact_email, compose_notification_email,
                                                                )

@pytest.mark.parametrize('exception_thrown', [False, True])
def test_send_contact_email(monkeypatch, test_client,
                            exception_thrown):
    """Email is sent via Gmail SMTP with correct metadata and logged in db."""

    mock_from_address = 'mock@from.address'
    mock_to_address = 'mock@to.address'
    mock_app_password = 'mock app password'

    test_message_id = 314
    test_contact_email = 'contact@host.tld'
    test_contact_name = 'Sir Lancelot'
    test_message_body = 'Some amusing message.'
    mock_email_subject = 'Contact from Sir Lancelot'

    mock_call = {
        'mock_compose_notification_email': False,
        'smtp.starttls': False,
        'smtp.login': False,
        'smtp.send_message': False,
        'app.DATABASE.email_sent': False,
    }

    def mock_compose_notification_email(contact_email, contact_name, message_body):
        mock_call['mock_compose_notification_email'] = True
        assert (contact_email, contact_name, message_body) == (
            test_contact_email, test_contact_name, test_message_body)
        return mock_email_subject, test_message_body

    class MockSMTP:
        def __init__(self, host, port):
            assert (host, port) == (email_notification.SMTP_HOST, email_notification.SMTP_PORT)

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def starttls(self):
            mock_call['smtp.starttls'] = True

        def login(self, user, password):
            mock_call['smtp.login'] = True
            assert (user, password) == (mock_from_address, mock_app_password)

        def send_message(self, message):
            mock_call['smtp.send_message'] = True
            if exception_thrown:
                raise smtplib.SMTPException
            # Don't test body, as is subject to change.
            assert (message['From'], message['To'], message['Subject']) == (
                mock_from_address, mock_to_address, mock_email_subject)

    class MockDatabase:
        def email_sent(self, message_id):
            mock_call['app.DATABASE.email_sent'] = True
            assert message_id == test_message_id

    class MockApp(Flask):
        def __init__(self):
            self.config = {'SERVER_EMAIL_ADDRESS': mock_from_address,
                           'CONTACT_EMAIL_ADDRESS': mock_to_address,
                           'SMTP_APP_PASSWORD': mock_app_password,
                           'DATABASE': MockDatabase(),
                           }

    monkeypatch.setattr(email_notification.smtplib, 'SMTP', MockSMTP)
    monkeypatch.setattr(email_notification, 'compose_notification_email', mock_compose_notification_email)

    assert send_contact_email(app=MockApp(),
                              message_id=test_message_id,
                              contact_email=test_contact_email,
                              contact_name=test_contact_name,
                              message_body=test_message_body,
                              ) is None

    if exception_thrown:
        assert mock_call['smtp.send_message'] is True
        assert mock_call['app.DATABASE.email_sent'] is False
    else:
        assert all(mock_call.values())


def test_compose_notification_email():
    """EmailMessage composed with correct metadata."""
    test_contact_email = 'contact@host.tld'
    test_contact_name = 'Sir Lancelot'
    test_message_body = 'Some amusing message.'

    test_email_subject, test_email_body = compose_notification_email(test_contact_email, test_contact_name,
                                                                     test_message_body)

    assert test_email_subject == f'Contact from {test_contact_name}'
    assert test_email_body == (f'{test_message_body}\n'
                               f'\n'
                               f'from {test_contact_name}\n'
                               f'{test_contact_email}'
                               )
