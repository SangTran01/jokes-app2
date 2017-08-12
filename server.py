import json

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



app = Flask(__name__)
app.secret_key = env.get('SECRET_KEY')
print(env.get('AUTH0_CALLBACK_URL'))
load_dotenv(path.join(path.dirname(__file__), ".env"))

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
    print('callback')
    print(env.get('AUTH0_CALLBACK_URL'))
    return render_template('index.html', const=const)


@app.route("/dashboard")
@requires_auth
def dashboard():
    return render_template('dashboard.html', user=session['profile'], const=const)


# Here we're using the /callback route.
@app.route('/callback')
def callback_handling():
    print('HEHEHEHEEHEHEH')
    code = request.args.get('code')
    get_token = GetToken(const['AUTH0_DOMAIN'])
    auth0_users = Users(const['AUTH0_DOMAIN'])
    token = get_token.authorization_code(const['AUTH0_CLIENT_ID'],
                                         const['AUTH0_CLIENT_SECRET'], code, const['AUTH0_CALLBACK_URL'])
    user_info = auth0_users.userinfo(token['access_token'])
    session['profile'] = json.loads(user_info)
    return redirect('/dashboard')


@app.route('/logout')
def logout():
    session.clear()
    parsed_base_url = urlparse(const['AUTH0_CALLBACK_URL'])
    base_url = parsed_base_url.scheme + '://' + parsed_base_url.netloc
    return redirect('https://%s/v2/logout?returnTo=%s&client_id=%s' % (const['AUTH0_DOMAIN'], base_url, const['AUTH0_CLIENT_ID']))

if __name__ == '__main__':
    app.run(debug=True)
