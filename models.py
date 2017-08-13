from flask_sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash

db = SQLAlchemy()
class User(db.Model):
    __tablename__ = 'users'
    userId = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    image = db.Column(db.String(120))
    jokes = db.relationship("Joke")

    def __init__(self, email, image):
        self.email = email
        self.image = image

class Joke(db.Model):
    __tablename__ = 'jokes'
    jokeId = db.Column(db.Integer, primary_key=True)
    joke = db.Column(db.String(120))
    posting_date = db.Column(db.DateTime)
    userId = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, joke, posting_date=None):
        self.joke = joke
        if posting_date is None:
            posting_date = datetime.utcnow()
        self.posting_date = posting_date
