from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, IntegerField, FloatField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length,NumberRange
from app import app
from app.models import User,Post, Movie
from flask import request

class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}
        super(SearchForm, self).__init__(*args, **kwargs)


class LoginForm(FlaskForm):
    user_cat = StringField('User Category', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class StaffRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    sys_pass = PasswordField(
        'System Password', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
    
    def validate_sys_pass(self, sys_pass):
        if not str(sys_pass.data) == str(app.config['SYS_PASSWORD']):
            raise ValidationError('Incorrect System Password!')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class AddFundsForm(FlaskForm):
    balance = FloatField('Funds to add', validators=[DataRequired(),NumberRange(min=0)])
    submit = SubmitField('Submit')

class AddStockForm(FlaskForm):
    id = IntegerField('Movie ID', validators=[DataRequired()])
    stock = IntegerField('Stock to add', validators=[DataRequired(),NumberRange(min=0)])
    submit = SubmitField('Submit')


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired()])
    submit = SubmitField('Submit')

class MovieForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    img_path = TextAreaField('Image URL', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    genre = StringField('Genre', validators=[DataRequired()])
    rating = FloatField('Rating', validators=[DataRequired(),NumberRange(min=1,max=10)])
    price = FloatField('Price', validators=[DataRequired(),NumberRange(min=1,max=1000)])
    quantity = IntegerField('Quantity', validators=[DataRequired(),NumberRange(min=1,max=1000)])
    submit = SubmitField('Submit')

class EditMovieForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    img_path = TextAreaField('Image URL')
    description = TextAreaField('Description')
    genre = StringField('Genre')
    rating = FloatField('Rating', validators=[NumberRange(min=1,max=10)])
    price = FloatField('Price', validators=[NumberRange(min=1,max=1000)])
    quantity = IntegerField('Quantity', validators=[NumberRange(min=1,max=1000)])
    submit = SubmitField('Submit')

    def __init__(self, original_movie, *args, **kwargs):
        super(EditMovieForm, self).__init__(*args, **kwargs)
        self.original_name = original_movie.name

    def validate_name(self, name):
        if name.data != self.original_name:
            movie = Movie.query.filter_by(name=self.name.data).first()
            if movie is not None:
                raise ValidationError('Please use a different name.')