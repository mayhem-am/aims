# import os
# import secrets
# from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
# from aims_ import app, db, bcrypt
from aims_ import app
# from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
# from flaskblog.models import User, Post
#from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template('about.html', title='About')