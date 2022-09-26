from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db' # relative path to where the app is
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    @staticmethod
    def create(username, password):  # create new user
        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()

def get_country_code():
    """Return the two-letter country code for this IP address."""
    import json
    from urllib.request import urlopen
    url = 'http://ipinfo.io/json'
    response = urlopen(url)
    data = json.load(response)

    return data['country'].lower()

@app.route('/initalize', methods=['GET'])
def initalize():
    """Create the database."""
    import os
    if os.path.exists('user.db'):
        os.remove('user.db')
    db.create_all()
    import json
    with open('./static/credentials.json') as f:
        credentials = json.load(f)
    
    for user in credentials:
        User.create(user['username'], generate_password_hash(user['password'], method='sha256'))

    return 'Database created and initialized'

# Webpage
@app.route('/', methods=['GET'])
def index():
    """Return the index page.
    
    State: 
        None - refresh or first time visiting
        1 - username does not contain 2 letter country code
        2 - user does not exist or wrong password
        3 - Database not initialized
        4 - Username and password are blank
    """
    state = request.args.get('state')
    return render_template('index.html', state = state)


@app.route('/home', methods=['GET'])
def home():
    """Return the home page."""
    username = request.args.get('username')
    password = request.args.get('password')
    encrypt = request.args.get('encrypt')

    if username:
        return render_template('home.html', username = username, password = password, encrypt = encrypt)
    else:
        return redirect(url_for('index', state=None))


@app.route('/login', methods=["POST"])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Corner cases
    import os
    if not os.path.exists('user.db'):
        return redirect(url_for('index', state=3))
    if not username or not password:
        return redirect(url_for('index', state=4))

    # Check if username contains country code
    country_code = get_country_code()

    if len(username) >= 2 and country_code not in username[:2].lower():
        return redirect(url_for('index', state=1))

    # Check if user exists and matches password
    user = db.session.query(User).filter_by(username=username.lower()).first()
    if user is None or not check_password_hash(user.password, password):
        return redirect(url_for('index', state=2))

    # Return Credentials
    return redirect(url_for('home', username=username.lower(), password= password, encrypt = user.password))




if __name__ == '__main__':
    app.run(port=8000, debug=True, host='0.0.0.0')