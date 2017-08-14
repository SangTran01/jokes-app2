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
from flask import request
from flask import send_from_directory
from flask import session
from models import db, User, Joke
from forms import AddJokeForm


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/jokesapp'
app.secret_key = env.get('SECRET_KEY', 'ThisIsASecretKey')
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


@app.route('/')
def index():
    jokes = json.loads(requests.get(
        "http://api.icndb.com/jokes/random/10").text)['value']
    return render_template('index.html', const=const, jokes=jokes)


@app.route("/dashboard")
@requires_auth
def dashboard():
    jokes = json.loads(requests.get(
        "http://api.icndb.com/jokes/random/10").text)['value']
    return render_template('dashboard.html', user=session['profile'], const=const, jokes=jokes)


@app.route("/addjoke", methods=['GET', 'POST'])
@requires_auth
def addjoke():
    form = AddJokeForm()
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('add_joke.html', user=session['profile'], const=const, form=form)
        else:
            userid = session['profile']["sub"][6:len( session['profile']["sub"] )]
            joke = form.joke.data
            print('YOUR JOKE')
            print(joke)
            print('USER')
            print(userid)
            return 'success'
            # newjoke = Joke()
    elif request.method == 'GET':
        return render_template('add_joke.html', user=session['profile'], const=const, form=form)


@app.route("/myjokes")
@requires_auth
def myjokes():
    return render_template('my_jokes.html', user=session['profile'], const=const)


@app.route("/editjoke/:jokeid")
@requires_auth
def editjoke():
    return render_template('edit_joke.html', user=session['profile'], const=const)


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
        userid = session['profile']["sub"][6:len( session['profile']["sub"] )]
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
