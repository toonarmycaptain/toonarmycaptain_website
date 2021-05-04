""" App factory """

from flask import Flask
from flask_wtf.csrf import CSRFProtect

from .database import ContactDatabase

ABOUT_TEXT_STRING = (
    b'<html>'
    b'<p>I am <span style="font-family:monospace;">toonarmycaptain</span>, this is my personal '
    b'website.</p>'
    b'<p>The repo for the site is '
    b'<a href="https://github.com/toonarmycaptain/toonarmycaptain_website/">'
    b'toonarmycaptain_website</a>.</p>'
    b'<p>I primarily created the site using Flask, some basic CSS, Flask-wtf, and pytest.</p>'
    b'<p>Any comments or enquiries can be directed to the contact page, or '
    b'<a href="https://twitter.com/toonarmycaptain">toonarmycaptain</a>.</p>'
    b'</html>')


def create_app(test_config: dict = None) -> Flask:
    """
    Create application instance.

    :param test_config: dict or None
    :return: Flask
    """
    app: Flask = Flask(__name__)
    # Defaults to be overridden by instance config:

    app.config.from_pyfile('default_config.py')

    # Load runtime config:
    if test_config is None:  # Load production config.
        app.config.from_pyfile('app_config.py')
    else:  # Load testing config:
        app.config.update(test_config)

    csrf = CSRFProtect(app)

    # CONTACT_MESSAGE_MAX_LENGTH: int = app.config['CONTACT_MESSAGE_MAX_LENGTH']

    # Instantiate/connect to db:

    app.DATABASE = ContactDatabase(database_path=app.config["CONTACT_DATABASE_PATH"],
                                   message_max_length=app.config['CONTACT_MESSAGE_MAX_LENGTH'])

    from toonarmycaptain_website import main_site
    app.register_blueprint(main_site.bp)

    app.blog_url = "https://dev.to/toonarmycaptain/"

    @app.context_processor
    def blog_url() -> dict:
        return dict(blog_url=app.blog_url)

    @app.route('/about_text/')
    def about_text() -> bytes:
        """
        Basic about text, mainly used for testing.

        :return: bytes
        """
        return ABOUT_TEXT_STRING

    return app
