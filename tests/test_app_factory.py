""" Test app factory. """
import flask

from toonarmycaptain_website import ABOUT_TEXT_STRING, create_app


def test_testing_config():
    """App should be under testing config when run by pytest."""
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_about_text(test_client):
    """About text route returns about text."""
    response = test_client.get('/about_text/')
    assert response.data == ABOUT_TEXT_STRING


def test_redirects(test_client):
    """Route w/out trailing backslash redirects (to route with backslash)."""
    response = test_client.get('about_text')
    assert response.status_code == 308


def test_create_app_name():
    """Test app has correct name."""
    app = create_app()
    assert isinstance(app, flask.app.Flask)
    assert app.name == 'toonarmycaptain_website'
