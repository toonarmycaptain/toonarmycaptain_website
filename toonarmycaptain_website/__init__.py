""" App factory """

from flask import Flask
from flask_wtf.csrf import CSRFProtect

from .database import ContactDatabase


def create_app(test_config=None) -> Flask:
    app: Flask = Flask(__name__)
    # Defaults to be overridden by instance config:

    app.config.from_pyfile('default_config.py')

    # Load runtime config:
    if test_config is None:
        app.config.from_pyfile('app_config.py')
    else:  # Load testing config:
        app.config.update(test_config)

    csrf = CSRFProtect(app)

    # CONTACT_MESSAGE_MAX_LENGTH: int = app.config['CONTACT_MESSAGE_MAX_LENGTH']

    # Instantiate/connect to db:

    app.DATABASE = ContactDatabase(app.config["CONTACT_DATABASE_PATH"],
                                   app.config['CONTACT_MESSAGE_MAX_LENGTH'])

    from toonarmycaptain_website import personal_site
    app.register_blueprint(personal_site.bp)

    return app
