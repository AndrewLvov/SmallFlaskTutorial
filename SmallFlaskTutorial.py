import re
import requests
import os

from flask import Flask, render_template, request,\
    session, redirect

app = Flask(__name__)
app.debug = True
app.secret_key = 'A0Zr98j/3yw R~5HH!xmN]LWX/,?RT'

DIR = os.path.dirname(__file__)


def extract_money_sums(content):
    patt = re.compile(r'(\w+ )?(\$[\d .]*\d)( \w+)?')
    return (''.join(values) for values in patt.findall(content))

@app.route('/', methods=['GET', 'POST'])
def home():
    ctx = {}
    user = session.get('logged_user')
    if request.method == 'POST':
        url = request.form['url']
        print('Received POST, {} !!!'.format(request.form))
        ctx['url'] = url
        response = requests.get(url)
        if response.status_code == 200:  # OK
            # session['logged_user'] vs  session.get('logged_user')
            if user:
                with open(os.path.join(DIR, 'user_data/{}.txt'.format(user)),
                          'a') as f:
                    f.write('{}\n'.format(url))
            money_sums = extract_money_sums(
                response.content.decode(response.encoding or 'ascii'))
            ctx['money_sums'] = money_sums
    # ctx = {'url': 'http://google.com'}
    # f(**ctx) => f(url='http://google.com')
    if user:
        with open(os.path.join(DIR, 'user_data/{}.txt'.format(user)), 'r') as f:
            ctx['stored_urls'] = f.read().split('\n')
    return render_template('index.html', **ctx)
    # return render_template('index.html',
    #     url=..., content=...)


def login_user(username):
    session['logged_user'] = username


def logout_user():
    del session['logged_user']


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with open(os.path.join(DIR, 'users.txt'), 'w') as f:
            f.write('{} {}\n'. format(username, password))
        with open(os.path.join(DIR, 'user_data/{}.txt'.format(username)), 'w') as f:
            pass
        login_user(username)
        return redirect('/')

    return render_template('register.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    ctx = {}
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with open(os.path.join(DIR, 'users.txt'), 'r') as f:
            for line in f:
                existing_user, existing_pass = line.split(' ')
                if username == existing_user and \
                   password == existing_pass:
                    login_user(username)
                    return redirect('/')
            ctx['error'] = 'Username or password invalid'

    return render_template('login.html', **ctx)


@app.route('/logout/', methods=['GET'])
def logout():
    logout_user()
    return redirect('/')


if __name__ == '__main__':
    app.run(use_reloader=True)
