""" Test app factory. """
from pathlib import Path

import flask

from toonarmycaptain_website import ABOUT_TEXT_STRING, create_app


def test_testing_config(test_app, tmpdir):
    """App should be under testing config when run by pytest."""
    # Use app with default/dummy production config, except for db in temp:
    assert not create_app({'CONTACT_DATABASE_PATH': Path(tmpdir, 'dummy.db')}).testing
    # Test app passing testing=true config:
    assert create_app({'CONTACT_DATABASE_PATH': Path(tmpdir, 'dummy.db'),
                       'TESTING': True}).testing
    # Test fixture:
    assert test_app.testing


def test_about_text(test_client):
    """About text route returns about text."""
    response = test_client.get('/about_text/')
    assert response.data == ABOUT_TEXT_STRING


def test_redirects(test_client):
    """Route w/out trailing backslash redirects (to route with backslash)."""
    response = test_client.get('about_text')
    assert response.status_code == 308
    assert response.headers['Location'] == f'http://localhost/about_text/'


def test_create_app_name(test_app):
    """Test app has correct name."""
    assert isinstance(test_app, flask.app.Flask)
    assert test_app.name == 'toonarmycaptain_website'
