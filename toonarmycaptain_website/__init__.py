""" App factory """
import logging

from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFProtect
from markupsafe import Markup
from werkzeug.middleware.proxy_fix import ProxyFix

from .database import ContactDatabase

ABOUT_TEXT_STRING = (
    b'<html>'
    b'<p>I am <span style="font-family:monospace;">toonarmycaptain</span>, this is my personal '
    b'website.<br>There are many like it, but this one is mine.</p>'
    b'<p>The repo for the site is '
    b'<a href="https://github.com/toonarmycaptain/toonarmycaptain_website/">'
    b'toonarmycaptain_website</a>.</p>'
    b'<p>Created using Flask, CSS, Flask-wtf, smtp, Turnstile, <a href="https://pypi.org/project/padeploy/">padeploy</a>, and pytest.</p>'
    b'<p>Any comments or enquiries can be directed to the contact page, or '
    b'<a href="https://www.linkedin.com/in/davidantonini">LinkedIn</a>.</p>'
    b'</html>')


def create_app(test_config: dict|None = None) -> Flask:
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

    # INFO and up to stderr (Flask's default handler); PythonAnywhere captures
    # stderr in the server log. Module loggers under toonarmycaptain_website.*
    # propagate to this logger.
    app.logger.setLevel(logging.INFO)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_host=1, x_proto=1)  # ty: ignore[invalid-assignment]

    csrf = CSRFProtect(app)

    # Instantiate/connect to db:
    app.config['DATABASE'] = ContactDatabase(database_path=app.config["CONTACT_DATABASE_PATH"],
                                             message_max_length=app.config['CONTACT_MESSAGE_MAX_LENGTH'])

    from toonarmycaptain_website import main_site
    app.register_blueprint(main_site.bp)

    @app.context_processor
    def blog_url() -> dict:
        return dict(blog_url=app.config['BLOG_URL'])

    @app.route('/about-text/')
    def about_text() -> bytes:
        """
        Basic about text, mainly used for testing.

        :return: bytes
        """
        return ABOUT_TEXT_STRING

    @app.errorhandler(404)
    def page_not_found(e):
        message=Markup("Looks like you managed to lose something, or I did.<br>"
                 "Maybe try something else?")
        app.logger.error(msg=f'{e.code=}, {e.name=}, {e.description=}, {request.url=}')
        return render_template('error.html', code=e.code, name=e.name, error_message=message), e.code

    return app
