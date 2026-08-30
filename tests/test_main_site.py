""" Test main routes. """
import pytest

from toonarmycaptain_website.utils import client_ip


@pytest.mark.parametrize('headers, expected',
                         [({'X-Real-IP': '203.0.113.7'}, '203.0.113.7'),  # Worker-forwarded visitor IP.
                          ({'CF-Connecting-IP': '198.51.100.9'}, '198.51.100.9'),  # Direct-CF fallback.
                          ({'X-Real-IP': '203.0.113.7',
                            'CF-Connecting-IP': '198.51.100.9'}, '203.0.113.7'),  # X-Real-IP preferred.
                          ({}, None),  # No proxy headers -> None, never the proxy remote_addr.
                          ])
def test_client_ip(test_app, headers, expected):
    """client_ip reads the real visitor IP from proxy headers, never remote_addr."""
    with test_app.test_request_context('/contact/', headers=headers):
        assert client_ip() == expected


def test_favicon(test_client, test_app):
    """Should return favicon."""
    response = test_client.get('/favicon.ico')
    assert response.status_code == 302
    import urllib.parse
    assert urllib.parse.unquote(response.headers['Location']) in 'http://localhost/static/favicon.ico?mimetype=image/vnd.microsoft.icon'


def test_base_url_redirects_to_home(test_client, test_app):
    """Base url should go to home page."""
    response = test_client.get('/')
    assert response.status_code == 301
    assert response.headers['Location'] in 'http://localhost/home/'


def test_bare_base_url_redirects_to_home(test_client, test_app):
    """Base url without / should redirect to home page."""
    response = test_client.get('')
    assert response.status_code == 308
    assert response.headers['Location'] in 'http://localhost/'

    # Ensure home page loaded.
    response = test_client.get('', follow_redirects=True)
    assert response.status_code == 200
    assert b"Home - toonarmycaptain.com" in response.data


@pytest.mark.parametrize('route',
                         ['home',
                          'projects',
                          'blog',
                          'about',
                          'contact',
                          ])
def test_subpage_routes_without_trailing_slash_redirects(test_client, test_app,
                                                         route):
    """Subpage routes without / redirect."""
    response = test_client.get(route)
    assert response.status_code == 308
    assert response.headers['Location'] in f'http://localhost/{route}/'


@pytest.mark.parametrize('route, page_title',
                         [('home', b'Home'),
                          ('projects', b'Projects'),
                          ('contact', b'Contact'),
                          ('about', b'About me'),
                          ])
def test_subpage_internal_routes(test_client, test_app,
                                 route, page_title):
    """Subpages load content."""
    response = test_client.get(f'{route}/')
    assert response.status_code == 200
    # Equivalent to assert f'{page_title} - toonarmycaptain.com' in str(response.data)
    assert page_title + b' - toonarmycaptain.com' in response.data


def test_redirect_to_blog(test_client, test_app):
    """Redirects to blog."""
    response = test_client.get('blog/')
    assert response.status_code == 302
    assert response.headers['Location'] in test_app.config['BLOG_URL']
