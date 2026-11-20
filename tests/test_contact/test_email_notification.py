"""Test email_notification.py"""

import json
from io import BytesIO
from urllib.error import HTTPError, URLError

import pytest
from flask import Flask

from toonarmycaptain_website.contact import email_notification
from toonarmycaptain_website.contact.email_notification import (
    compose_notification_email,
    send_contact_email,
)


@pytest.mark.parametrize(
    ("mailer_reply", "email_sent"),
    [
        (b'{"messageId": "m-123"}', True),
        # mailer refuses the request, eg wrong key
        (
            HTTPError("https://mailer.example/send", 401, "Unauthorized", None, None),
            False,
        ),
        (URLError("timed out"), False),
        # a reply without a message id isn't taken as sent
        (b'{"error": "some error"}', False),
    ],
)
def test_send_contact_email(monkeypatch, test_client, mailer_reply, email_sent):
    """
    Email is POSTed to the mailer with correct metadata, and logged in db only
    if the mailer replies with a message id.
    """

    mock_mailer_url = "https://mailer.example/send"
    mock_mailer_key = "mock mailer key"

    test_message_id = 314
    test_contact_email = "contact@host.tld"
    test_contact_name = "Sir Lancelot"
    test_message_body = "Some amusing message."
    mock_email_subject = "Contact from Sir Lancelot"

    def mock_compose_notification_email(contact_email, contact_name, message_body):
        assert (contact_email, contact_name, message_body) == (
            test_contact_email,
            test_contact_name,
            test_message_body,
        )
        return mock_email_subject, test_message_body

    # Recorded rather than asserted in the mocks: send_contact_email swallows exceptions.
    mailer_requests = []
    emailed_message_ids = []

    def mock_urlopen(mailer_request, timeout):
        mailer_requests.append(mailer_request)
        if isinstance(mailer_reply, Exception):
            raise mailer_reply
        return BytesIO(mailer_reply)

    class MockDatabase:
        def email_sent(self, message_id):
            emailed_message_ids.append(message_id)

    class MockApp(Flask):
        def __init__(self):
            self.config = {
                "MAILER_URL": mock_mailer_url,
                "MAILER_KEY": mock_mailer_key,
                "DATABASE": MockDatabase(),
            }

    monkeypatch.setattr(email_notification.request, "urlopen", mock_urlopen)
    monkeypatch.setattr(
        email_notification,
        "compose_notification_email",
        mock_compose_notification_email,
    )

    assert (
        send_contact_email(
            app=MockApp(),
            message_id=test_message_id,
            contact_email=test_contact_email,
            contact_name=test_contact_name,
            message_body=test_message_body,
        )
        is None
    )

    assert [
        (each.full_url, each.get_method(), each.headers, json.loads(each.data))
        for each in mailer_requests
    ] == [
        (
            mock_mailer_url,
            "POST",
            {
                "Authorization": f"Bearer {mock_mailer_key}",
                "Content-type": "application/json",
                "User-agent": "toonarmycaptain-website contact form",
            },
            {
                "site": "toonarmycaptain.com",
                "subject": mock_email_subject,
                "text": test_message_body,
                "reply_to": test_contact_email,
            },
        )
    ]
    assert emailed_message_ids == ([test_message_id] if email_sent else [])


def test_compose_notification_email():
    """EmailMessage composed with correct metadata."""
    test_contact_email = "contact@host.tld"
    test_contact_name = "Sir Lancelot"
    test_message_body = "Some amusing message."

    test_email_subject, test_email_body = compose_notification_email(
        test_contact_email, test_contact_name, test_message_body
    )

    assert test_email_subject == f"Contact from {test_contact_name}"
    assert test_email_body == (
        f"{test_message_body}\n\nfrom {test_contact_name}\n{test_contact_email}"
    )


def test_send_contact_email_async(monkeypatch):
    """Async dispatch runs send_contact_email on a daemon background thread."""
    recorded = {}

    class FakeThread:
        def __init__(self, target, args, daemon):
            self.target = target
            self.args = args
            recorded["daemon"] = daemon

        def start(self):
            self.target(*self.args)

    def fake_send(app, message_id, contact_email, contact_name, message_body):
        recorded["call"] = (app, message_id, contact_email, contact_name, message_body)

    monkeypatch.setattr(email_notification, "Thread", FakeThread)
    monkeypatch.setattr(email_notification, "send_contact_email", fake_send)

    email_notification.send_contact_email_async("app", 7, "c@e.tld", "Name", "body")

    assert recorded["call"] == ("app", 7, "c@e.tld", "Name", "body")
    assert recorded["daemon"] is True
