from app import db


class Assessment(db.Model):
    __tablename__ = 'assessments'
    id = db.Column(db.Integer, primary_key=True)
    module = db.Column(db.String(100))
    title = db.Column(db.String(100))
    code = db.Column(db.String(10))
    release_day = db.Column(db.Date())
    deadline = db.Column(db.Date())
    description = db.Column(db.String(500))
    status = db.Column(db.Boolean())
    submit_times = db.Column(db.Integer())
