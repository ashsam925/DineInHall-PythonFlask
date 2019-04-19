from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Optional, NumberRange


class ReviewForm(FlaskForm):
    stars = IntegerField('Stars', validators=[DataRequired(), NumberRange(min=1, max=5)])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Submit')