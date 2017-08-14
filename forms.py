from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Length

class AddJokeForm(FlaskForm):
    joke = StringField('joke', validators=[DataRequired("Can't leave joke empty"), Length(min=20, message="This a joke? Your joke should be at least 20 characters long")], widget=TextArea())
    submit = SubmitField("Submit")