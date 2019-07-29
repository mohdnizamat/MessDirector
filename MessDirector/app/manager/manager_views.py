from datetime import datetime
import pytz
from flask import Blueprint, redirect, render_template
from flask import request, url_for, flash, abort, Markup
from flask_user import current_user, login_required, roles_required
from sqlalchemy import extract, desc

from app import db, getlogger
from app.models.user_models import User, Attendance, Hostel, BillPending, HostelExpense
from app.forms import UserProfile, BillingSectionForm, BillPopulationForm,\
            AttendanceViewForm, AttendanceForm, UserProfileForm, UserBillSection, AttendanceViewFormManager
from app.users.user_views import attendance_total


manager_blueprint = Blueprint('manager', __name__, template_folder='templates')
tz_india = pytz.timezone('Asia/Kolkata')

logger=getlogger()

@roles_required('manager')
@manager_blueprint.route('/hostel_summary', methods=['GET', 'POST'])
def hostel_summary():
    '''
    Todays attendance views
    Total member list

    attendance_view_today function will return a tuple, which can be accessed with a[1] kind of referencing.
    attendance_view will have all these values. With, BreakFast, Lunchm Dinner and Full Order.

    '''
    users = User.query.filter_by(hostel_location=current_user.hostel_location)\
                    .filter_by(user_status="Active").all()
    pending_users = User.query.filter_by(hostel_location=current_user.hostel_location)\
                    .filter_by(user_status="Pending").all()
    alumni_users = User.query.filter_by(hostel_location=current_user.hostel_location)\
                    .filter_by(user_status="Alumni").all()
    attendance_view=attendance_view_today()

    pendinglist = BillPending.query.filter_by(bill_payment_status="Pending").all()

    total_amount_to_be_collected = []
    user_ids = []
    for user in users:
        user_ids.append(user.id)
    for bill_balance in pendinglist:
            if bill_balance.bill_user in user_ids:
                total_amount_to_be_collected.append(bill_balance.bill_total)
    total_amount_to_be_collected = sum(total_amount_to_be_collected)

    user_details = {}
    for user in users:
        phonenumber = user.phonenumber
        blood_group = user.blood_group
        try:
            bills = BillPending.query.filter_by(bill_user=user.id).all()
            if len(bills)>0:
                if bills[-1].bill_balance == 0.0 and \
                    bills[-1].bill_total == bills[-1].bill_payment:

                    bill_total = 0
                elif bills[-1].bill_balance == 0.0 and \
                    bills[-1].bill_total != bills[-1].bill_payment:
                    bill_total = bills[-1].bill_total
                else:
                    bill_total = bills[-1].bill_balance
            else:
                bill_total = 0

        except AttributeError:
            bill_total=0
        user_details[user] = [phonenumber, bill_total, blood_group]


    return render_template('manager/manager.html', titel='Hostel Summary',
                users=user_details, attendance=attendance_view,
                pending_users=pending_users, alumni_users=alumni_users,
                total_amount_to_be_collected=total_amount_to_be_collected)

@roles_required('manager')
@manager_blueprint.route('/edit_user/<id>', methods=['GET', 'POST'])
def edit_user(id):
#Below code can be used to get data, and update as well on the go.
    user_bill_form = UserBillSection()
    form = UserProfile()
    if request.method == 'GET':
        user = User.query.filter_by(id=id).first()
        form = UserProfile(obj=user)
        user_st = user.user_status
        billing_history = BillPending.query.filter_by(bill_user = user.id).all()
        return render_template('manager/manager_user_details_view.html', form=form,
                                billing_history=billing_history, st=user_st, user_bill_form=user_bill_form)

    elif dict(form.user_status.choices).get(form.user_status.data) == "Delete User":
        user = User.query.filter_by(id=id).first()
        db.session.delete(user)
        db.session.commit()
        flash('User Deleted !!!', 'danger')
    elif form.submit.data and form.validate_on_submit():
        user = User.query.filter_by(id=id).first()
        user.rent_amount = form.rent_amount.data
        user.joining_date = form.joining_date.data
        user.caution_deposit = form.caution_deposit.data
        user.user_status = dict(form.user_status.choices).get(form.user_status.data)
        db.session.commit()
        flash('Details Updated !!!', 'success')
    elif user_bill_form.submit_bill_details.data and user_bill_form.validate_on_submit():
        user = User.query.filter_by(id=id).first()
        bill_paid_amount = user_bill_form.paid_amount.data
        bill_paying_month = user_bill_form.bill_paying_month.data
        bill_payment = BillPending.query.filter_by(bill_user=user.id).filter_by(bill_date=user_bill_form.bill_paying_month.data).first()
        bill_balance = bill_payment.bill_total - bill_paid_amount
        bill_payment.bill_payment = bill_paid_amount
        bill_payment.bill_balance = bill_balance
        db.session.commit()
    return render_template('manager/manager_user_details_view.html',
                form=form, user_bill_form=user_bill_form)


        #bill_settlement(user, bill_paid_amount, bill_payment,bill_paying_month)
        #bill_payment and user is an object.

def attendance_view_today():
    total_users = User.query.filter_by(hostel_location=current_user.hostel_location).\
                                        filter_by(user_status="Active").all()
    total_users = len(total_users)

    attendance_today = Attendance.query.filter_by(attendance_hostel=current_user.hostel_location).\
                                        filter_by(attendance_date=datetime.now(tz_india).date()).all()
    #attendance_today =  len(attendance_today)-total_users

    #for finding each dinner, breakfast, Lunch
    Dinner=0
    Lunch=0
    BreakFast=0
    Full=0

    for i in range(len(attendance_today)):

        if attendance_today[i].attendance_time == "Dinner":
            Dinner+=1
        elif  attendance_today[i].attendance_time == "Lunch":
            Lunch+=1
        elif  attendance_today[i].attendance_time == "BreakFast":
            BreakFast+=1
        elif  attendance_today[i].attendance_time == "Full Day":
            Full+=1
    FullAttendanceTotal = total_users-Full
    BreakFastAttendance = total_users-Full-BreakFast
    LunchAttendance = total_users-Full-Lunch
    DinnerAttendance = total_users-Full-Dinner

    absent_list = {}
    #attendance[4]
    #{'Member1 Hebbal': ['Full', 11]}
    for i in range(len(attendance_today)):
        absent_list[(User.query.filter_by(hostel_location=current_user.hostel_location).filter_by(
        id=attendance_today[i].attendance_user).first())] = [attendance_today[i].attendance_time, attendance_today[i].attendance_reason ]



    return FullAttendanceTotal, BreakFastAttendance,\
            LunchAttendance, DinnerAttendance, absent_list

@roles_required('manager')
@manager_blueprint.route('/bill_section', methods=['GET', 'POST'])
def bill_section():
    '''
    Need a form to take month and year to calculate total points for that Month
    Another form form for calculating total Expense and Buffer amount

    For one user i.e for Hebbal manager, tested and verified the same.
    For Implementation:
    If data already feeded, then provision should be there to give warning to manager,
    cath those exception

    Can a form have two submit form?

    Total points shoulbe by considering peoples not in attendance list, since they have 30 attendance.

    '''
    bill_section_form = BillingSectionForm()
    billing_history_form = AttendanceViewForm()


    #Optimize this #For avoiding referencing early error, just initialing hostel expense class, month cannot be 81 at any case
    expense_data = HostelExpense.query.filter_by(
                    expense_bill_month=81).first()
    users = User.query.filter_by(hostel_location=current_user.hostel_location).filter_by(user_status="Active").all()
    #This for loop is for identifying the total points if user has marked no absence and still in Active list
    total_points =[]
    if bill_section_form.submit_bill_section.data and bill_section_form.validate_on_submit():
        for user in users:
            points = Attendance.query.filter_by(attendance_user=user.id).filter_by(
            attendance_hostel=current_user.hostel_location).filter(
            extract('month', Attendance.attendance_date)==bill_section_form.hostel_expense_month.data.month,
            extract('year', Attendance.attendance_date)==bill_section_form.hostel_expense_month.data.year).all()
            if not points:
                total_points.append(bill_section_form.hostel_working_days_per_month.data)
            elif points:
                user_monthly_points = []
                for point in range(len(points)):
                    user_monthly_points.append(float(points[point].attendance_point))
                total_points.append(bill_section_form.hostel_working_days_per_month.data-sum(user_monthly_points))



        monthly_expense = bill_section_form.hostel_monthly_expense.data
        monthly_buffer = bill_section_form.hostel_monthly_buffer.data
        common_expense = bill_section_form.hostel_common_expense.data
        hostel = current_user.hostel_location
        total_point=sum(total_points)
        daily_expense = (monthly_buffer+monthly_expense)/total_point

        expense_data = HostelExpense.query.filter_by(
                        expense_bill_month=bill_section_form.hostel_expense_month.data).filter_by(
                        expense_hostel=current_user.hostel_location
                        ).first()
        if expense_data:
            expense_data.expense_hostel = current_user.hostel_location
            expense_data.expense_bill_month = bill_section_form.hostel_expense_month.data
            expense_data.expense_monthly = monthly_expense
            expense_data.expense_monthly_buffer = monthly_buffer
            expense_data.expense_daily_expense = daily_expense
            expense_data.expense_common_per_head = common_expense
            expense_data.expense_total_points = total_point
            expense_data.expense_working_days_per_month = bill_section_form.hostel_working_days_per_month.data
            db.session.commit()
        else:
            expense_data = HostelExpense()
            expense_data.expense_hostel = current_user.hostel_location
            expense_data.expense_bill_month = bill_section_form.hostel_expense_month.data
            expense_data.expense_monthly = monthly_expense
            expense_data.expense_monthly_buffer = monthly_buffer
            expense_data.expense_daily_expense = daily_expense
            expense_data.expense_common_per_head = common_expense
            expense_data.expense_total_points = total_point
            expense_data.expense_working_days_per_month = bill_section_form.hostel_working_days_per_month.data
            db.session.add(expense_data)
            db.session.commit()
        bill_population(daily_expense, common_expense, bill_section_form)

    elif billing_history_form.submit1.data and billing_history_form.validate_on_submit():
        expense_data = HostelExpense.query.filter_by(
                        expense_bill_month=billing_history_form.attendance_view_date.data).filter_by(
                        expense_hostel=current_user.hostel_location
                        ).first()
        return render_template('manager/billing.html', bill_section_form=bill_section_form,
                                                       billing_history_form=billing_history_form,
                                                       expense_data=expense_data)

    return render_template('manager/billing.html', bill_section_form=bill_section_form,
                                                   billing_history_form=billing_history_form,
                                                   expense_data=expense_data)





def bill_population(hostel_daily_expense, common_expense, form):
    '''
    Above we have which hostel is present in the picture.
    Now, take all the users of that particual hostel,
    for each user, take attendance total, mutliply with hostel's hostel_daily_expense and add to databse.
    Here, catch exceptions of adding again

    When no absense, attendnaceview will not catch anything, so provision should be there to charge full amount

    If manager resubmit the data again. it should be modified in the database for all users
    '''

    #bill_population_form = BillPopulationForm()
    attendanceviewform = AttendanceViewForm()
    users = User.query.filter_by(hostel_location=current_user.hostel_location).filter_by(
                        user_status="Active").all()
    for user in users:
        attendanceview = Attendance.query.filter_by(attendance_user=user.id).filter_by(
        attendance_hostel=current_user.hostel_location).filter(
        extract('month', Attendance.attendance_date)==form.hostel_expense_month.data.month,
        extract('year', Attendance.attendance_date)==form.hostel_expense_month.data.year).all()
        if not attendanceview:
            monthlytotal_attendance = form.hostel_working_days_per_month.data
        elif attendanceview:
            monthlytotal_attendance = attendance_total_manager(attendanceview,form,user)
        monthlytotal_mess_bill = monthlytotal_attendance*hostel_daily_expense+common_expense
        bills=BillPending.query.filter_by(bill_date=form.hostel_expense_month.data).filter_by(bill_user=user.id).first()
        if bills:
            bills.bill_date = form.hostel_expense_month.data
            bills.bill_user = user.id
            if (user.joining_date.month, user.joining_date.year) == (form.hostel_expense_month.data.month,
            form.hostel_expense_month.data.year) and user.joining_date.day > 15:
                bills.bill_amount_current_date = monthlytotal_mess_bill+user.rent_amount/2
            else:
                bills.bill_amount_current_date = monthlytotal_mess_bill+user.rent_amount
            last_month_balance = BillPending.query.\
                                order_by(desc(BillPending.id)).filter_by(bill_user=user.id).first()
            if last_month_balance:
                bills.bill_total = bills.bill_amount_current_date + last_month_balance.bill_balance
            else:
                bills.bill_total = bills.bill_amount_current_date
            db.session.commit()
        elif not bills:

            bill = BillPending()
            bill.bill_date = form.hostel_expense_month.data
            bill.bill_user = user.id
            if (user.joining_date.month, user.joining_date.year) == (form.hostel_expense_month.data.month,
             form.hostel_expense_month.data.year) and user.joining_date.day > 15:
                bill.bill_amount_current_date = monthlytotal_mess_bill+user.rent_amount/2
            else:
                bill.bill_amount_current_date = monthlytotal_mess_bill+user.rent_amount
            last_month_balance = BillPending.query.\
                                order_by(desc(BillPending.id)).filter_by(bill_user=user.id).first()
            if last_month_balance:
                bill.bill_total = bill.bill_amount_current_date + last_month_balance.bill_balance
            else:
                bill.bill_total = bill.bill_amount_current_date
            db.session.add(bill)
            db.session.commit()

def attendance_total_manager(attendanceview,form,user):
    #[Nizam][July-03]Number of working days should be taken from hostel instead of default 30
    attendanceview=attendanceview
    total=[]
    for i in range(len(attendanceview)):
        total.append(float(attendanceview[i].attendance_point))

    working_days = HostelExpense.query.filter_by(expense_hostel=user.hostel_location).\
    filter_by(expense_bill_month=form.hostel_expense_month.data.month).first()
    if working_days:
        monthlytotal=working_days.expense_working_days_per_month-sum(total)
    elif not working_days:
        monthlytotal=30-sum(total)

    if (user.joining_date.month, user.joining_date.year) == (form.hostel_expense_month.data.month, form.hostel_expense_month.data.year):
        monthlytotal = monthlytotal-int(user.joining_date.day)

    return monthlytotal




@roles_required('manager')
@manager_blueprint.route('/edit_attendance/<user_id>', methods=['GET', 'POST'])
def edit_attendance(user_id):
    form = AttendanceForm()
    attendanceviewform = AttendanceViewForm()
    if form.submit.data :
        if Attendance.query.filter_by(attendance_date=form.absend_date.data).filter_by(attendance_user=user_id).first():
            attendance_mark = Attendance.query.filter_by(attendance_date=form.absend_date.data).filter_by(attendance_user=user_id).first()
            if form.absend_time.data == '0':
                db.session.delete(attendance_mark)
                db.session.commit()
                flash('Attendace Deleted !!!', 'danger')
            else:
                attendance_mark = Attendance.query.filter_by(attendance_date=form.absend_date.data).filter_by(attendance_user=user_id).first()
                attendance_mark.attendance_point =  form.absend_time.data
                attendance_mark.attendance_time = dict(form.absend_time.choices).get(form.absend_time.data)
                attendance_mark.attendance_user = current_user.id
                attendance_mark.attendance_hostel = current_user.hostel_location
                db.session.commit()
                flash('Attendance Updated', 'success')
    return render_template('manager/edit_attendance.html',title='Submit Poster Details',form=form)

@roles_required('manager')
@manager_blueprint.route('/attendance_section', methods=['GET', 'POST'])
def attendance_section():
    form = AttendanceViewFormManager()
    total_users = 0
    attendance_day=[]
    if form.validate_on_submit():
        attendance_day = Attendance.query.filter_by(attendance_hostel=current_user.hostel_location).\
                                        filter_by(attendance_date=form.attendance_view.data).all()
        total_users = User.query.filter_by(hostel_location=current_user.hostel_location).\
                                            filter_by(user_status="Active").all()
        total_users = len(total_users)
    #attendance_today =  len(attendance_today)-total_users

    #for finding each dinner, breakfast, Lunch
    Dinner=0
    Lunch=0
    BreakFast=0
    Full=0

    for i in range(len(attendance_day)):

        if attendance_day[i].attendance_time == "Dinner":
            Dinner+=1
        elif  attendance_day[i].attendance_time == "Lunch":
            Lunch+=1
        elif  attendance_day[i].attendance_time == "BreakFast":
            BreakFast+=1
        elif  attendance_day[i].attendance_time == "Full Day":
            Full+=1
    FullAttendanceTotal = total_users-Full
    BreakFastAttendance = total_users-Full-BreakFast
    LunchAttendance = total_users-Full-Lunch
    DinnerAttendance = total_users-Full-Dinner

    absent_list = {}
    #attendance[4]
    #{'Member1 Hebbal': ['Full', 11]}
    for i in range(len(attendance_day)):
        absent_list[(User.query.filter_by(hostel_location=current_user.hostel_location).filter_by(
        id=attendance_day[i].attendance_user).first())] = [attendance_day[i].attendance_time, attendance_day[i].attendance_reason ]


    return render_template('manager/attendance_section.html', form=form,
                            BreakFastAttendance=BreakFastAttendance,
                            LunchAttendance=LunchAttendance,
                            DinnerAttendance=DinnerAttendance,
                            absent_list=absent_list)
