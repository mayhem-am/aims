import os
import secrets
#from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, session
from aims_ import app, db, bcrypt, collection
from aims_.forms import RegistrationForm, LoginForm, UploadInvoiceForm, SelectBrokerForm, AssignCommissionForm
from aims_.models import Broker, Admin, Company, Invoice
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home():
    """
    Test mongodb connection
    for x in collection.find({}):
        print(x) 
    """
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

@app.route("/viewinvoices")
@login_required
def view_invoices(): 
    if session['account_type']== 'company':
        invoices = Invoice.query.filter_by(owner_id = current_user.id).all()
        title = 'View Invoices'
    elif session['account_type']== 'admin':
        invoices = Invoice.query.filter_by(broker_id = None).all() 
        title = 'Assign Broker'
    elif session['account_type']== 'broker':
        invoices = Broker.query.filter_by(id = current_user.id).first().invoices
        invoices = list(filter(lambda inv:inv.processed==False,invoices))
        title = 'Process Invoices'
    return render_template('view_invoices.html', title=title,userdetail = current_user, image_files=invoices)

@app.route("/viewinvoices/<int:invoice_id>/view")
@login_required
def view_invoice_by_id(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    return render_template('viewinvoice.html', title='View Invoice',invoice = invoice)

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
            # MODIFYING SESSION
            session['account_type'] = form.role.data.lower()
            # ADDED SESSION DETAILS
            if session['account_type'] == 'broker':
                typeofuser = Broker
            elif session['account_type'] == 'admin':
                typeofuser = Admin
            elif session['account_type'] == 'company':
                typeofuser = Company
            user = typeofuser.query.filter_by(email=form.email.data).first()
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

'''
broker specific routing
'''
@app.route("/viewinvoices/<int:invoice_id>/process", methods=['GET','POST'])
@login_required
def process_invoice(invoice_id): 
    """
    invoice extraction part
    """
    if session['account_type']== 'broker':
        invoice = Invoice.query.filter_by(id= invoice_id).first()
        invoice.processed = True
        db.session.commit()
        return redirect(url_for('view_invoices'))
        return render_template('process_invoice.html', title='Extract Invoice')
    abort(403)

'''
admin specific routing
'''
@app.route("/viewinvoices/<int:invoice_id>/assign", methods=['GET','POST'])
@login_required
def assign_invoice(invoice_id): 
    if session['account_type']== 'admin':
        form = SelectBrokerForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                invoice = Invoice.query.filter_by(id = invoice_id).first()
                brokerid = Broker.query.filter_by(username = form.broker.data).first().id
                invoice.broker_id = brokerid
                db.session.commit()
                flash('Your invoice has been assigned to %s'%(form.broker.data), 'success')
                return redirect(url_for('view_invoices'))
        return render_template('assign_broker.html', title='Assign Broker',form = form)
    abort(403)

@app.route("/viewcompanies")
@login_required
def view_companies():
    if session['account_type']== 'admin':
        companies = Company.query.all()
        return render_template('view_companies.html', title='View Companies',companies = companies)
    abort(403)

@app.route("/viewcompanies/<int:company_id>/assigncommission",methods= ['GET','POST'])
@login_required
def view_company_by_id(company_id):
    if session['account_type']== 'admin':
        company = Company.query.filter_by(id = company_id).first()
        form = AssignCommissionForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                company.commission = form.newcommission.data
                db.session.commit()
                flash('%s commission has been changed to %d'%(company.username,form.newcommission.data), 'success')
                return redirect(url_for('view_companies'))
        elif request.method == 'GET':
            form.newcommission.data = company.commission
        return render_template('assign_commission.html', title='Assign Commission',form = form)
    abort(403)

'''
company specific routing
'''
def save_picture(form_picture,directory):
    """
    helper function to save pictue in static/<directory>
    """
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = f_name + f_ext
    picture_path = os.path.join(app.root_path, 'static/'+directory, picture_fn)
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
def upload_invoice():
    if session['account_type']== 'company':
        form = UploadInvoiceForm()
        if form.validate_on_submit():
            if form.invoice_picture.data and form.coords_file.data:
                picture_file = save_picture(form.invoice_picture.data,'invoices')
                coords_file = save_picture(form.coords_file.data,'coordinates')
                inv = Invoice(image_file = picture_file,coors_file = coords_file,owner_id = current_user.id)
                db.session.add(inv)
                db.session.commit()
                flash('Your invoice has been uploaded. Go to View invoices to check', 'success')
        return render_template('upload_invoice.html', title='Upload',userdetail = current_user, form=form)
    abort(403)

@app.route("/viewinvoices/<int:invoice_id>/delete", methods=['GET','POST'])
@login_required
def delete_invoice(invoice_id):
    if session['account_type']== 'company':
        invoice = Invoice.query.get_or_404(invoice_id)
        if invoice.owner_id == current_user.id:
            db.session.delete(invoice)
            db.session.commit()
            flash('Your invoice has been deleted!', 'success')
        else:
            flash('You are not the owner!', 'danger')
        return redirect(url_for('view_invoices'))
    abort(403)

@app.route("/viewinventory")
@login_required
def view_inventory(): #separate -- query
    """
    query products belonging to company and id of invoice from where they came from
    Product.query.filter_by(owner_id = currentuser.id).all()
    """
    if session['account_type']== 'company':
        return render_template('view_inventory.html', title='View Inventory',userdetail = current_user)
    abort(403)
