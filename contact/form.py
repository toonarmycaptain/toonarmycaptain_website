""" Form for contact page. """
from flask_wtf import (FlaskForm,
                       RecaptchaField,
                       )
from wtforms import (StringField,
                     SubmitField,
                     TextAreaField,
                     )
from wtforms.validators import (DataRequired,
                                Email,
                                Length,
                                )

from app import contact_message_max_length


class ContactForm(FlaskForm):
    """Contact form."""
    name = StringField(label='Name',
                       validators=[Length(min=3, max=255),
                                   DataRequired()],
                       render_kw={'minlength': 3, 'maxlength': 255},
                       )
    email = StringField(label='Email',
                        validators=[Email(message='Not a valid email address.'),
                                    Length(min=6, max=255),
                                    DataRequired(),
                                    ],
                        render_kw={'minlength': 6, 'maxlength': 255}
                        )

    message = TextAreaField(label='Message',
                            validators=[Length(min=4, max=contact_message_max_length,
                                               message=f'Message must be between 4 '
                                                       f'and {contact_message_max_length} '
                                                       f'characters.',
                                               ),
                                        DataRequired()],
                            render_kw={'maxlength': contact_message_max_length},
                            )
    # recaptcha = RecaptchaField()
    submit = SubmitField('Submit')
