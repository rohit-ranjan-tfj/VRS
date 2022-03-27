from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, StaffRegistrationForm, EditProfileForm, \
    EmptyForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm, MovieForm
from app.models import User, Post, Movie
from app.email import send_password_reset_email


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/index_user', methods=['GET', 'POST'])
@login_required
def index_user():
    page = request.args.get('page', 1, type=int)
    movies = Movie.query.order_by(Movie.timestamp.desc()).paginate(
        page, app.config['MOVIES_PER_PAGE'], False)
    next_url = url_for('explore', page=movies.next_num) \
        if movies.has_next else None
    prev_url = url_for('explore', page=movies.prev_num) \
        if movies.has_prev else None

    return render_template('index.html', title='Home', form=None,
                           movies=movies.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/index_staff', methods=['GET', 'POST'])
@login_required
def index_staff():
    if request.form.get('Add Movie') == 'Add Movie':
        return redirect(url_for('add_movie'))

    return render_template('index.html', title='Home')


@app.route('/index_manager', methods=['GET', 'POST'])
@login_required
def index_manager():
    if request.form.get('Add Movie') == 'Add Movie':
        return redirect(url_for('add_movie'))

    return render_template('index.html', title='Home')                                                      


@app.route('/')
@app.route('/explore')
def explore():
    page = request.args.get('page', 1, type=int)
    movies = Movie.query.order_by(Movie.timestamp.desc()).paginate(
        page, app.config['MOVIES_PER_PAGE'], False)
    next_url = url_for('explore', page=movies.next_num) \
        if movies.has_next else None
    prev_url = url_for('explore', page=movies.prev_num) \
        if movies.has_prev else None
    return render_template('index.html', title='Explore', movies=movies.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated :
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = LoginForm()
    if form.validate_on_submit():
        cat = form.user_cat.data
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data) or user.user_cat != cat:
            flash('Invalid credentials')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index'+"_" + current_user.user_cat)
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('explore'))


@app.route('/register', methods=['GET', 'POST'])
def register(user_cat = "user"):
    if current_user.is_authenticated:
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = RegistrationForm()
    if form.validate_on_submit():

        user = User(username=form.username.data, email=form.email.data,user_cat = user_cat)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/staff_register', methods=['GET', 'POST'])
def staff_register(user_cat = "staff"):
    if current_user.is_authenticated:
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = StaffRegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data,user_cat = user_cat)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered staff!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'+"_" + current_user.user_cat))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)


@app.route('/movie/<id>')
@login_required
def movie(id):
    movie = Movie.query.filter_by(id=id).first_or_404()
    page = request.args.get('page', 1, type=int)
    movies = Movie.query.order_by(Movie.timestamp.desc()).paginate(
        page, app.config['MOVIES_PER_PAGE'], False)
    next_url = url_for('movie',id=Movie.query.order_by(Movie.id.data)[-1], page=movies.next_num) \
        if movies.has_next else None
    prev_url = url_for('movie',id=Movie.query.order_by(Movie.id.data)[0], page=movies.prev_num) \
        if movies.has_prev else None
    return render_template('movie.html', movie=movie, movies=movies.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'+"_" + current_user.user_cat))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'+"_" + current_user.user_cat))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'+"_" + current_user.user_cat))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'+"_" + current_user.user_cat))

@app.route('/add_movie', methods=['GET', 'POST'])
@login_required
def add_movie():
    if request.form.get('Back to Dashboard') == 'Back to Dashboard':
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = MovieForm()
    if form.validate_on_submit():
        movie = Movie(name=form.name.data,description = form.description.data, genre = form.genre.data,rating=form.rating.data,price = form.price.data,quantity=form.quantity.data, img_path=form.img_path.data)
        db.session.add(movie)
        db.session.commit()
        flash('The movie is now live on the store!')
        return redirect(url_for('add_movie'))
    return render_template('add_movie.html', title='Home', form=form)