from datetime import datetime
import pytz
from flask import Blueprint, redirect, render_template
from flask import request, url_for, flash, abort, Markup
from flask_user import current_user, login_required, roles_required
from sqlalchemy import extract

from app import db, getlogger
from app.models.user_models import Attendance, Hostel, HostelExpense, BillPending
from app.forms import AttendanceForm, AttendanceViewForm, UserProfileForm
#from app.forms import AttendanceForm


user_blueprint = Blueprint('users', __name__, template_folder='templates')
tz_india = pytz.timezone('Asia/Kolkata')

logger = getlogger()



'''@user_blueprint.route('/profile')
@login_required  # Limits access to authenticated users
def user_page():
    return render_template('users/user1_page.html')'''

@user_blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
#@roles_required('manager')
def user_page():
    if current_user.user_status == "Pending" and current_user.has_roles('manager'):
        return redirect(url_for('manager.hostel_summary'))

    elif current_user.user_status == "Active":

        if (current_user.joining_date.month, current_user.joining_date.year) == (datetime.now(tz_india).month, datetime.now(tz_india).year):
            if current_user.joining_date.day > 15:
                rent = current_user.rent_amount/2
            else:
                rent = current_user.rent_amount
        else:
            rent = current_user.rent_amount
        form = AttendanceForm()
        attendanceviewform = AttendanceViewForm()
        if form.submit.data and form.validate_on_submit():
            if form.absend_date.data < datetime.now(tz_india).date():
                flash('You cannot mark attendance for dates alreay passed', 'info')
            elif Attendance.query.filter_by(attendance_date=form.absend_date.data).filter_by(attendance_user=current_user.id).first():
                if form.absend_time.data == '0':
                    attendance_mark = Attendance.query.filter_by(attendance_date=form.absend_date.data)\
                                        .filter_by(attendance_user=current_user.id).filter_by(attendance_hostel=current_user.hostel_location).first()
                    db.session.delete(attendance_mark)
                    db.session.commit()
                    flash('Attendace Deleted !!!', 'danger')
                else:
                    attendance_mark = Attendance.query.filter_by(attendance_date=form.absend_date.data).filter_by(attendance_user=current_user.id).first()
                    attendance_mark.attendance_point =  form.absend_time.data
                    attendance_mark.attendance_time = dict(form.absend_time.choices).get(form.absend_time.data)
                    attendance_mark.attendance_reason = dict(form.absend_reason.choices).get(form.absend_reason.data)
                    attendance_mark.attendance_user = current_user.id
                    attendance_mark.attendance_hostel = current_user.hostel_location
                    db.session.commit()
                    flash('Attendance Updated', 'success')
            elif (form.absend_date.data > datetime.now(tz_india).date() and ( datetime.now(tz_india).hour >=23 )):
                    flash('Attendance can be marked only till 11.00pm', 'danger')
            elif (form.absend_date.data > datetime.now(tz_india).date() and form.absend_time.data != '0'):
            # >= should be converted to >. this is for debugging points
                try:
                    attendance_mark = Attendance(attendance_date=form.absend_date.data,
                                            attendance_time = dict(form.absend_time.choices).get(form.absend_time.data),
                                            attendance_point=form.absend_time.data,
                                            attendance_user=current_user.id,
                                            attendance_hostel = current_user.hostel_location,
                                            attendance_reason = dict(form.absend_reason.choices).get(form.absend_reason.data) )
                    db.session.add(attendance_mark)
                    db.session.commit()
                    #flash(Markup('Your Requirments are submitted, <a href ="/my_submissions"> here </a>  !!!'),'success')
                    flash('Your Attendance Recorded. You can check the same below','success')
                except:
                    db.session.rollback()
                    flash('Duplicate Entry for this date, Only one time can be marked as absent','danger')
                    return render_template('users/profile.html',title='Submit Poster Details',form=form,
                                            attendanceviewform=attendanceviewform)

            else:
                flash('You are trying to delete a Attendance Date that you have not entered', 'danger')

        elif attendanceviewform.submit1.data and attendanceviewform.validate_on_submit():
                #Nizam: Add one more extract to extraxt via year also
                attendanceview = Attendance.query.filter_by(attendance_user=current_user.id).filter(extract('month', Attendance.attendance_date)==attendanceviewform.attendance_view_date.data.month).all()
                monthlytotal = attendance_total(attendanceview,attendanceviewform,current_user)
                daily_expense, common_expense = monthly_bill(attendanceviewform)
                bill = daily_expense*monthlytotal+common_expense
                return render_template('users/profile.html',title='Submit Poster Details',
                                        form=form, attendanceviewform=attendanceviewform,
                                        attendanceview=attendanceview, monthlytotal=monthlytotal,
                                        monthlybill=bill, rent=rent)
        return render_template('users/profile.html',title='Submit Poster Details', form=form, attendanceviewform=attendanceviewform)
    elif current_user.user_status == "Pending":
        flash('Your request to join hostel is still pending, Please contact Hostel Manager for approval', 'primary')
        return render_template('users/user_status_not_active.html')
    elif current_user.user_status == "Alumni":
        flash('Your are not a member of hostel now , If you are looking for re-admission please contact hostel manager', 'primary')
        return render_template('users/user_status_not_active.html')


def attendance_total(attendanceview,attendanceviewform,current_user):
    #[Nizam][July-03]Number of working days should be taken from hostel instead of default 30
    attendanceview=attendanceview
    attendanceviewform=attendanceviewform
    current_user=current_user
    total=[]
    for i in range(len(attendanceview)):
        total.append(float(attendanceview[i].attendance_point))

    working_days = HostelExpense.query.filter_by(expense_hostel=current_user.hostel_location).\
    filter_by(expense_bill_month=attendanceviewform.attendance_view_date.data).first()
    if working_days:
        monthlytotal=working_days.expense_working_days_per_month-sum(total)
    elif not working_days:
        monthlytotal=30-sum(total)

    if (current_user.joining_date.month, current_user.joining_date.year) == (attendanceviewform.attendance_view_date.data.month,attendanceviewform.attendance_view_date.data.year):
        monthlytotal = monthlytotal-current_user.joining_date.day

    return monthlytotal

def monthly_bill(attendanceviewform):
    #AttributeError: 'NoneType' object has no attribute 'hostel_daily_expense', Implementation from 106 onwards if ....

    attendanceviewform=attendanceviewform
    daily_expense = HostelExpense.query.filter_by(expense_hostel=current_user.hostel_location).\
        filter(extract('month',HostelExpense.expense_bill_month)==attendanceviewform.attendance_view_date.data.month).first()
    if not daily_expense:
        flash('expense not available')
        return 0,0
    elif daily_expense:
        return daily_expense.expense_daily_expense, daily_expense.expense_common_per_head


@user_blueprint.route('/billing_history', methods=['GET', 'POST'])
@login_required
#@roles_required('manager')
def billing_history():
    billing_history = BillPending.query.filter_by(bill_user = current_user.id).all()
    return render_template('users/billing_history.html',title='Billing History', billing_history=billing_history)
