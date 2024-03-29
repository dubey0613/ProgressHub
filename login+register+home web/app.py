from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from flask import session,request
import requests

from flask import jsonify


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_database.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    codechef = db.Column(db.String(100))
    codeforces = db.Column(db.String(100))
    leetcode = db.Column(db.String(100))
    hackerrank = db.Column(db.String(100))
    github = db.Column(db.String(100))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    leetcode_id = StringField('LeetCode ID')
    codechef_id = StringField('CodeChef ID')
    codeforces_id = StringField('Codeforces ID')
    github_id = StringField('GitHub ID')
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email address already exists. Please log in.')
            return redirect(url_for('login'))
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            codechef=form.codechef_id.data,
            codeforces=form.codeforces_id.data,
            leetcode=form.leetcode_id.data,
            github=form.github_id.data
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully.')
            session['user'] = user.email 
            print(session['user'])
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.')
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')



@app.route('/contest', methods=['GET', 'POST'])
def contest():
            response = requests.get('https://kontests.net/api/v1/all')
            if response.status_code == 200:
                events = response.json()
            else:
                events = []  # Empty list if API request fails
            return render_template('contest.html',events=events)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('home'))


@app.route("/user_id")
def fetch_apps():
    email=session['user']
    user = User.query.filter_by(email=email).first()
    leetcode=user.leetcode
    codechef=user.codechef
    codeforces=user.codeforces
    print(leetcode)

    response1 = requests.get(f'http://127.0.0.1:8000/api/leetcode/{leetcode}')
    response2 = requests.get(f'http://127.0.0.1:8000/api/codechef/{codechef}')
    # response3 = requests.get(f'http://127.0.0.1:8000/api/codeforces/{codeforces}')

    combined_response = {}

    if response1.status_code == 200:
        combined_response['leetcode'] = response1.json()

    if response2.status_code == 200:
        combined_response['codechef'] = response2.json()


    if combined_response:
        return render_template("display.html",combined_response=combined_response)
    else:
        return jsonify({"Error": "Oops, sorry"})

    



if __name__ == '__main__':
      with app.app_context():
        db.create_all()
        app.run(port=7000)