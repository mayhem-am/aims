from aims_ import db, login_manager
from flask_login import UserMixin
from aims_.routes import session

@login_manager.user_loader
def load_user(user_id):
    if 'account_type' in session:
        if session['account_type'] == 'broker':
            return Broker.query.get(int(user_id))
        elif session['account_type'] == 'admin':
            return Admin.query.get(int(user_id))
        elif session['account_type'] == 'company':
            return Company.query.get(int(user_id))
        else:
            return None
    else:
        return None


class Broker(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"Broker('{self.username}', '{self.email}', '{self.image_file}')"

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"Admin('{self.username}', '{self.email}', '{self.image_file}')"

class Company(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"Company('{self.username}', '{self.email}', '{self.image_file}')" 

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_file =  db.Column(db.String(20), nullable=False)
    coors_file =  db.Column(db.String(20), nullable=False)
    broker_id = db.Column(db.Integer, db.ForeignKey('broker.id'),nullable = True)
    owner_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)


'''
PRODUCT -->

invoice id - fk
company id - fk
amount
name
id
quantity
'''