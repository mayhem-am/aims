import os
import secrets
#from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, session
from aims_ import app, db, bcrypt, collection
from aims_.models import Broker, Admin, Company, Invoice, Specialization,Product,Inventory
from aims_.forms import RegistrationUserForm, RegistrationCompanyForm, LoginForm, UploadInvoiceForm, SelectBrokerForm, AssignCommissionForm, RoleForm, AssignQuantityForm,ManualProcessForm
from flask_login import login_user, current_user, logout_user, login_required
from aims_.invoice_extract import predict_invoice
from aims_.updateproddb import update_products

@app.route("/")
@app.route("/home")
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
        invoices = list(filter(lambda inv:inv.processed==False or (inv.processed==True and inv.manual_processing==True),invoices))
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
    form = RoleForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            role = form.role.data.lower()
            if role == 'broker' or role == 'admin':
                return redirect(url_for('registeruser'))
            else:
                return redirect(url_for('registercompany'))
    return render_template('register.html', title='Register', form=form)
        
@app.route("/register/user", methods=['GET', 'POST'])
def registeruser():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationUserForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(
                form.password.data).decode('utf-8')
            role = form.role.data.lower()
            if role == 'broker':
                user = Broker(username=form.username.data,
                              email=form.email.data, password=hashed_password,sex = form.sex.data,street=form.street.data,phone=form.phone.data)
            else:
                user = Admin(username=form.username.data,
                             email=form.email.data, password=hashed_password, sex=form.sex.data, street=form.street.data, phone=form.phone.data)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created with a role of %s! You are now able to log in' % (
                role), 'success')
            return redirect(url_for('login'))
    return render_template('registeruser.html', title='Register - User', form=form)
        
@app.route("/register/company", methods=['GET', 'POST'])
def registercompany():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationCompanyForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')          
            user = Company(username=form.username.data, email=form.email.data,
                           password=hashed_password, street=form.street.data, phone=form.phone.data)
            db.session.add(user)
            db.session.commit()
            specs = []
            if form.specialization1.data!='N/A':
                specs.append(form.specialization1.data)
            if form.specialization2.data != 'N/A':
                specs.append(form.specialization2.data)
            if form.specialization3.data != 'N/A':
                specs.append(form.specialization3.data)
            g = specs[:]
            g = list(filter(lambda x: g.remove(x) is None and g.count(x) == 0, specs)) # unique specialization only
            getcomp = Company.query.filter_by(email=form.email.data).first()
            if getcomp!=None:
                for spec in g:
                    user = Specialization(name=spec,company_id=getcomp.id)
                    db.session.add(user)
                    db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))
    return render_template('registercompany.html', title='Register - Company', form=form)

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
    if session['account_type']== 'broker':
        invoice = Invoice.query.filter_by(id= invoice_id).first()
        if invoice!=None and invoice.processed==True:
            flash('Invoice %d has already been processed' %
                  (invoice.id), 'danger')
            return redirect(url_for('view_invoices'))
        image_path = os.path.join(app.root_path, 'static/invoices', invoice.image_file)
        coors_path = os.path.join(app.root_path, 'static/coordinates', invoice.coors_file)
        data, table_data,confidence  = predict_invoice(image_path,coors_path) #extract fields
        update_products(table_data,invoice.owner_id,invoice.id)      #update product database
        if confidence>100:
            confidence=100
        post_data = {"invoice_id":invoice.id,"owner_id":invoice.owner_id,"Accuracy":confidence}
        if len(data)!=0:
            for field in data:
                post_data.update(field)
        tabledata = {}
        if len(table_data) != 0:
            ll = []
            for ele in table_data:
                ll.append([ele[0],ele[2]])
            tabledata = {"Items": ll}
        post_data.update(tabledata)
        collection.insert_one(post_data)
        invoice.processed = True
        no_table_items = len(data)+len(table_data)
        owner = invoice.owner
        owner.revenue_generated+= (owner.commission*no_table_items)
        db.session.commit()
        flash('Invoice %d by %s has been processed'%(invoice.id,owner.username), 'success')
        return redirect(url_for('view_invoices'))
    abort(403)


@app.route("/viewinvoices/<int:invoice_id>/manprocess", methods=['GET', 'POST'])
@login_required
def processman(invoice_id):
    if session['account_type'] == 'broker':
        items = []
        for x in collection.find({"invoice_id":invoice_id}):
            checkinvoice = Invoice.query.filter_by(id=x["invoice_id"]).first()
            if checkinvoice !=None:
                post_data = {"invoice_id": x["invoice_id"], "owner_id": x["owner_id"], "Accuracy": 100}
                tabledata = {"Items":x["Items"]}
                form = ManualProcessForm()
                if request.method == 'POST':
                    if form.validate_on_submit():
                        if "Company Name" in x:
                            post_data["Company Name"] = form.compname.data
                        if "Company Address" in x:
                            post_data["Company Address"] = form.compaddr.data
                        if "Invoice Number" in x:
                            post_data["Invoice Number"] = form.invnum.data
                        if "Discount" in x:
                            post_data["Discount"] = form.disc.data
                        if "Tax" in x:
                            post_data["Tax"] = form.tax.data
                        if "Subtotal" in x:
                            post_data["Subtotal"] = form.subt.data
                        if "Total" in x:
                            post_data["Total"] = form.total.data
                        collection.delete_one({"invoice_id": invoice_id})
                        post_data.update(tabledata)
                        collection.insert_one(post_data)
                        checkinvoice.manual_processing = False
                        db.session.commit()
                        flash('Invoice %d successfully manually processed'%(checkinvoice.id), 'success')
                        return redirect(url_for('view_invoices'))
                elif request.method == 'GET':
                    if "Company Name" in x:
                        form.compname.data = x["Company Name"]
                    if "Company Address" in x:
                        form.compaddr.data = x["Company Address"]
                    if "Invoice Number" in x:
                        form.invnum.data = x["Invoice Number"] 
                    if "Discount" in x:
                        form.disc.data = x["Discount"] 
                    if "Tax" in x:
                        form.tax.data = x["Tax"] 
                    if "Subtotal" in x:
                        form.subt.data = x["Subtotal"]
                    if "Total" in x:
                        form.total.data = x["Total"]
        return render_template('manual_process.html', title='Manual Process', actlabels=x, form=form, invoice=checkinvoice)
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
                brokerid = Broker.query.filter_by(username = form.broker.data).first()
                if brokerid is None:
                    flash('Broker does not exist. Please reassign to different broker', 'danger')
                    return redirect(url_for('view_invoices'))
                invoice.broker_id = brokerid.id
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

@app.route("/viewcompanies/<int:company_id>/terminate", methods=['GET','POST'])
@login_required
def terminate_company(company_id):
    if session['account_type']== 'admin':
        comp = Company.query.get_or_404(company_id)
        compname = comp.username
        collection.delete_many({"owner_id":comp.id})
        db.session.delete(comp)
        db.session.commit()
        flash('Business with %s has been terminated!'%(compname), 'success')
    else:
        flash('You are not an admin!', 'danger')
    return redirect(url_for('view_companies'))
    
@app.route("/viewbrokers")
@login_required
def view_brokers():
    if session['account_type']== 'admin':
        brokers = Broker.query.all()
        return render_template('view_brokers.html', title='View Brokers',users = brokers)
    abort(403)

@app.route("/viewbrokers/<int:broker_id>/terminate", methods=['GET', 'POST'])
@login_required
def terminate_broker(broker_id):
    if session['account_type'] == 'admin':
        bro = Broker.query.get_or_404(broker_id)
        broname = bro.username
        db.session.delete(bro)
        db.session.commit()
        flash('%s has been terminated!' %
              (broname), 'success')
    else:
        flash('You are not an admin!', 'danger')
    return redirect(url_for('view_brokers'))

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
                checkinv = Invoice.query.filter_by(image_file = picture_file,coors_file = coords_file).first()
                if checkinv==None or checkinv.owner_id!=current_user.id:
                    inv = Invoice(image_file = picture_file,coors_file = coords_file,owner_id = current_user.id)
                    db.session.add(inv)
                    db.session.commit()
                    flash('Your invoice has been uploaded. Go to View invoices to check', 'success')
                else:
                    flash('That invoice has already been uploaded. Go to View invoices to check', 'danger')
        return render_template('upload_invoice.html', title='Upload',userdetail = current_user, form=form)
    abort(403)

@app.route("/viewinvoices/<int:invoice_id>/delete", methods=['GET','POST'])
@login_required
def delete_invoice(invoice_id):
    if session['account_type']== 'company':
        invoice = Invoice.query.get_or_404(invoice_id)
        if invoice.owner_id == current_user.id:
            collection.delete_one({"invoice_id":invoice.id,"owner_id":current_user.id})
            db.session.delete(invoice)
            db.session.commit()
            flash('Your invoice has been deleted!', 'success')
        else:
            flash('You are not the owner!', 'danger')
        return redirect(url_for('view_invoices'))
    abort(403)


@app.route("/viewinvoices/<int:invoice_id>/manualprocess", methods=['GET', 'POST'])
@login_required
def manually_process(invoice_id):
    if session['account_type'] == 'company':
        invoice = Invoice.query.get_or_404(invoice_id)
        if invoice.owner_id == current_user.id:
            invoice.manual_processing = True
            db.session.commit()
            flash('Invoice %d has been submitted for manual process!'%(invoice.id), 'success')
        else:
            flash('You are not the owner!', 'danger')
        return redirect(url_for('view_invoices'))
    abort(403)


@app.route("/viewfields")
@login_required
def view_fields(): 
    if session['account_type']== 'company':
        items = []
        for x in collection.find({"owner_id":current_user.id}):
            checkinvoice = Invoice.query.filter_by(id=x["invoice_id"]).first()
            if checkinvoice !=None:
                del x["_id"]
                del x["owner_id"]
                items.append(x)                
        if len(items)==0:
            flash('No invoices uploaded or processed to view details!', 'danger')
            return redirect(url_for('view_invoices'))
        return render_template('view_fields.html', title='View Details',items = items)
    abort(403)

@app.route("/viewinventory")
@login_required
def view_inventory(): 
    if session['account_type']== 'company':
        comp = Company.query.filter_by(id=current_user.id).first()
        prods = comp.products
        tp = []
        for product in prods:
            actprod = Product.query.filter_by(id=product.product_id).first()
            tp.append([actprod.name,product.quantity,actprod.price,product.product_id])
        if len(tp) == 0:
            flash('No invoices uploaded or processed to view inventory!', 'danger')
            return redirect(url_for('view_invoices'))
        return render_template('view_inventory.html', title='View Inventory',products=tp)
    abort(403)

'''
product specific routing

'''
@app.route("/viewproduct/<int:product_id>/changequantity", methods=['GET', 'POST'])
@login_required
def update_product_quant(product_id):
    if session['account_type'] == 'company':
        company = Company.query.filter_by(id=current_user.id).first()
        invitem = Inventory.query.filter_by(company_id=company.id,product_id=product_id).first()
        actprod = Product.query.filter_by(id=product_id).first()
        form = AssignQuantityForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                invitem.quantity = form.newquantity.data
                db.session.commit()
                flash('%s quantity has been changed to %d' %
                      (actprod.name.title(), form.newquantity.data), 'success')
                return redirect(url_for('view_inventory'))
        elif request.method == 'GET':
            form.newquantity.data = invitem.quantity
        return render_template('assign_quantity.html', title='Update Quantity', form=form)
    abort(403)

@app.route("/viewproduct/<int:product_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_product_quant(product_id):
    if session['account_type'] == 'company':
        print(product_id)
        company = Company.query.filter_by(id=current_user.id).first()
        invitem = Inventory.query.filter_by(company_id=company.id, product_id=product_id).first()
        actprod = Product.query.filter_by(id=product_id).first()
        #invitem = Inventory.query.get_or_404(company_id=company.id,product_id=product_id)
        print(invitem)
        db.session.delete(invitem)
        db.session.commit()
        flash('Product %s has been removed!' %
            (actprod.name.title()), 'success')
        return redirect(url_for('view_inventory'))
    flash('You are not a company!', 'danger')
    abort(403)
    
    
