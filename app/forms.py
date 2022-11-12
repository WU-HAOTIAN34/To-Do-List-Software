from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length


class CreateAssessment(FlaskForm):
    module = StringField('module', validators=[DataRequired(), Length(max=100)])
    title = StringField('title', validators=[DataRequired(), Length(max=100)])
    code = StringField('code', validators=[DataRequired(), Length(max=10)])
    release_day = DateField('release_day', validators=[DataRequired()])
    deadline = DateField('deadline', validators=[DataRequired()])
    description = TextAreaField('description', validators=[DataRequired(), Length(max=3000)])


class SortForm(FlaskForm):
    method = SelectField('Sorted by', choices=[(0, "None"), (1, 'Module'), (2, 'Title'), (3, 'Release time'),
                                               (4, 'Deadline')], validators=[DataRequired()])
    submit = SubmitField('Sort')


class SearchForm(FlaskForm):
    module = StringField('module', validators=[DataRequired(), Length(max=100)])
    title = StringField('title', validators=[DataRequired(), Length(max=100)])
    release_day = DateField('release_day', validators=[DataRequired()])
    deadline = DateField('deadline', validators=[DataRequired()])
