from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    userid = db.Column(db.String(50), primary_key=True)
    email = db.Column(db.String(100), unique=True)
    nickname = db.Column(db.String(100))
    image = db.Column(db.Text)
    jokes = db.relationship("Joke")

    def __init__(self, userid, email, nickname, image):
        self.userid = userid
        self.email = email
        self.nickname = nickname
        self.image = image


class Joke(db.Model):
    __tablename__ = 'jokes'
    jokeid = db.Column(db.Integer, primary_key=True)
    joke = db.Column(db.String(120))
    posting_date = db.Column(db.DateTime)
    rating = db.Column(db.Integer, default=0)
    userid = db.Column(db.String(50), db.ForeignKey("users.userid"))

    def __init__(self, joke, posting_date=None):
        self.joke = joke
        if posting_date is None:
            posting_date = datetime.utcnow()
        self.posting_date = posting_date
