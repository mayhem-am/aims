from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from aims_.models import Broker, Admin,Company


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    
    role = StringField('Role',validators=[DataRequired()])

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        role = self.role.data.lower()
        if role == 'broker':
            user = Broker.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username as User role is taken. Please choose a different one.')
        elif role == 'admin':
            user = Admin.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username as Tester role is taken. Please choose a different one.')
        elif role == 'company':
            user = Company.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username as Tester role is taken. Please choose a different one.')
        else:
            raise ValidationError('Invalid role entered.')

    def validate_email(self, email):
        role = self.role.data.lower()
        if role == 'broker':
            user = Broker.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email as User role is taken. Please choose a different one.')
        elif role == 'admin':
            user = Admin.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email as Tester role is taken. Please choose a different one.')
        elif role == 'company':
            user = Company.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email as Tester role is taken. Please choose a different one.')
        else:
            raise ValidationError('Invalid role entered.')
    
    def validate_role(self, role):
        role = role.data.lower()
        if role not in ["admin","broker","company"]:
            raise ValidationError('Your role is undefined. Please choose one from Broker, Admin or Company.')


class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    role = StringField('Role',validators=[DataRequired()])
    submit = SubmitField('Login')

    def validate_role(self, role):
        role = role.data.lower()
        if role not in ["admin","broker","company"]:
            raise ValidationError('Your role is undefined. Please choose one from  Broker, Admin or Company.')