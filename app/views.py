from flask import request, flash, url_for, redirect, render_template
from app import app, db
import datetime
from .forms import CreateAssessment
from .models import assessments


def wrap_assessment(assessment):
    curr_time = datetime.datetime.now()
    res = []
    for i in assessment:
        left_time = (i.deadline - curr_time.date()).days
        all_time = (i.deadline - i.release_day).days
        num = left_time * 10 / all_time
        if num <= 0:
            num = 0
        elif num <= 1:
            num = 1
        elif 9 <= num < 10:
            num = 9
        elif num == 10:
            num = 10
        else:
            num = int(round(num))
        day = []
        for j in range(10):
            if 9 - j < num:
                day.append(1)
            else:
                day.append(0)
        if left_time < 0:
            left_time = 0
        res.append([i, num, day, left_time])
    return res


def judge_page(page):
    if page == "All Assessments":
        assessment = assessments.query.all()
        assessment_list = wrap_assessment(assessment)
    elif page == "Completed Assessment":
        assessment = assessments.query.filter_by(status=1).all()
        assessment_list = wrap_assessment(assessment)
    else:
        assessment = assessments.query.filter_by(status=0).all()
        assessment_list = wrap_assessment(assessment)
    return [page, assessment_list]


@app.route('/')
def show():
    assessment = assessments.query.all()
    assessment_list = wrap_assessment(assessment)
    return render_template('show.html', assessments=assessment_list, PageTitle="All Assessments")


@app.route('/new', methods=['GET', 'POST'])
def new():
    form = CreateAssessment()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        assessment = assessments(module=form.module.data, title=form.title.data, code=form.code.data,
                                 release_day=form.release_day.data, deadline=form.deadline.data,
                                 description=form.description.data, status=0, submit_times=0)
        db.session.add(assessment)
        db.session.commit()
        flash('Record was successfully added')
        assessment = assessments.query.all()
        assessment_list = wrap_assessment(assessment)
        return render_template('show.html', assessments=assessment_list, PageTitle="All Assessments")
    return render_template('new.html', form=form, PageTitle="Add Assessments")


@app.route('/complete')
def complete():
    assessment = assessments.query.filter_by(status=1).all()
    assessment_list = wrap_assessment(assessment)
    return render_template('show.html', assessments=assessment_list, PageTitle="Completed Assessment")


@app.route('/uncompleted')
def uncompleted():
    assessment = assessments.query.filter_by(status=0).all()
    assessment_list = wrap_assessment(assessment)
    return render_template('show.html', assessments=assessment_list, PageTitle="Uncompleted Assessment")


@app.route('/mark', methods=['GET'])
def mark():
    id_num = request.args.get('id')
    page = request.args.get('page')
    status = (assessments.query.filter_by(id=id_num).all())[0].status
    if status == 0:
        assessments.query.filter_by(id=id_num).update({"status": 1})
        db.session.commit()
    else:
        assessments.query.filter_by(id=id_num).update({"status": 0})
        db.session.commit()
    res = judge_page(page)
    assessment_list = res[1]
    page = res[0]
    return render_template('show.html', assessments=assessment_list, PageTitle=page)


@app.route('/delete', methods=['GET'])
def delete():
    id_num = request.args.get('id')
    page = request.args.get('page')
    task = assessments.query.filter_by(id=id_num).one()
    db.session.delete(task)
    db.session.commit()
    res = judge_page(page)
    assessment_list = res[1]
    page = res[0]
    return render_template('show.html', assessments=assessment_list, PageTitle=page)


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    id_num = request.args.get('id')
    assessment = assessments.query.filter_by(id=id_num).one()
    print(assessment.description)
    form = CreateAssessment()
    if form.validate_on_submit():
        assessment.module = form.module.data
        assessment.title = form.title.data
        assessment.release_day = form.release_day.data
        assessment.deadline = form.deadline.data
        assessment.code = form.code.data
        assessment.description = form.description.data
        db.session.commit()
        flash('Successfully edited assessment.')
        assessment = assessments.query.all()
        assessment_list = wrap_assessment(assessment)
        return render_template('show.html', assessments=assessment_list, PageTitle="All Assessments")
    return render_template('edit.html', assessment=assessment, PageTitle="Edit", form=form,)
