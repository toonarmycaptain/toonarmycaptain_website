"""Test app fixture"""
from pathlib import Path
from random import randint

import pytest

from flask import Flask

from toonarmycaptain_website import create_app

default_test_config = {'SECRET_KEY': b'some secret key',

                       'CONTACT_DATABASE_PATH': 'Not yet defined.',
                       'CONTACT_MESSAGE_MAX_LENGTH': 31415,

                       'SERVER_EMAIL_ADDRESS': 'Not yet defined.',
                       'SERVER_EMAIL_PASSWORD': 'Not yet defined.',
                       'CONTACT_EMAIL_ADDRESS': 'Not yet defined.',

                       'CONTACT_CELL_NUMBER': 'Not yet defined.',
                       }


def app_with_test_config(db_dir_path: Path) -> Flask:
    """
    Instantiate app with given config.

    :param db_dir_path: Path to dir containing test db.
    :return: Flask app
    """
    num = randint(1, 1000000000)
    default_test_config['CONTACT_DATABASE_PATH'] = Path(db_dir_path, f'test_db{num}')

    app = create_app(default_test_config)
    return app


@pytest.fixture
def test_app(tmpdir):
    """Return app-providing function."""
    yield app_with_test_config(tmpdir)


def test_app_fixture(test_app):
    for key, value in default_test_config.items():
        assert test_app.config[key] == value

@pytest.fixture
def test_client(test_app):
    return test_app.test_client()
