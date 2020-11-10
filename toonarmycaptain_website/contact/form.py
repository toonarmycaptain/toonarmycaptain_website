""" Form for contact page. """
from flask import current_app

from flask_wtf import (FlaskForm,
                       RecaptchaField,
                       )
from wtforms import (StringField,
                     SubmitField,
                     TextAreaField,
                     )
from wtforms.fields.html5 import EmailField
from wtforms.validators import (DataRequired,
                                Email,
                                Length,
                                )

CONTACT_MESSAGE_MAX_LENGTH = current_app.config['CONTACT_MESSAGE_MAX_LENGTH']


class ContactForm(FlaskForm):
    """Contact form."""
    name = StringField(label='Name',
                       validators=[Length(min=3, max=255,
                                          message="Name must be between 4 "
                                                  "and 255 characters."),
                                   DataRequired(),
                                   ],
                       render_kw={'minlength': 3, 'maxlength': 255},
                       )
    email = EmailField(label='Email',
                       validators=[Email(message='Not a valid email address.'),
                                   Length(min=6, max=255),
                                   DataRequired(),
                                   ],
                       render_kw={'minlength': 6, 'maxlength': 255}
                       )

    message = TextAreaField(label='Message',
                            validators=[Length(min=4, max=CONTACT_MESSAGE_MAX_LENGTH,
                                               message=f"Message must be between 4 "
                                                       f"and {CONTACT_MESSAGE_MAX_LENGTH} "
                                                       f'characters.',
                                               ),
                                        DataRequired()],
                            render_kw={'minlength': 4,
                                       'maxlength': CONTACT_MESSAGE_MAX_LENGTH},
                            )
    # recaptcha = RecaptchaField()
    submit = SubmitField('Submit')
