from flask import request, flash, render_template, url_for, redirect
from app import app, db
import datetime
from .forms import CreateAssessment, SortForm, SearchForm
from .models import Assessment, Plan
from datetime import datetime
import calendar


# used to obtain the planning schedule
@app.route('/timeline', methods=['GET', 'POST'])
def timeline():
    # joint searching plan table and assessment table with plan.work==assessment.id
    plan = db.session.query(Plan.plan_id, Plan.day, Assessment.id, Assessment.module, Assessment.title,
                            Assessment.release_day, Assessment.deadline).join(Assessment, Plan.work == Assessment.id)\
        .order_by(Plan.day).all()
    # obtain the current day and the number of days in this month
    curr_time = datetime.now()
    month = curr_time.month
    month_range = calendar.monthrange(curr_time.year, curr_time.month)[1]
    # the plan_list: [[day (from the largest day), [plans in this day, ...]],...]
    plan_list = []
    for i in range(month_range):
        plan_list.append([month_range-i, []])
    before = []
    this_month = datetime(curr_time.year, curr_time.month, 1)
    # search the plans before this month and add other assessment to the correct day
    for i in plan:
        if (i.day - this_month.date()).days * 1 < 0:
            before.append(i)
        else:
            plan_list[30 - i.day.day][1].append(i)
    print(plan_list)
    return render_template('timeline.html', PageTitle='Time Line', plan=plan_list, month=month, before=before,
                           now=curr_time.day*1)


# used to delete a plan
@app.route('/delete_plan', methods=['GET'])
def delete_plan():
    # obtain the id of a certain plan and quarry it
    id = request.args.get('id')
    print(id)
    task = Plan.query.filter_by(plan_id=int(id)).one()
    print(task)
    # try to delete it
    try:
        db.session.delete(task)
        db.session.commit()
    # if there are errors roll back
    except Exception as error:
        db.session.rollback()
        raise error
    return redirect(url_for('timeline'))


# used to obtain the assessments which are not plans in a certain day
@app.route('/turn', methods=['GET'])
def turn():
    # obtain the date and month to create a datetime object
    day = request.args.get('day')
    curr_time = datetime.now()
    day = datetime(curr_time.year, curr_time.month, int(day)).date()
    print(day)
    # quarry all plans in this day and all assessments
    plan = Plan.query.filter_by(day=day).all()
    task = Assessment.query.all()
    print(plan)
    left_assessment = []
    num = []
    for i in plan:
        num.append(i.work)
    print(num)
    # quarry the assessments not in the plans and show them
    for k in task:
        if k.id not in num:
            left_assessment.append(k)
    print(left_assessment)
    return render_template('choose.html', PageTitle='Choose', assessments=left_assessment, day=day.day)


# used to add a plan
@app.route('/choose', methods=['GET'])
def choose():
    # get the date and id of an assessment
    day = request.args.get('day_p')
    curr_time = datetime.now()
    day = datetime(curr_time.year, curr_time.month, int(day)).date()
    id = request.args.get('id')
    # try to add a data
    try:
        plan = Plan(day=day, work=id)
        db.session.add(plan)
        db.session.commit()
    # if there are errors roll back
    except Exception as error:
        db.session.rollback()
        raise error
    return redirect(url_for('timeline'))


# the function used to wrap the assessment list
# [[assessment object, the percentage of remaining day, a list contains 0,1, remaining days]...]
def wrap_assessment(assessment):
    curr_time = datetime.now()
    res = []
    for i in assessment:
        # obtain the remaining days
        left_time = (i.deadline - curr_time.date()).days
        all_time = (i.deadline - i.release_day).days
        # obtain the remaining ratio
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
        # a list represents the remaining ratio
        for j in range(10):
            if 9 - j < num:
                day.append(1)
            else:
                day.append(0)
        if left_time < 0:
            left_time = 0
        res.append([i, num, day, left_time])
    return res


# the function used to judge which page to return
def judge_page(page):
    if page == "All Assessments":
        # if all assessments quarry all
        assessment = Assessment.query.all()
        assessment_list = wrap_assessment(assessment)
    elif page == "Completed Assessment":
        # if completed assessments quarry status=1
        assessment = Assessment.query.filter_by(status=1).all()
        assessment_list = wrap_assessment(assessment)
    else:
        # if uncompleted assessments quarry status=0
        assessment = Assessment.query.filter_by(status=0).all()
        assessment_list = wrap_assessment(assessment)
    return [page, assessment_list]


# represent all assessments
@app.route('/', methods=['GET', 'POST'])
def show():
    # quarry all of assessments
    assessment = Assessment.query.all()
    assessment_list = wrap_assessment(assessment)
    # create the sorting form
    form = SortForm()
    print(form.validate_on_submit())
    # the operation after submitting the form
    if form.validate_on_submit():
        form = SortForm()
        method = form.method.data
        # judge sorting method deadline, release_day, module, title or none
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
        # back to all assessments page with the sorted list
        return render_template('show.html', assessments=assessment_list, PageTitle="All Assessments", form=form)
    return render_template('show.html', assessments=assessment_list, PageTitle="All Assessments", form=form)


# used to new an assessments
@app.route('/new', methods=['GET', 'POST'])
def new():
    # create the creation form
    form = CreateAssessment()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        # new an assessment object by obtaining the form data
        assessment = Assessment(module=form.module.data, title=form.title.data, code=form.code.data,
                                release_day=form.release_day.data, deadline=form.deadline.data,
                                description=form.description.data, status=0)
        # try to submit data to the database
        try:
            db.session.add(assessment)
            db.session.commit()
        # if there are errors, roll back and raise errors
        except Exception as error:
            db.session.rollback()
            raise error
        flash('Record was successfully added')
        # back the all assessments page
        return redirect(url_for("show"))
    return render_template('new.html', form=form, PageTitle="Add Assessments")


# represent the completed assessments
@app.route('/complete', methods=['GET', 'POST'])
def complete():
    # quarry the assessments that status is completed(=1)
    assessment = Assessment.query.filter_by(status=1).all()
    assessment_list = wrap_assessment(assessment)
    # create sorting form
    form = SortForm()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        form = SortForm()
        method = form.method.data
        # judge sorting method deadline, release_day, module, title or none
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
        # back to completed assessments page with the sorted list
        return render_template('show.html', assessments=assessment_list, PageTitle="Completed Assessment", form=form)
    return render_template('show.html', assessments=assessment_list, PageTitle="Completed Assessment", form=form)


# back to all assessments page with the sorted list
@app.route('/uncompleted', methods=['GET', 'POST'])
def uncompleted():
    # quarry the assessments that status is uncompleted(=0)
    assessment = Assessment.query.filter_by(status=0).all()
    assessment_list = wrap_assessment(assessment)
    # create sorting form
    form = SortForm()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        form = SortForm()
        method = form.method.data
        # judge sorting method deadline, release_day, module, title or none
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
        # back to completed assessments page with the sorted list
        return render_template('show.html', assessments=assessment_list, PageTitle="Uncompleted Assessment", form=form)
    return render_template('show.html', assessments=assessment_list, PageTitle="Uncompleted Assessment", form=form)


# used to change the status of a certain assessment
@app.route('/mark', methods=['GET'])
def mark():
    # obtain the id of a certain assessment and quarry it
    id_num = request.args.get('id')
    page = request.args.get('page')
    status = (Assessment.query.filter_by(id=id_num).all())[0].status
    # convert 1 to 0 or convert 0 to 1
    if status == 0:
        try:
            Assessment.query.filter_by(id=id_num).update({"status": 1})
            db.session.commit()
        # if there are errors roll back
        except Exception as error:
            db.session.rollback()
            raise error
    else:
        try:
            Assessment.query.filter_by(id=id_num).update({"status": 0})
            db.session.commit()
        # if there are errors roll back
        except Exception as error:
            db.session.rollback()
            raise error
    # judge which page to return and redirect
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
        # otherwise, get the assessment list and return to the page by page title
        form = SortForm()
        return render_template('show.html', assessments=assessment_list, PageTitle=page, form=form)


# used to delete a certain assessment
@app.route('/delete', methods=['GET'])
def delete():
    # obtain the id of a certain assessment and quarry it
    id_num = request.args.get('id')
    page = request.args.get('page')
    task = Assessment.query.filter_by(id=id_num).one()
    # submit the deleting
    try:
        db.session.delete(task)
        db.session.commit()
    # if there are errors roll back
    except Exception as error:
        db.session.rollback()
        raise error
    # if there are some plans which contain this assessment, delete them
    # quarry the plan list
    plan = Plan.query.filter_by(work=id_num).all()
    # delete each plan
    for k in plan:
        try:
            db.session.delete(k)
            db.session.commit()
        # if there are errors roll back
        except Exception as error:
            db.session.rollback()
            raise error
    # judge which page to return and redirect
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
    # otherwise, get the assessment list and return to the page by page title
    else:
        form = SortForm()
        return render_template('show.html', assessments=assessment_list, PageTitle=page, form=form)


# used to edit a certain assessment
@app.route('/edit', methods=['GET', 'POST'])
def edit():
    # obtain the id of a certain assessment and quarry it
    id_num = request.args.get('id')
    assessment = Assessment.query.filter_by(id=id_num).one()
    print(assessment.description)
    # create a creation form
    form = CreateAssessment()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        print(form.deadline.data)
        # obtain the data after edition and submit to the database
        try:
            assessment.module = form.module.data
            assessment.title = form.title.data
            assessment.release_day = form.release_day.data
            assessment.deadline = form.deadline.data
            assessment.code = form.code.data
            assessment.description = form.description.data
            db.session.commit()
        # if there are errors roll back
        except Exception as error:
            db.session.rollback()
            raise error
        flash('Successfully edited assessment.')
        # return to the all assessments page
        return redirect(url_for("show"))
    return render_template('edit.html', assessment=assessment, PageTitle="Edit", form=form)


# used to search the assessments which are fit the conditions
@app.route('/search', methods=['GET', 'POST'])
def search():
    # create the searching form
    form = SearchForm()
    num = 0
    assessment_list = []
    print(form.is_submitted())
    if form.is_submitted():
        # obtain the searching conditions: module, title, release_day and deadline
        module = form.module.data
        title = form.title.data
        # ambiguous conditions of module and title
        module1 = "%"+form.module.data+"%"
        title1 = "%"+form.title.data+"%"
        release_day = form.release_day.data
        deadline = form.deadline.data
        # obtain the consist of the searching conditions
        # none
        if module == "20020930" and title == "20020930" and release_day == datetime(1902, 2, 2).date() \
                and deadline == datetime(1902, 2, 2).date():
            assessment = Assessment.query.all()
            assessment_list = wrap_assessment(assessment)
        # module
        elif module != "20020930" and title == "20020930" and release_day == datetime(1902, 2, 2).date() \
                and deadline == datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter(Assessment.module.like(module1)).all()
            assessment_list = wrap_assessment(assessment)
        # title
        elif module == "20020930" and title != "20020930" and release_day == datetime(1902, 2, 2).date() \
                and deadline == datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter(Assessment.title.like(title1)).all()
            assessment_list = wrap_assessment(assessment)
        # release_day
        elif module == "20020930" and title == "20020930" and release_day != datetime(1902, 2, 2).date() \
                and deadline == datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter_by(release_day=release_day).all()
            assessment_list = wrap_assessment(assessment)
        # deadline
        elif module == "20020930" and title == "20020930" and release_day == datetime(1902, 2, 2).date() \
                and deadline != datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter_by(deadline=deadline).all()
            assessment_list = wrap_assessment(assessment)
        # module and title
        elif module != "20020930" and title != "20020930" and release_day == datetime(1902, 2, 2).date() \
                and deadline == datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter(Assessment.module.like(module1), Assessment.title.like(title1)).all()
            assessment_list = wrap_assessment(assessment)
        # module release_day
        elif module != "20020930" and title == "20020930" and release_day != datetime(1902, 2, 2).date() \
                and deadline == datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter(Assessment.module.like(module1),
                                                 Assessment.release_day == release_day).all()
            assessment_list = wrap_assessment(assessment)
        # module and deadline
        elif module != "20020930" and title == "20020930" and release_day == datetime(1902, 2, 2).date() \
                and deadline != datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter(Assessment.module.like(module1), Assessment.deadline == deadline).all()
            assessment_list = wrap_assessment(assessment)
        # title and release_day
        elif module == "20020930" and title != "20020930" and release_day != datetime(1902, 2, 2).date() \
                and deadline == datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter(Assessment.title.like(title1),
                                                 Assessment.release_day == release_day).all()
            assessment_list = wrap_assessment(assessment)
        # title and deadline
        elif module == "20020930" and title != "20020930" and release_day == datetime(1902, 2, 2).date() \
                and deadline != datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter(Assessment.deadline == deadline, Assessment.title.like(title1)).all()
            assessment_list = wrap_assessment(assessment)
        # release_day and deadline
        elif module == "20020930" and title == "20020930" and release_day != datetime(1902, 2, 2).date() \
                and deadline != datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter(Assessment.deadline == deadline,
                                                 Assessment.release_day == release_day).all()
            assessment_list = wrap_assessment(assessment)
        # title, release_day and deadline
        elif module == "20020930" and title != "20020930" and release_day != datetime(1902, 2, 2).date() \
                and deadline != datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter(Assessment.deadline == deadline, Assessment.release_day == release_day,
                                                 Assessment.title.like(title1)).all()
            assessment_list = wrap_assessment(assessment)
        # module, release_day and deadline
        elif module != "20020930" and title == "20020930" and release_day != datetime(1902, 2, 2).date() \
                and deadline != datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter(Assessment.deadline == deadline, Assessment.release_day == release_day,
                                                 Assessment.module.like(module1)).all()
            assessment_list = wrap_assessment(assessment)
        # module, title and deadline
        elif module != "20020930" and title != "20020930" and release_day == datetime(1902, 2, 2).date() \
                and deadline != datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter(Assessment.deadline == deadline, Assessment.module.like(module1),
                                                 Assessment.title.like(title1)).all()
            assessment_list = wrap_assessment(assessment)
        # module, title and release_day
        elif module != "20020930" and title != "20020930" and release_day != datetime(1902, 2, 2).date() \
                and deadline == datetime(1902, 2, 2).date():
            assessment = Assessment.query.filter_by(Assessment.module.like(module1), Assessment.title.like(title1),
                                                    Assessment.release_day == release_day).all()
            assessment_list = wrap_assessment(assessment)
        # all conditions
        else:
            assessment = Assessment.query.filter_by(Assessment.module.like(module1), Assessment.title.like(title1),
                                                    Assessment.release_day == release_day,
                                                    Assessment.deadline == deadline).all()
            assessment_list = wrap_assessment(assessment)
        # the number of the searching results
        num = 0
        for k in assessment_list:
            num += 1
        form = SearchForm()
        return render_template('search.html', PageTitle="Search", form=form, assessments=assessment_list, num=num)
    return render_template('search.html', PageTitle="Search", form=form, num=num, assessments=assessment_list)
