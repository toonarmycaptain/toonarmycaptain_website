"""main_site.py"""
from flask import (current_app as app,
                   Blueprint,
                   flash,
                   redirect,
                   request,
                   render_template,
                   session,
                   url_for,
                   )
from flask_wtf.csrf import CSRFError

from toonarmycaptain_website.contact.email_notification import send_contact_email
from toonarmycaptain_website.contact.form import ContactForm
from toonarmycaptain_website.contact.turnstile import verify_turnstile
from toonarmycaptain_website.utils import client_ip

bp = Blueprint("my_site", __name__)


@bp.route('/favicon.ico', methods=['GET'])
def favicon():
    """
    Serve webpage icon.
    """
    return redirect(url_for('static',
                            filename='favicon.ico',
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
    """
    Blog page.

    Links to dev.to blog. May in future embed blog/posts.
    """
    return redirect(app.config['BLOG_URL'])


@bp.route('/contact/', methods=['GET', 'POST'])
def contact():
    """
    Contact form route.

    Saves data to db, sends text message and email.
    Returns successful message on form validation, error on error.
    """
    expired_form = session.pop('_expired_form', None)
    form = ContactForm(data=expired_form) if expired_form else ContactForm()

    if request.method == 'POST':
        # receive/validate format
        if form.validate_on_submit():
            DATABASE = app.config['DATABASE']
            captcha_passed = verify_turnstile(request.form.get('cf-turnstile-response', ''),
                                              secret=app.config['TURNSTILE_SECRET_KEY'],
                                              remoteip=client_ip())
            # store form contents in databases, flagging spam rather than dropping it
            person_id = DATABASE.store_person(name=form.name.data,
                                              email=form.email.data)
            message_id = DATABASE.store_message_text(person_id=person_id,
                                                     message_text=form.message.data,
                                                     captcha_passed=captcha_passed)
            app.logger.info(f"Contact message {message_id} stored, captcha_passed={captcha_passed}")
            # Don't send email notification if flagged as spam [still saved in db]
            if captcha_passed:
                send_contact_email(app,
                                   message_id=message_id,
                                   contact_email=form.email.data,
                                   contact_name=form.name.data,
                                   message_body=form.message.data)
            # send myself text message

            flash("success message", 'successful_submission')
            return redirect(url_for('my_site.contact'))
    return render_template('contact.html', form=form)


@bp.route('/about/', methods=['GET'])
def about():
    """About page."""
    return render_template('about.html')


@bp.errorhandler(CSRFError)
def handle_csrf_error(e):
    """
    Redirects user to requested page in event of CSRF Error.

    Stashes form data in session so user doesn't lose their input.
    Assumes all routes are under my_site blueprint.
    """
    app.logger.warning(f"CSRF error on {request.path}: {e.description}")
    if request.form:
        session['_expired_form'] = {k: v for k, v in request.form.items() if k != 'csrf_token'}
    flash("Your session expired. Please try again.", 'error')
    return redirect(url_for(f'my_site.{request.path[1:-1]}'))


@bp.route('/adam_todo/', methods=['GET'])
def adam_todo():
    """Adam's stuff."""
    return render_template('adam_todo.html')


if __name__ == '__main__':
    app.run()
