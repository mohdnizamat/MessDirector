from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, SelectField, validators
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms.fields.html5 import DateField



class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = DateField('Password - Your Date of Birth', validators=[DataRequired()], format='%Y-%m-%d')

    phonenumber = IntegerField('Phone Number', validators=[DataRequired()])
    parents_phonenumber = IntegerField('Parent Phone Number', validators=[DataRequired()])
    blood_group = SelectField('Blood Group', choices=[('1', 'A+'), ('2','O+'), ('3', 'B+'),('4', 'AB+'), ('5','A-'), ('6', 'O-'),('7','B-'), ('8', 'AB-'), ('9', 'Dont Know') ])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=5,max=20)])
    hostel = SelectField('Select hostel', coerce=int, choices=[()], validators=[DataRequired()])

    submit = SubmitField('Sign Up')



    '''def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')'''


class LoginForm(FlaskForm):
    phonenumber = IntegerField('Phohe Number', validators=[DataRequired()])
    password = DateField('Password - Your Date of Birth', validators=[DataRequired()], format='%Y-%m-%d')
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class AttendanceViewForm(FlaskForm):
    attendance_view_date =  DateField('Select Month to view ', validators=[DataRequired()],format='%Y-%m')
    submit1 = SubmitField('Update')

class AttendanceViewFormManager(FlaskForm):
    attendance_view =  DateField('Select Date to view ', validators=[DataRequired()],format='%Y-%m-%d')
    submit = SubmitField('Check Attendance')


class AttendanceForm(FlaskForm):
    absend_date = DateField('Select Mess Absent Date', validators=[DataRequired()],format='%Y-%m-%d')
    absend_time = SelectField('Select Time For Absent', choices=[('1','Full Day'),('0.30','BreakFast'),('0.3','Lunch'),('0.4','Dinner'), ('0','Delete Absent on this date' )], validators=[DataRequired()])
    absend_reason = SelectField('Reason for Mess Absent', choices=[('1','Not in Bangalore'),('2','In Office'),('3','In College'),('4','Going Out'), ('5','Not well - Sick'), ('6','Fasting')], validators=[DataRequired()])
    submit = SubmitField('Submit')

class UserProfileForm(FlaskForm):
    first_name = StringField('First name', validators=[
        validators.DataRequired('First name is required')])
    last_name = StringField('Last name', validators=[
        validators.DataRequired('Last name is required')])
    submit = SubmitField('Save')

class UserProfile(FlaskForm):
    first_name = StringField('First name', validators=[
        validators.DataRequired('First name is required')])
    last_name = StringField('Last name', validators=[
        validators.DataRequired('Last name is required')])
    email = StringField('Email')
    phonenumber = IntegerField('Your Primary Phone Number', validators=[
        validators.DataRequired('Phone number is required')])
    parent_phone = IntegerField('Parent Phone Number', validators=[
        validators.DataRequired('Parents Phone Number is required')])
    address = StringField('Home Address', validators=[
        validators.DataRequired('Home Address is required')])
    caution_deposit = IntegerField('Caution Deposit', validators=[
        validators.DataRequired('Amount enterd is not proper')])
    rent_amount = IntegerField('Rent per month', validators=[
        validators.DataRequired('Amount enterd is not proper')])
    joining_date = DateField('Hostel Admission date', validators=[DataRequired()],format='%Y-%m-%d')
    user_status = SelectField('User Status', choices=[('2', 'Active'), ('1','Pending'), ('3', 'Alumni'), ('4', 'Delete User')])
    submit = SubmitField('Save User Details')


class UserBillSection(FlaskForm):
    paid_amount = IntegerField('Total Amount Paid', validators=[
        validators.DataRequired('Amount enterd is not proper')])
    bill_paying_month =  DateField(label='Bill Paying Month', validators=[
        validators.DataRequired('Select Month - This is required')],format='%Y-%m')
    submit_bill_details = SubmitField('Submit Bill Details')


class BillingSectionForm(FlaskForm):
    hostel_expense_month =  DateField('Select Month to generate bill ', validators=[DataRequired()],format='%Y-%m')
    hostel_monthly_expense = IntegerField('Monthly Total Expense',validators=[
        validators.DataRequired('First name is required')])
    hostel_monthly_buffer = IntegerField('Monthly Buffer')
    hostel_common_expense = IntegerField('Common Expense Per Head')
    hostel_working_days_per_month = IntegerField('Number of Mess days')
    submit_bill_section = SubmitField('Save')

class BillPopulationForm(FlaskForm):
    submit_bill_population = SubmitField('Generate Bill')
