from app import db


# the assessment class with its id, module, title, module code, release_day, deadline description and status
class Assessment(db.Model):
    __tablename__ = 'assessments'
    id = db.Column(db.Integer, primary_key=True)
    module = db.Column(db.String(100))
    title = db.Column(db.String(100))
    code = db.Column(db.String(10))
    release_day = db.Column(db.Date())      # the date that assessment begins
    deadline = db.Column(db.Date())
    description = db.Column(db.String(3000))
    status = db.Column(db.Boolean())    # there are two status, 1 is completed, 0 is uncompleted


# the plan class with plan_id, the date of a plan and its assessment id
class Plan(db.Model):
    __tablename__ = 'plan'
    plan_id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Date())
    work = db.Column(db.Integer())
