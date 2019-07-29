# This file defines command line commands for manage.py
#
# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

import datetime

from flask import current_app
from flask_script import Command

from app import db
from app.models.user_models import User, Role, Hostel, Attendance, BillPending

class InitDbCommand(Command):
    """ Initialize the database."""

    def run(self):
        init_db()
        print('Database has been initialized.')

def init_db():
    """ Initialize the database."""
    db.drop_all()
    db.create_all()
    create_users()
    create_hostel()


def create_users():
    """ Create users """

    # Create all tables
    db.create_all()

    # Adding roles
    admin_role = find_or_create_role('admin', u'Admin')
    manager_role = find_or_create_role('manager', u'Manager')

    a=datetime.date(2019,5,5)
    #dob should be passed as python datetime.date object, so implemented This.


    # Add users
    site_admin = find_or_create_user(u'Admin', u'Example', u'admin@example.com', 'Password1', '8892258999', a, u'MessDirectorAdmin', admin_role)
    hebbal = find_or_create_user(u'Hebbal Manager', u'Ashik', u'manager@hebbal.com', 'kradhakrishnan', '8105200959',a, u'Hebbal Darussalam', manager_role)
    banashankari = find_or_create_user(u'Banashankari Manager', u'Samad Faizy', u'manager@banashankari.com', 'soundsystem', '9645567432',  a, u'Banashankari',  manager_role)
    bommanahalli = find_or_create_user(u'Bommanahalli Manager', u'Saleem Mint', u'manager@bommanahalli.com', 'mintmarketing', '7907015940', a, u'Bommanahalli', manager_role)
    user1 = find_or_create_user(u'Member1 Bommanhalli', u'Example', u'bommember1@example.com', 'Password1','1234567899',a, u'Bommanahalli')
    user2 = find_or_create_user(u'Member2 Bommanhalli', u'Example', u'bommember2@example.com', 'Password1', '3692587412',a, u'Bommanahalli')
    user3 = find_or_create_user(u'Member3 Bommanhalli', u'Example', u'bommember3pppppp@example.com', 'Password1', '4561239874',a, u'Bommanahalli')

    #Banashankari
    user4 = find_or_create_user(u'Member1 Banashankari', u'Example', u'banmember1@example.com', 'Password1','1234567999',a, u'Banashankari')
    user5 = find_or_create_user(u'Member2 Banashankari', u'Example', u'banmember2@example.com', 'Password1', '3692587112',a, u'Banashankari')
    user6 = find_or_create_user(u'Member3 Banashankari', u'Example', u'banmember3pppppp@example.com', 'Password1', '4561239774',a, u'Banashankari')

    #Hebbal

    user7 = find_or_create_user(u'Member1 Hebbal', u'Example', u'hebmember1@example.com', 'Password1','1234557899',a, u'Hebbal Darussalam')
    user8 = find_or_create_user(u'Member2 Hebbal', u'Example', u'hebmember2@example.com', 'Password1', '3692557412',a, u'Hebbal Darussalam')
    user9 = find_or_create_user(u'Member3 Hebbal', u'Example', u'hebmember3@example.com', 'Password1', '4561229874',a, u'Hebbal Darussalam')


    # Save to DB
    db.session.commit()

def create_hostel():
    db.create_all()
    hebbal = find_or_create_hostel(u'Hebbal Darussalam', u'manager@hebbl.com')
    banashankari = find_or_create_hostel(u'Banashankari', u'manager@banashankari.com')
    bommanahalli = find_or_create_hostel(u'Bommanahalli', u'manager@bommanahalli.com')

    db.session.commit()



def find_or_create_role(name, label):
    """ Find existing role or create new role """
    role = Role.query.filter(Role.name == name).first()
    if not role:
        role = Role(name=name, label=label)
        db.session.add(role)
    return role


def find_or_create_user(first_name, last_name, email,
                        password, phonenumber, dob, hostel_location, role=None):
    """ Find existing user or create new user """
    user = User.query.filter(User.email == email).first()
    if not user:
        user = User(email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=current_app.user_manager.password_manager.hash_password(password),
                    active=True,
                    phonenumber=phonenumber,
                    dob=dob,
                    hostel_location=hostel_location,
                    email_confirmed_at=datetime.datetime.utcnow())
        if role:
            user.roles.append(role)
        db.session.add(user)
    return user

def find_or_create_hostel(name, hostel_manager):
    """ Find existing role or create new role """
    hostel = Hostel.query.filter(Hostel.hostel_name == name).first()
    if not hostel:
        hostel = Hostel(hostel_name=name, hostel_manager=hostel_manager)
        db.session.add(hostel)
    return hostel
