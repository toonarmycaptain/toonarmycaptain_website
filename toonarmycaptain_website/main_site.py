"""main_site.py"""
from flask import (current_app as app,
                   Blueprint,
                   flash,
                   redirect,
                   request,
                   render_template,
                   url_for,
                   )
from flask_wtf.csrf import CSRFError

bp = Blueprint("my_site", __name__)


@bp.route('/favicon.ico', methods=['GET'])
def favicon():
    """
    Serve webpage icon.
    """
    return redirect(url_for('static',
                            filename='favicon48x48.ico',
                            mimetype='image/vnd.microsoft.icon'
                            )
                    )


@bp.route('/', methods=['GET'])
def base_url():
    """Redirect bare url to home page."""
    return redirect(url_for('my_site.home'), code=301)


@bp.route('/home/', methods=['GET'])
def home():
    """Home page."""
    return render_template('home.html')


@bp.route('/projects/', methods=['GET'])
def projects():
    """Projects page."""
    return render_template('projects.html', methods=['GET'])


@bp.route('/blog/', methods=['GET'])
def blog():
    """Blog page."""
    return render_template('blog.html')


@bp.route('/contact/', methods=['GET', 'POST'])
def contact():
    """
    Contact form route.

    Saves data to db, sends text message and email.
    Returns successful message on form validation, error on error.
    """

    from toonarmycaptain_website.contact.form import ContactForm
    from toonarmycaptain_website.contact.email_notification import send_contact_email

    form = ContactForm()

    if request.method == 'POST':
        'receive/validate format'
        if form.validate_on_submit():
            'store form contents in databases'
            message_id = app.DATABASE.store_contact(name=form.name.data,
                                                    email=form.email.data,
                                                    message=form.message.data)
            'using async:'
            '    send myself email'
            send_contact_email(message_id=message_id,
                               contact_email=form.email.data,
                               contact_name=form.name.data,
                               message_body=form.message.data)
            '    send myself text message'

            flash("success message", 'successful_submission')
            return redirect(url_for('my_site.contact'))
        # else:
        #     Template will render form.errors
    return render_template('contact.html', form=form)


@bp.route('/about/', methods=['GET'])
def about():
    """About page."""
    return render_template('about.html')


@bp.errorhandler(CSRFError)
def handle_csrf_error(e):
    """
    Redirects user to requested page in event of CSRF Error.

    Assumes all routes are under my_site blueprint.
    """
    return redirect(url_for(f'my_site.{request.path[1:-1]}'))


if __name__ == '__main__':
    app.run()
