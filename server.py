import json
import requests

from auth0.v3.authentication import GetToken
from auth0.v3.authentication import Users
from urllib.parse import urlparse
from os import environ as env, path
from dotenv import load_dotenv
from functools import wraps
from flask import Flask
from flask import redirect
from flask import render_template
from flask import url_for
from flask import request
from flask import send_from_directory
from flask import session
from models import db, User, Joke, Rating
from forms import AddJokeForm, EditJokeForm
from sqlalchemy.sql import text


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/jokesapp'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://bhtkbijjrjlznn:9a84b5af24251bc6838c865b734e802679d032c730a28fd1cc44b1b285bad306@ec2-23-23-221-255.compute-1.amazonaws.com:5432/d97jfnk18117a9'
app.secret_key = env.get('SECRET_KEY', 'ThisIsASecretKey')
# load_dotenv(path.join(path.dirname(__file__), ".env"))
load_dotenv(path.join(path.dirname(__file__), ".envl"))
db.init_app(app)

const = {
    'AUTH0_CALLBACK_URL': env.get('AUTH0_CALLBACK_URL'),
    'AUTH0_CLIENT_ID': env.get('AUTH0_CLIENT_ID'),
    'AUTH0_CLIENT_SECRET': env.get('AUTH0_CLIENT_SECRET'),
    'AUTH0_DOMAIN': env.get('AUTH0_DOMAIN')
}


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
            # Redirect to Login page here
            return redirect('/')
        return f(*args, **kwargs)
    return decorated


def get_or_create(session, model, **kwargs):
    instance = db.session.query(model).filter_by(**kwargs).first()
    if instance:
        print('got one')
        return True
    else:
        print('no got')
        return False


@app.route('/')
def index():
    # get rating
    jokes = db.engine.execute(
        text('select users.nickname, users.image, jokes.userid, jokes.joke, ' +
             'jokes.jokeid, jokes.posting_date, SUM(ratings.rating) AS "total" ' +
             'from users join jokes on users.userid = jokes.userid left join ratings on jokes.jokeid = ratings.jokeid ' +
             'group by users.nickname, users.image, jokes.userid, jokes.joke, jokes.jokeid ' +
             'order by "total" DESC'))
    return render_template('index.html', const=const, jokes=jokes)


@app.route("/dashboard")
@requires_auth
def dashboard():
    # get rating
    userid = session['profile']["sub"]
    userid = userid[userid.index('|') + 1:len(userid)]
    ratings = Rating.query.all()

    if len(ratings) == 0:
        jokes = db.engine.execute(
        text('select users.nickname, users.image, jokes.jokeid, jokes.joke, ' +
             'jokes.posting_date, jokes.userid ' +
             'from users inner join jokes on users.userid = jokes.userid'))
    else:
        jokes = db.engine.execute(
        text('select users.nickname, users.image, jokes.userid, jokes.joke, ' +
             'jokes.jokeid, jokes.posting_date, SUM(ratings.rating) AS "total" ' +
             'from users join jokes on users.userid = jokes.userid left join ratings on jokes.jokeid = ratings.jokeid ' +
             'group by users.nickname, users.image, jokes.userid, jokes.joke, jokes.jokeid ' +
             'order by "total" DESC'))
    return render_template('dashboard.html', user=session['profile'], const=const, jokes=jokes, userid=userid)


@app.route("/addjoke", methods=['GET', 'POST'])
@requires_auth
def addjoke():
    form = AddJokeForm()
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('add_joke.html', user=session['profile'], const=const, form=form)
        else:
            userid = session['profile']["sub"]
            userid = userid[userid.index('|') + 1:len(userid)]
            joke = form.joke.data
            # create joke and rating for that joke
            new_joke = Joke(joke, userid)
            db.session.add(new_joke)
            db.session.commit()
            return redirect(url_for('dashboard'))
    elif request.method == 'GET':
        return render_template('add_joke.html', user=session['profile'], const=const, form=form)


@app.route("/myjokes")
@requires_auth
def myjokes():
    # get rating
    userid = session['profile']["sub"]
    userid = userid[userid.index('|') + 1:len(userid)]
    ratings = Rating.query.all()
    strUserid = str(userid)
    if len(ratings) == 0:
        jokes = db.engine.execute(
        text("select users.nickname, users.image, users.email, jokes.jokeid, jokes.joke, " +
             "jokes.posting_date, jokes.userid " +
             "from users inner join jokes on users.userid = jokes.userid " + 
             "where jokes.userid = '%s'" % userid))
    else:
        jokes = db.engine.execute(
        text("select users.nickname, users.image, jokes.userid, jokes.joke, " +
             "jokes.jokeid, jokes.posting_date, SUM(ratings.rating) AS " + "Total" + " " +
             "from users join jokes on users.userid = jokes.userid left join ratings on jokes.jokeid = ratings.jokeid " +
             "where jokes.userid = '%s'" % userid +
             "group by users.nickname, users.image, jokes.userid, jokes.joke, jokes.jokeid " +
             "order by " + "Total" + " DESC"))
    return render_template('my_jokes.html', user=session['profile'], const=const, jokes=jokes, userid=userid)


@app.route("/editjoke/<jokeid>", methods=['GET', 'POST'])
@requires_auth
def editjoke(jokeid):
    userid = session['profile']["sub"]
    userid = userid[userid.index('|') + 1:len(userid)]
    # check your ID matches the joke's userid to be able to EDIT
    # get joke object with jokeid
    joke = Joke.query.filter_by(jokeid=jokeid).first()
    if userid != joke.userid:
        return render_template('error.html', user=session['profile'], const=const)
    form = EditJokeForm()
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('edit_joke.html', user=session['profile'], const=const, form=form, joke=joke)
        else:
            # get joke object and update
            updated_joke = form.joke.data
            joke.joke = updated_joke
            db.session.commit()
            return redirect(url_for('dashboard'))
    elif request.method == 'GET':
        return render_template('edit_joke.html', user=session['profile'], const=const, form=form, joke=joke)


@app.route("/deletejoke/<jokeid>")
@requires_auth
def deletejoke(jokeid):
    userid = session['profile']["sub"]
    userid = userid[userid.index('|') + 1:len(userid)]
    # check your ID matches the joke's userid to be able to EDIT
    # get joke object with jokeid
    joke = Joke.query.filter_by(jokeid=jokeid).first()
    # print(joke.jokeid)
    if userid != joke.userid:
        return render_template('error.html', user=session['profile'], const=const)
    else:
        Joke.query.filter_by(jokeid=jokeid).delete()
        db.session.commit()
        return redirect(url_for('dashboard'))


@app.route("/editrating/<jokeid>/<rating>")
@requires_auth
def editrating(jokeid, rating):
    userid = session['profile']["sub"]
    userid = userid[userid.index('|') + 1:len(userid)]
    rows = Rating.query.filter_by(jokeid=jokeid, userid=userid).count()
    print(rows)
    print('what i clicked is %s' % rating)

    if rows == 0:
        if rating == '1':
            print('clicked 1')
            new_rating = Rating(int(rating), jokeid, userid)
            db.session.add(new_rating)
            db.session.commit()
        elif rating == '-1':
            print('clicked -1')
            new_rating = Rating(int(rating), jokeid, userid)
            db.session.add(new_rating)
            db.session.commit()
        return redirect('/dashboard')
    else:
        return render_template('error_voted.html', user=session['profile'], const=const)

# Here we're using the /callback route.
@app.route('/callback')
def callback_handling():
    code = request.args.get('code')
    get_token = GetToken(const['AUTH0_DOMAIN'])
    auth0_users = Users(const['AUTH0_DOMAIN'])
    token = get_token.authorization_code(const['AUTH0_CLIENT_ID'],
                                         const['AUTH0_CLIENT_SECRET'], code, const['AUTH0_CALLBACK_URL'])
    user_info = auth0_users.userinfo(token['access_token'])
    session['profile'] = json.loads(user_info)
    print('USER INFO')
    # check if user in db
    user = User.query.filter_by(email=session['profile']['email']).first()
    print('CHECK')
    if user is None:
        print('new user being added to db')
        userid = session['profile']["sub"]
        userid = userid[userid.index('|') + 1:len(userid)]
        new_user = User(userid, session['profile']['email'], session['profile'][
                        'nickname'], session['profile']['picture'])
        db.session.add(new_user)
        db.session.commit()
    else:
        print('old user')
    return redirect('/dashboard')


@app.route('/logout')
def logout():
    session.clear()
    parsed_base_url = urlparse(const['AUTH0_CALLBACK_URL'])
    base_url = parsed_base_url.scheme + '://' + parsed_base_url.netloc
    return redirect('https://%s/v2/logout?returnTo=%s&client_id=%s' % (const['AUTH0_DOMAIN'], base_url, const['AUTH0_CLIENT_ID']))


if __name__ == '__main__':
    app.run(debug=True)
