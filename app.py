"""app.py"""

import os

from pathlib import Path

from flask import (Flask,
                   redirect,
                   request,
                   render_template,
                   url_for,
                   )

from database import ContactDatabase

app = Flask(__name__)

# Set config:
SECRET_KEY = os.urandom(64)

app.config['SECRET_KEY'] = SECRET_KEY

CONTACT_MESSAGE_MAX_LENGTH: int = 10000  # characters

# Instantiate/connect to db:
database_path = Path(Path.cwd(), 'contact.db')
DATABASE = ContactDatabase(database_path, CONTACT_MESSAGE_MAX_LENGTH)

# Late import to avoid circular import.
from contact.form import ContactForm


@app.route('/favicon.ico', methods=['GET'])
def favicon():
    """
    Serve webpage icon.
    """
    return redirect(url_for('static',
                            filename='favicon48x48.ico',
                            mimetype='image/vnd.microsoft.icon'
                            )
                    )


@app.route('/', methods=['GET'])
def base_url():
    """Redirect bare url to home page."""
    return redirect(url_for('home'), code=303)


@app.route('/home/', methods=['GET'])
def home():
    """Home page."""
    return render_template('home.html')


@app.route('/projects/', methods=['GET'])
def projects():
    """Projects page."""
    return render_template('projects.html', methods=['GET'])


@app.route('/blog/', methods=['GET'])
def blog():
    """Blog page."""
    return render_template('blog.html')


@app.route('/contact/', methods=['GET', 'POST'])
def contact():
    """
    Contact form route.

    Saves data to db, sends text message and email.
    Returns successful message on form validation, error on error.
    """
    form = ContactForm()

    if request.method == 'POST':
        'receive/validate format'
        if form.validate_on_submit():
            'using async:'
            '    store form contents in databases'
            '    send myself email'
            '    send myself text message'
            '    return template contact with thankyou instead of form'
            print(form.name, form.message, form.email)
            return render_template('contact.html', form=form)
        else:
            'return template with contact and error message'
    return render_template('contact.html', form=form)


@app.route('/about/', methods=['GET'])
def about():
    """About page."""
    return render_template('about.html')


if __name__ == '__main__':
    app.run()
