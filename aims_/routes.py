import os
import secrets
#from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, session
from aims_ import app, db, bcrypt
from aims_.forms import RegistrationForm, LoginForm, UploadInvoiceForm
from aims_.models import Broker, Admin, Company
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
@login_required
def home():
    return render_template('home.html')

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
                        login_user(user)
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
                        login_user(user)
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
                        login_user(user)
                        next_page = request.args.get('next')
                        return redirect(next_page) if next_page else redirect(url_for('home'))
                    else:
                        flash(f'Welcome back {user.username}. Please check password', 'danger')
                else:
                    flash('Email does not exist. Register Below', 'danger')
            
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    del session['account_type'] # remove user from session to complement anonymous user mixin for 'current_user'
    logout_user()
    return redirect(url_for('home'))

@app.route("/account/<int:user_id>/view")
@login_required
def account(user_id):
    if session['account_type'] == 'broker':
        user = Broker.query.get_or_404(user_id)
    elif session['account_type'] == 'admin':
        user = Admin.query.get_or_404(user_id)
    elif session['account_type'] == 'company':
        user = Company.query.get_or_404(user_id)
    return render_template('account.html', title='Account',userdetail = user)

'''
user specific routing
'''
@app.route("/processinvoices")
@login_required
def process_invoices():  #separate -- button
    if session['account_type']== 'broker':
        return render_template('process_invoices.html', title='Process',userdetail = current_user)
    else:
        abort(403)

@app.route("/assignbrokers")
@login_required
def assign_brokers():  #separate -- button
    if session['account_type']== 'admin':
        return render_template('assign_brokers.html', title='Process',userdetail = current_user)
    else:
        abort(403)

@app.route("/viewcompanies")
@login_required
def view_companies(): #separate -- query
    if session['account_type']== 'admin':
        return render_template('view_companies.html', title='Process',userdetail = current_user)
    else:
        abort(403)


# helper function to save pictue in static/profile_pics
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    # file_name and file_extension is returned
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    form_picture.save(picture_path)
    """
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    """

    return picture_fn

@app.route("/uploadinvoice", methods=['GET','POST'])
@login_required
def upload_invoice(): #separate -- button #IMP
    """
    creating a form
    """
    if session['account_type']== 'company':
        form = UploadInvoiceForm()
        if form.validate_on_submit():
            if form.invoice_picture.data or form.coords_file.data:
                picture_file = save_picture(form.invoice_picture.data)

        return render_template('upload_invoice.html', title='Process',userdetail = current_user, form=form)
    else:
        abort(403)

@app.route("/viewinvoices")
@login_required
def view_invoices(): #separate -- query
    # write the database query to get all invoices and then send
    # here sending only profile picture
    image_file = url_for('static', filename='profile_pics/')
    if session['account_type']== 'company':
        return render_template('view_invoices.html', title='Process',userdetail = current_user, image_file=image_file)
    else:
        abort(403)

@app.route("/viewinventory")
@login_required
def view_inventory(): #separate -- query
    if session['account_type']== 'company':
        return render_template('view_inventory.html', title='Process',userdetail = current_user)
    else:
        abort(403)