# import os
# import secrets
# from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, session
from aims_ import app, db, bcrypt
# from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from aims_.forms import RegistrationForm, LoginForm
from aims_.models import Broker, Admin, Company
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
@login_required
def home():
    return render_template('home.html')

#broker
@app.route("/fellowsdisplay")
@login_required
def fellowdisp():
    if session['account_type'] == 'broker':
        users = Broker.query.all()
    elif session['account_type'] == 'admin':
        users = Admin.query.all()
    elif session['account_type'] == 'company':
        users = Company.query.all()
    return render_template('fellowsdisp.html',users = users)

@app.route("/about")
def about():
    #-------------
    print("Request ",end="")
    print(request)
    print(current_user) #User('ak', 'akanksh@example.com', 'default.jpg') or <flask_login.mixins.AnonymousUserMixin object at 0x0000019494BFA388> if not login
    print(session)
    #print(session['_user_id']) #cant access this here as this guy is anonymous as @login_required is not applied to this guy
    #print(session['account_type'])
    #------------
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            if form.role.data.lower() == 'broker':
                user = Broker(username=form.username.data, email=form.email.data, password=hashed_password)
            elif form.role.data.lower() == 'admin':
                user = Admin(username=form.username.data, email=form.email.data, password=hashed_password)
            elif form.role.data.lower() == 'company':
                user = Company(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created with a role of %s! You are now able to log in'%(form.role.data.lower()), 'success')
            return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            #----------------- MODIFYING SESSION
            session['account_type'] = form.role.data.lower()
            #------------------ ADDED SESSION DETAILS
            if session['account_type'] == 'broker':
                user = Broker.query.filter_by(email=form.email.data).first()
                if user: 
                    if bcrypt.check_password_hash(user.password, form.password.data):
                        login_user(user, remember=form.remember.data)
                        next_page = request.args.get('next')
                        
                        return redirect(next_page) if next_page else redirect(url_for('home'))
                    else:
                        flash(f'Welcome back {user.username}. Please check password', 'danger')
                else:
                    flash('Email does not exist. Register Below', 'danger')
            elif session['account_type'] == 'admin':
                user = Admin.query.filter_by(email=form.email.data).first()
                if user: 
                    if bcrypt.check_password_hash(user.password, form.password.data):
                        login_user(user, remember=form.remember.data)
                        next_page = request.args.get('next')
                        
                        return redirect(next_page) if next_page else redirect(url_for('home'))
                    else:
                        flash(f'Welcome back {user.username}. Please check password', 'danger')
                else:
                    flash('Email does not exist. Register Below', 'danger')
            elif session['account_type'] == 'company':
                user = Company.query.filter_by(email=form.email.data).first()
                if user: 
                    if bcrypt.check_password_hash(user.password, form.password.data):
                        login_user(user, remember=form.remember.data)
                        next_page = request.args.get('next')
                        
                        return redirect(next_page) if next_page else redirect(url_for('home'))
                    else:
                        flash(f'Welcome back {user.username}. Please check password', 'danger')
                else:
                    flash('Email does not exist. Register Below', 'danger')
            
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

# @app.route("/account")
# @login_required
# def account():
#     #-------------
#     print("Request ",end="")
#     print(request)
#     print(current_user) #User('ak', 'akanksh@example.com', 'default.jpg') 
#     print(session)   #<SecureCookieSession {'_fresh': True, '_id': 'fb94666e191c4de1198f13e41f735dfd8fbb27cff6226f6777bf3bbc1928c9d778c203afc99c194ea9e7501da9ec71446193196e7ea20e3f74b7a7919adea310', '_user_id': '1', 'csrf_token': '907b4853ddd27b84ae9cca324b5ad4d1bc679cdb'}> 
#     print(session['_user_id'])
#     #------------
#     return render_template('account.html', title='Account')


@app.route("/account/<int:user_id>/view")
@login_required
def account(user_id):
    if session['account_type'] == 'broker':
        user = Broker.query.get_or_404(user_id)
    elif session['account_type'] == 'admin':
        user = Admin.query.get_or_404(user_id)
    elif session['account_type'] == 'company':
        user = Company.query.get_or_404(user_id)
    #-------------
    print("Request ", end="")
    print(request)
    print(current_user)  # User('ak', 'akanksh@example.com', 'default.jpg')
    print(session)  # <SecureCookieSession {'_fresh': True, '_id': 'fb94666e191c4de1198f13e41f735dfd8fbb27cff6226f6777bf3bbc1928c9d778c203afc99c194ea9e7501da9ec71446193196e7ea20e3f74b7a7919adea310', '_user_id': '1', 'csrf_token': '907b4853ddd27b84ae9cca324b5ad4d1bc679cdb'}>
    print(session['_user_id'])
    #------------
    return render_template('account.html', title='Account',userdetail = user)
