""" Test email_notification.py """
import ssl

from flask import Flask

from toonarmycaptain_website.contact import email_notification
from toonarmycaptain_website.contact.email_notification import (send_contact_email,
                                                                compose_notification_email,
                                                                )


def test_send_contact_email(monkeypatch, test_client):
    mock_host_url = 42
    mock_ssl_port = 'some.server'
    mock_from_address = 'mock@from.address'
    mock_password = 'mock_password'
    mock_to_address = 'mock@to.address'

    test_message_id = 314
    test_contact_email = 'contact@host.tld'
    test_contact_name = 'Sir Lancelot'
    test_message_body = 'Some amusing message.'

    mock_email = 'some email message'

    mock_call = {
        'mock_compose_notification_email': False,
        'app.login': False,
        'app.send_message': False,
        'app.DATABASE.email_sent': False,
    }

    def mock_compose_notification_email(from_address, to_address,
                                        contact_email, contact_name, message_body):
        mock_call['mock_compose_notification_email'] = True
        assert (from_address, to_address) == (mock_from_address, mock_to_address)
        assert (contact_email, contact_name, message_body) == (
            test_contact_email, test_contact_name, test_message_body)
        return mock_email

    class MockSMTP_SSL:
        def __init__(self, host_url, ssl_port, context):
            assert (host_url, ssl_port) == (mock_host_url, mock_ssl_port)
            assert isinstance(context, ssl.SSLContext)

        def login(self, from_address, password):
            mock_call['app.login'] = True
            assert (from_address, password) == (mock_from_address, mock_password)

        def send_message(self, from_addr, to_addrs, msg):
            mock_call['app.send_message'] = True
            assert (from_addr, to_addrs, msg) == (
                mock_from_address, mock_to_address, mock_email)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            """End context"""

    class MockDatabase:
        def email_sent(self, message_id):
            mock_call['app.DATABASE.email_sent'] = True
            assert message_id == test_message_id

    class MockApp(Flask):
        def __init__(self):
            self.config = {'EMAIL_SERVER_HOST_URL': mock_host_url,
                           'SSL_PORT': mock_ssl_port,
                           'SERVER_EMAIL_ADDRESS': mock_from_address,
                           'SERVER_EMAIL_PASSWORD': mock_password,
                           'CONTACT_EMAIL_ADDRESS': mock_to_address,
                           }
            self.DATABASE = MockDatabase()

    monkeypatch.setattr(email_notification.smtplib, 'SMTP_SSL', MockSMTP_SSL)
    monkeypatch.setattr(email_notification, 'compose_notification_email', mock_compose_notification_email)

    assert send_contact_email(app=MockApp(),
                              message_id=test_message_id,
                              contact_email=test_contact_email,
                              contact_name=test_contact_name,
                              message_body=test_message_body,
                              ) is None

    assert all([call for call in mock_call])


def test_compose_notification_email():
    test_from_address = 'test@from.address'
    test_to_address = 'test@to.address'
    test_message_id = 314
    test_contact_email = 'contact@host.tld'
    test_contact_name = 'Sir Lancelot'
    test_message_body = 'Some amusing message.'

    test_message = compose_notification_email(test_from_address, test_to_address,
                                              test_contact_email, test_contact_name, test_message_body)

    assert test_message['Subject'] == f'Contact from {test_contact_name}'
    assert test_message['From'] == test_from_address
    assert test_message['To'] == test_to_address
    assert test_message.get_content() == (f'{test_message_body}\n'
                                          f'\n'
                                          f'from {test_contact_name}\n'
                                          f'{test_contact_email}'
                                          f'\n'  # Function will add trailing newline.
                                          )
