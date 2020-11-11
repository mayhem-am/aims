from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['MONGO_URI'] = 'mongodb+srv://admin:1234@cluster0.zpmg5.mongodb.net/test?retryWrites=true&w=majority' 
"""
mongodb+srv://admin:1234@cluster0.djdta.mongodb.net/ <dbname> ?retryWrites=true&w=majority      #akanksham.cs18@rvce.edu.in  <available database : mongodb>
mongodb+srv://admin:1234@cluster0.zpmg5.mongodb.net/  <dbname>  ?retryWrites=true&w=majority    #amakanksh@gmail.com <available database : test>
<dbname> == database leading to collection u want to use
"""
db = SQLAlchemy(app)
mongo = PyMongo(app)
mongodb = mongo.db
collection = mongodb["test"] #collection
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from aims_ import routes