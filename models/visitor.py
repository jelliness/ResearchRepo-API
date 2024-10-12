from . import db

class Visitor(db.Model):
    __tablename__ = 'visitor'
    visitor_id = db.Column(db.String(15), db.ForeignKey('account.user_id'), primary_key=True)
    institution = db.Column(db.String(200))
    first_name = db.Column(db.String(30))
    middle_name = db.Column(db.String(2))
    last_name = db.Column(db.String(30))
    suffix = db.Column(db.String(10))
    reason = db.Column(db.String(100))