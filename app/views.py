from flask import request, flash, render_template, url_for, redirect
from app import app, db
import datetime
from .forms import CreateAssessment, SortForm, SearchForm
from .models import Assessment, Plan
from datetime import datetime
import calendar


def wrap_assessment(assessment):
    curr_time = datetime.now()
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
        assessment = Assessment.query.all()
        assessment_list = wrap_assessment(assessment)
    elif page == "Completed Assessment":
        assessment = Assessment.query.filter_by(status=1).all()
        assessment_list = wrap_assessment(assessment)
    else:
        assessment = Assessment.query.filter_by(status=0).all()
        assessment_list = wrap_assessment(assessment)
    return [page, assessment_list]


@app.route('/', methods=['GET', 'POST'])
def show():
    assessment = Assessment.query.all()
    assessment_list = wrap_assessment(assessment)
    form = SortForm()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        print(1)
        form = SortForm()
        method = form.method.data
        print(method)
        if method == "4":
            assessment = Assessment.query.order_by(Assessment.deadline).all()
        elif method == "3":
            assessment = Assessment.query.order_by(Assessment.release_day).all()
        elif method == "1":
            assessment = Assessment.query.order_by(Assessment.module).all()
        elif method == "2":
            assessment = Assessment.query.order_by(Assessment.title).all()
        else:
            assessment = Assessment.query.all()
        assessment_list = wrap_assessment(assessment)
        return render_template('show.html', assessments=assessment_list, PageTitle="All Assessments", form=form)
    return render_template('show.html', assessments=assessment_list, PageTitle="All Assessments", form=form)


@app.route('/new', methods=['GET', 'POST'])
def new():
    form = CreateAssessment()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        assessment = Assessment(module=form.module.data, title=form.title.data, code=form.code.data,
                                release_day=form.release_day.data, deadline=form.deadline.data,
                                description=form.description.data, status=0)
        try:
            db.session.add(assessment)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise error
        flash('Record was successfully added')
        return redirect(url_for("show"))
    return render_template('new.html', form=form, PageTitle="Add Assessments")


@app.route('/complete', methods=['GET', 'POST'])
def complete():
    assessment = Assessment.query.filter_by(status=1).all()
    assessment_list = wrap_assessment(assessment)
    form = SortForm()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        print(1)
        form = SortForm()
        method = form.method.data
        print(method)
        if method == "4":
            assessment = Assessment.query.filter_by(status=1).order_by(Assessment.deadline).all()
        elif method == "3":
            assessment = Assessment.query.filter_by(status=1).order_by(Assessment.release_day).all()
        elif method == "1":
            assessment = Assessment.query.filter_by(status=1).order_by(Assessment.module).all()
        elif method == "2":
            assessment = Assessment.query.filter_by(status=1).order_by(Assessment.title).all()
        else:
            assessment = Assessment.query.all()
        assessment_list = wrap_assessment(assessment)
        return render_template('show.html', assessments=assessment_list, PageTitle="Completed Assessment", form=form)
    return render_template('show.html', assessments=assessment_list, PageTitle="Completed Assessment", form=form)


@app.route('/uncompleted', methods=['GET', 'POST'])
def uncompleted():
    assessment = Assessment.query.filter_by(status=0).all()
    assessment_list = wrap_assessment(assessment)
    form = SortForm()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        print(1)
        form = SortForm()
        method = form.method.data
        print(method)
        if method == "4":
            assessment = Assessment.query.filter_by(status=0).order_by(Assessment.deadline).all()
        elif method == "3":
            assessment = Assessment.query.filter_by(status=0).order_by(Assessment.release_day).all()
        elif method == "1":
            assessment = Assessment.query.filter_by(status=0).order_by(Assessment.module).all()
        elif method == "2":
            assessment = Assessment.query.filter_by(status=0).order_by(Assessment.title).all()
        else:
            assessment = Assessment.query.filter_by(status=0).all()
        assessment_list = wrap_assessment(assessment)
        return render_template('show.html', assessments=assessment_list, PageTitle="Uncompleted Assessment", form=form)
    return render_template('show.html', assessments=assessment_list, PageTitle="Uncompleted Assessment", form=form)


@app.route('/mark', methods=['GET'])
def mark():
    id_num = request.args.get('id')
    page = request.args.get('page')
    status = (Assessment.query.filter_by(id=id_num).all())[0].status
    if status == 0:
        try:
            Assessment.query.filter_by(id=id_num).update({"status": 1})
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise error
    else:
        try:
            Assessment.query.filter_by(id=id_num).update({"status": 0})
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise error
    res = judge_page(page)
    assessment_list = res[1]
    page = res[0]
    if page == "All Assessments":
        return redirect(url_for("show"))
    elif page == "Completed Assessment":
        return redirect(url_for("complete"))
    elif page == "Uncompleted Assessment":
        return redirect(url_for("uncompleted"))
    elif page == "Search":
        return redirect(url_for("search"))
    else:
        form = SortForm()
        return render_template('show.html', assessments=assessment_list, PageTitle=page, form=form)


@app.route('/delete', methods=['GET'])
def delete():
    id_num = request.args.get('id')
    page = request.args.get('page')
    task = Assessment.query.filter_by(id=id_num).one()
    try:
        db.session.delete(task)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        raise error
    plan = Plan.query.filter_by(work=id_num).all()
    for k in plan:
        try:
            db.session.delete(k)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise error
    res = judge_page(page)
    assessment_list = res[1]
    page = res[0]
    if page == "All Assessments":
        return redirect(url_for("show"))
    elif page == "Completed Assessment":
        return redirect(url_for("complete"))
    elif page == "Uncompleted Assessment":
        return redirect(url_for("uncompleted"))
    elif page == "Search":
        return redirect(url_for("search"))
    else:
        form = SortForm()
        return render_template('show.html', assessments=assessment_list, PageTitle=page, form=form)


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    id_num = request.args.get('id')
    assessment = Assessment.query.filter_by(id=id_num).one()
    print(assessment.description)
    form = CreateAssessment()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        print(form.deadline.data)
        try:
            assessment.module = form.module.data
            assessment.title = form.title.data
            assessment.release_day = form.release_day.data
            assessment.deadline = form.deadline.data
            assessment.code = form.code.data
            assessment.description = form.description.data
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise error
        flash('Successfully edited assessment.')
        return redirect(url_for("show"))
    return render_template('edit.html', assessment=assessment, PageTitle="Edit", form=form)


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    num = 0
    assessment_list = []
    print(form.is_submitted())
    if form.is_submitted():
        module = form.module.data
        title = form.title.data
        release_day = form.release_day.data
        deadline = form.deadline.data
        if module == "20020930" and title == "20020930" and release_day == datetime(1902, 2, 2).date() \
                and deadline == datetime(1902, 2, 2).date():
            assessment = Assessment.query.all()
            assessment_list = wrap_assessment(assessment)
        elif module != "20020930" and title == "20020930" and release_day == datetime(1902, 2, 2).date() \
                and deadline == datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter_by(module=module).all()
            assessment_list = wrap_assessment(assessment)
        elif module == "20020930" and title != "20020930" and release_day == datetime(1902, 2, 2).date() \
                and deadline == datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter_by(title=title).all()
            assessment_list = wrap_assessment(assessment)
        elif module == "20020930" and title == "20020930" and release_day != datetime(1902, 2, 2).date() \
                and deadline == datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter_by(release_day=release_day).all()
            assessment_list = wrap_assessment(assessment)
        elif module == "20020930" and title == "20020930" and release_day == datetime(1902, 2, 2).date() \
                and deadline != datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter_by(deadline=deadline).all()
            assessment_list = wrap_assessment(assessment)
        elif module != "20020930" and title != "20020930" and release_day == datetime(1902, 2, 2).date() \
                and deadline == datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter_by(module=module, title=title).all()
            assessment_list = wrap_assessment(assessment)
        elif module != "20020930" and title == "20020930" and release_day != datetime(1902, 2, 2).date() \
                and deadline == datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter_by(module=module, release_day=release_day).all()
            assessment_list = wrap_assessment(assessment)
        elif module != "20020930" and title == "20020930" and release_day == datetime(1902, 2, 2).date() \
                and deadline != datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter_by(module=module, deadline=deadline).all()
            assessment_list = wrap_assessment(assessment)
        elif module == "20020930" and title != "20020930" and release_day != datetime(1902, 2, 2).date() \
                and deadline == datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter_by(title=title, release_day=release_day).all()
            assessment_list = wrap_assessment(assessment)
        elif module == "20020930" and title != "20020930" and release_day == datetime(1902, 2, 2).date() \
                and deadline != datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter_by(deadline=deadline, title=title).all()
            assessment_list = wrap_assessment(assessment)
        elif module == "20020930" and title == "20020930" and release_day != datetime(1902, 2, 2).date() \
                and deadline != datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter_by(deadline=deadline, release_day=release_day).all()
            assessment_list = wrap_assessment(assessment)
        elif module == "20020930" and title != "20020930" and release_day != datetime(1902, 2, 2).date() \
                and deadline != datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter_by(deadline=deadline, release_day=release_day, title=title).all()
            assessment_list = wrap_assessment(assessment)
        elif module != "20020930" and title == "20020930" and release_day != datetime(1902, 2, 2).date() \
                and deadline != datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter_by(deadline=deadline, release_day=release_day, module=module).all()
            assessment_list = wrap_assessment(assessment)
        elif module != "20020930" and title != "20020930" and release_day == datetime(1902, 2, 2).date() \
                and deadline != datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter_by(deadline=deadline, title=title, module=module).all()
            assessment_list = wrap_assessment(assessment)
        elif module != "20020930" and title != "20020930" and release_day != datetime(1902, 2, 2).date() \
                and deadline == datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter_by(title=title, module=module, release_day=release_day).all()
            assessment_list = wrap_assessment(assessment)
        else:
            assessment = Assessment.query.filter_by(deadline=deadline, release_day=release_day, title=title,
                                                    module=module).all()
            assessment_list = wrap_assessment(assessment)
        num = 0
        for k in assessment_list:
            num += 1
        form = SearchForm()
        return render_template('search.html', PageTitle="Search", form=form, assessments=assessment_list, num=num)
    return render_template('search.html', PageTitle="Search", form=form, num=num, assessments=assessment_list)


@app.route('/timeline', methods=['GET', 'POST'])
def timeline():
    plan = db.session.query(Plan.plan_id, Plan.day, Assessment.id, Assessment.module, Assessment.title,
                            Assessment.release_day, Assessment.deadline).join(Assessment, Plan.work == Assessment.id)\
        .order_by(Plan.day).all()
    curr_time = datetime.now()
    month = curr_time.month
    month_range = calendar.monthrange(curr_time.year, curr_time.month)[1]
    plan_list = []
    for i in range(month_range):
        plan_list.append([month_range-i, []])
    before = []
    this_month = datetime(curr_time.year, curr_time.month, 1)
    for i in plan:
        if (i.day - this_month.date()).days * 1 < 0:
            before.append(i)
        else:
            plan_list[30 - i.day.day][1].append(i)
    print(plan_list)
    return render_template('timeline.html', PageTitle='Time Line', plan=plan_list, month=month, before=before,
                           now=curr_time.day*1)


@app.route('/delete_plan', methods=['GET'])
def delete_plan():
    id = request.args.get('id')
    print(id)
    task = Plan.query.filter_by(plan_id=int(id)).one()
    print(task)
    try:
        db.session.delete(task)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        raise error
    return redirect(url_for('timeline'))


@app.route('/turn', methods=['GET'])
def turn():
    day = request.args.get('day')
    curr_time = datetime.now()
    day = datetime(curr_time.year, curr_time.month, int(day)).date()
    print(day)
    plan = Plan.query.filter_by(day=day).all()
    task = Assessment.query.all()
    print(plan)
    left_assessment = []
    num = []
    for i in plan:
        num.append(i.work)
    print(num)
    for k in task:
        if k.id not in num:
            left_assessment.append(k)
    print(left_assessment)
    return render_template('choose.html', PageTitle='Choose', assessments=left_assessment, day=day.day)


@app.route('/choose', methods=['GET'])
def choose():
    day = request.args.get('day_p')
    curr_time = datetime.now()
    day = datetime(curr_time.year, curr_time.month, int(day)).date()
    id = request.args.get('id')
    try:
        plan = Plan(day=day, work=id)
        db.session.add(plan)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        raise error
    return redirect(url_for('timeline'))
