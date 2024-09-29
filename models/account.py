from . import db
from sqlalchemy import text

class Account(db.Model):
    __tablename__ = 'account'
    user_id = db.Column(db.String(15), primary_key=True)
    live_account = db.Column(db.String(80))
    user_pw = db.Column(db.String(64))  # Store the hashed password
    acc_status = db.Column(db.String(20), server_default=text("'ACTIVATED'"))
    role_id = db.Column(db.String(2), db.ForeignKey('roles.role_id'))
    role = db.relationship('Role', backref=db.backref('accounts', lazy=True))
