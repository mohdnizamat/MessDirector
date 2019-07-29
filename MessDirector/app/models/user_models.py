# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

from flask_user import UserMixin
# from flask_user.forms import RegisterForm
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators
from flask_user.forms import RegisterForm
from wtforms.validators import DataRequired
from app import db


# Define the User data model. Make sure to add the flask_user.UserMixin !!

class Hostel(db.Model):
    __tablename__ = 'hostels'
    id = db.Column(db.Integer, primary_key=True)
    hostel_name = db.Column(db.String(100), nullable=False)
    hostel_manager = db.Column(db.String(10), nullable=True)
    hostel_inmates_list = db.relationship('User', backref='hostel_list', lazy='dynamic')
    hostel_role = db.relationship('Role', secondary='hostel_roles', backref=db.backref('hostels', lazy='dynamic'))
    hostel_expense = db.relationship('HostelExpense', backref='hostels', lazy='dynamic')




class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # User authentication information (required for Flask-User)
    email = db.Column(db.Unicode(255), nullable=False, server_default=u'', unique=True)
    email_confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')

    # reset_password_token = db.Column(db.String(100), nullable=False, server_default='')
    active = db.Column(db.Boolean(), nullable=False, server_default='0')

    # User information
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')
    last_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')
    image_file = db.Column(db.String(20), default='default.jpg')
    dob = db.Column(db.Date, nullable=True)
    phonenumber = db.Column(db.String(20), unique=True, nullable=False, server_default='0')
    parent_phone = db.Column(db.String(20),  nullable=True, server_default='0')
    address = db.Column(db.String(100), unique=False)
    rent_amount = db.Column(db.Integer,nullable=True, default=0)
    user_status = db.Column(db.String, server_default=u'Pending')
    blood_group = db.Column(db.String, nullable=True, server_default='0')
    caution_deposit = db.Column(db.Integer,nullable=True, default=0)
    joining_date =  db.Column(db.Date, nullable=True)
    hostel_location = db.Column(db.String, db.ForeignKey('hostels.hostel_name'))


    # Relationships
    roles = db.relationship('Role', secondary='users_roles',
                            backref=db.backref('users', lazy='dynamic'))
    hostels = db.relationship('Hostel', backref=db.backref('users', lazy='dynamic'))
    attendance = db.relationship('Attendance', backref='users', lazy='dynamic')
    bill_pending = db.relationship('BillPending', backref='users', lazy='dynamic')





# Define the Role data model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False, server_default=u'', unique=True)  # for @roles_accepted()
    label = db.Column(db.Unicode(255), server_default=u'')  # for display purposes


# Define the UserRoles association model
class UsersRoles(db.Model):
    __tablename__ = 'users_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


class HostelRoles(db.Model):
    __tablename__ = 'hostel_roles'
    id = db.Column(db.Integer(), primary_key=True)
    hostel_id = db.Column(db.Integer(), db.ForeignKey('hostels.id', ondelete='CASCADE'))
    hostel_role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))




class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attendance_user = db.Column(db.Integer,  db.ForeignKey('users.id'))
    attendance_date = db.Column(db.Date, nullable=False)
    attendance_point = db.Column(db.String, nullable=False) #this is string, later will have to converted, we are getting as string
    attendance_time = db.Column(db.String, nullable=False)
    attendance_reason = db.Column(db.String, nullable=True)
    attendance_hostel = db.Column(db.String,  nullable=True)



class BillPending(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_user = db.Column(db.Integer,  db.ForeignKey('users.id'))
    bill_date = db.Column(db.Date, nullable=True)
    bill_amount_current_date = db.Column(db.Integer, default=0)
    bill_total = db.Column(db.Integer, default=0)
    bill_payment = db.Column(db.Integer, default=0)
    bill_balance = db.Column(db.Integer, default=0)
    bill_payment_status = db.Column(db.String, default='Pending')


class HostelExpense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expense_hostel = db.Column(db.String,  db.ForeignKey('hostels.hostel_name'))
    expense_monthly = db.Column(db.Integer, default=0)
    expense_monthly_buffer = db.Column(db.Integer, default=0)
    expense_daily_expense = db.Column(db.Integer, default=0)
    expense_common_per_head = db.Column(db.Integer, default=0)
    expense_bill_month = db.Column(db.Date, nullable=True)
    expense_total_points = db.Column(db.Integer, default=0)
    expense_working_days_per_month = db.Column(db.Integer, nullable=True, default=30)



# # Define the User registration form
# # It augments the Flask-User RegisterForm with additional fields
# class MyRegisterForm(RegisterForm):
#     first_name = StringField('First name', validators=[
#         validators.DataRequired('First name is required')])
#     last_name = StringField('Last name', validators=[
#         validators.DataRequired('Last name is required')])


# Define the User profile form
