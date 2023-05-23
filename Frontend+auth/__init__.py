from distutils.log import debug
from flask import Flask, render_template, flash, request,redirect,session
from flask_sqlalchemy import SQLAlchemy
import joblib
from extensions import db,login_manager
from model import User,Manager
from flask_login import login_required
import requests



def create_app():
    app = Flask(__name__)

    app.secret_key = "super secret key"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///manager.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # db = SQLAlchemy(app)
    db.init_app(app)
    # For managing sessions during login
    login_manager.init_app(app)
    from auth import auth

    app.register_blueprint(auth)

    


    @login_manager.user_loader
    def load_user(user_id):
        # using the user id as primary key as id for session
        return User.query.get(int(user_id))


    @app.route('/')
    def homepage():
       return redirect("/login")

    @app.route('/contest', methods=['GET', 'POST'])
    def contest():
            response = requests.get('https://kontests.net/api/v1/all')
            if response.status_code == 200:
                events = response.json()
            else:
                events = []  # Empty list if API request fails
            return render_template('contest.html',events=events)

    @login_required
    @app.route('/manage', methods=['GET', 'POST'])
    def manager() :
        email = session['user']
        alldata = Manager.query.filter_by(emailid=email).all()

        if request.method == "POST":
            website = request.form['website']
            email = request.form['email']
            password = request.form['password']
            
            manageinstance=Manager(website=website,emailid=email,password=password)
            db.session.add(manageinstance)
            db.session.commit()
            email = session['user']
            alldata = Manager.query.filter_by(emailid=email).all()

            print(website)

            return render_template('manager.html', data=alldata,value=1)
        
        else:
            
            return render_template('manager.html',value=1,data=alldata)

   
    return app
   
            

if __name__ == "__main__":
    app=create_app()
    app.app_context().push()

    app.run(debug=True)

