from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length


class CreateAssessment(FlaskForm):
    module = StringField('module', validators=[DataRequired(), Length(max=100)])
    title = StringField('title', validators=[DataRequired(), Length(max=100)])
    code = StringField('code', validators=[DataRequired(), Length(max=10)])
    release_day = DateField('release_day', validators=[DataRequired()])
    deadline = DateField('deadline', validators=[DataRequired()])
    description = TextAreaField('description', validators=[DataRequired(), Length(max=500)])