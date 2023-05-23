from extensions import db
from flask_login import UserMixin



class Manager(db.Model):

        sno = db.Column(db.Integer, primary_key=True)
        website = db.Column(db.String(200), nullable=False)
        emailid = db.Column(db.String(200), nullable=False)
        password = db.Column(db.String(500), nullable=False)

        def __repr__(self) -> str:
            return f"{self.sno} - {self.website}"


class User(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(520))
        email = db.Column(db.String(520), nullable=False)
        leetcode = db.Column(db.String(520), nullable=False)
        codechef = db.Column(db.String(520), nullable=False)
        codeforces = db.Column(db.String(520), nullable=False)
        password = db.Column(db.String(520), nullable=False)

        def __repr__(self):
            return '<User %r>' % self.email


