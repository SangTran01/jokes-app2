from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    userid = db.Column(db.String(50), primary_key=True)
    email = db.Column(db.String(100), unique=True)
    nickname = db.Column(db.String(100))
    image = db.Column(db.Text)
    jokes = db.relationship("Joke")
    ratings = db.relationship("Rating")

    def __init__(self, userid, email, nickname, image):
        self.userid = userid
        self.email = email
        self.nickname = nickname
        self.image = image


class Joke(db.Model):
    __tablename__ = 'jokes'
    jokeid = db.Column(db.Integer, primary_key=True)
    joke = db.Column(db.String(120))
    posting_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    userid = db.Column(db.String(50), db.ForeignKey("users.userid"))
    ratings = db.relationship("Rating", cascade="all, delete, delete-orphan")

    def __init__(self, joke, userid):
        self.joke = joke
        self.userid = userid


class Rating(db.Model):
    __tablename__ = 'ratings'
    rateid = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, default=0)
    jokeid = db.Column(db.Integer, db.ForeignKey("jokes.jokeid"))
    userid = db.Column(db.String(50), db.ForeignKey("users.userid"))

    def __init__(self, rating, jokeid, userid):
        self.rating = rating
        self.jokeid = jokeid
        self.userid = userid
