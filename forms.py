from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Length

class AddJokeForm(FlaskForm):
    joke = StringField('joke', validators=[DataRequired("Can't leave joke empty"), Length(min=10, message="This a joke? Your joke should be at least 10 characters long")], widget=TextArea())
    submit = SubmitField("Submit")


class EditJokeForm(FlaskForm):
    joke = StringField('joke', validators=[DataRequired("Can't leave joke empty"), Length(min=10, message="This a joke? Your joke should be at least 10 characters long")], widget=TextArea())
    update = SubmitField("Update")