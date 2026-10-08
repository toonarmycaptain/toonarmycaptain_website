""" Form for contact page. """
from flask import current_app

from flask_wtf import (FlaskForm,
                       RecaptchaField,
                       )
from wtforms import (EmailField,
                     StringField,
                     SubmitField,
                     TextAreaField,
                     )
from wtforms.validators import (DataRequired,
                                Email,
                                Length,
                                )


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

    message = TextAreaField(label='Message')
    # recaptcha = RecaptchaField()
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        max_length = current_app.config['CONTACT_MESSAGE_MAX_LENGTH']
        self.message.validators = [  # ty: ignore[invalid-assignment]
            Length(min=4, max=max_length,
                   message=f"Message must be between 4 and {max_length} characters."),
            DataRequired(),
        ]
        self.message.render_kw = {'minlength': 4, 'maxlength': max_length}
