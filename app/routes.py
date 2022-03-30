# This file contains all the route registrations for the application.
# Routes are called when a specific url is requested by the user.
from datetime import datetime
from locale import getlocale
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import *
from app.models import User, Movie, Order
from app.email import send_password_reset_email
from app.functions import *
from flask import g

# Required setup for the search bar.
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

    g.search_form = SearchForm()
    g.locale = str(getlocale())

# Dashboard for customer user.
@app.route('/index_user', methods=['GET', 'POST'])
@login_required
def index_user():
    if str(request.form.get('Rent Movie'))[:10] == 'Rent Movie':
        rent_movie(current_user.id, int(str(request.form.get('Rent Movie'))[14:]))

    if request.form.get('View Orders') == 'View Orders':
        orders = view_orders(current_user.id)
        order_list=[]
        for order in orders:
            movie = Movie.query.filter_by(id = order.movie_id).first()
            order_list.append((order,movie))
        if len(order_list)>0:
            return render_template('index.html', order_list=order_list)
        else:
            flash('No orders found.')
            return render_template('index.html', title='Home')
    
    if request.form.get('View Deadlines') == 'View Deadlines':
        orders = view_orders(current_user.id)
        order_list=[]
        for order in orders:
            movie = Movie.query.filter_by(id = order.movie_id).first()
            if order.status == 'NO':
                order_list.append((order,movie))
        if len(order_list)>0:
            return render_template('index.html', order_list=order_list)
        else:
            flash('No approaching deadlines found.')
            return render_template('index.html', title='Home')
    
    if str(request.form.get("Return Order"))[:12] == "Return Order":
        return_movie(int(str(request.form.get('Return Order'))[16:]))

    if str(request.form.get("Generate Receipt"))[:16] == "Generate Receipt":
        generate_receipt(int(str(request.form.get('Generate Receipt'))[30:]))
    rec_movies = generate_reccomendations(current_user)
    return render_template('index.html', title='Home',rec_movies=rec_movies)

# Dashboard for staff user
@app.route('/index_staff', methods=['GET', 'POST'])
@login_required
def index_staff():
    if request.form.get('Add Movie') == 'Add Movie':
        return redirect(url_for('add_movie'))

    if request.form.get('View Users') == 'View Users':
        page = request.args.get('page', 1, type=int)
        users = User.query.filter_by(user_cat='user').order_by(User.id.desc()).paginate(
            page, app.config['USERS_PER_PAGE'], False)
        next_url = url_for('explore', page=users.next_num) \
            if users.has_next else None
        prev_url = url_for('explore', page=users.prev_num) \
            if users.has_prev else None
        return render_template('index.html', title='Home', users=users.items,
                            next_url=next_url, prev_url=prev_url)

    if str(request.form.get('View Orders'))[:11] == 'View Orders':
        orders = view_orders(int(str(request.form.get('View Orders'))[23:]))
        order_list=[]
        for order in orders:
            movie = Movie.query.filter_by(id = order.movie_id).first()
            order_list.append((order,movie))
        if len(order_list)>0:
            return render_template('index.html', order_list=order_list)
        else:
            flash('No orders found.')
            return render_template('index.html', title='Home')

    if str(request.form.get('View Deadlines'))[:14] == 'View Deadlines':
        orders = view_orders(int(str(request.form.get('View Deadlines'))[26:]))
        order_list=[]
        for order in orders:
            movie = Movie.query.filter_by(id = order.movie_id).first()
            if order.status == 'NO':
                order_list.append((order,movie))
        if len(order_list)>0:
            return render_template('index.html', order_list=order_list)
        else:
            flash('No approaching deadlines found.')
            return render_template('index.html', title='Home')

    if str(request.form.get('Delete User'))[:11] == 'Delete User':
        tbd_user = User.query.filter_by(id = int(str(request.form.get('Delete User'))[15:])).first()
        if tbd_user is not None:
            db.session.delete(tbd_user)
            db.session.commit()
            flash('User deleted.')
        else:
            flash('User not found.')
    
    if str(request.form.get("Return Order"))[:12] == "Return Order":
        return_movie(int(str(request.form.get('Return Order'))[16:]))
    
    if str(request.form.get("Generate Receipt"))[:16] == "Generate Receipt":
        generate_receipt(int(str(request.form.get('Generate Receipt'))[30:]))
                                
    return render_template('index.html', title='Home')

# Dashboard for manaager user.
@app.route('/index_manager', methods=['GET', 'POST'])
@login_required
def index_manager():
    if request.form.get('Add Movie') == 'Add Movie':
        return redirect(url_for('add_movie'))

    if request.form.get('View Users') == 'View Users':
        page = request.args.get('page', 1, type=int)
        users = User.query.filter_by(user_cat='user').order_by(User.id.desc()).paginate(
            page, app.config['USERS_PER_PAGE'], False)
        next_url = url_for('explore', page=users.next_num) \
            if users.has_next else None
        prev_url = url_for('explore', page=users.prev_num) \
            if users.has_prev else None
        return render_template('index.html', title='Home', users=users.items,
                            next_url=next_url, prev_url=prev_url)

    if request.form.get('View Staff') == 'View Staff':
        page = request.args.get('page', 1, type=int)
        users = User.query.filter_by(user_cat='staff').order_by(User.id.desc()).paginate(
            page, app.config['USERS_PER_PAGE'], False)
        next_url = url_for('explore', page=users.next_num) \
            if users.has_next else None
        prev_url = url_for('explore', page=users.prev_num) \
            if users.has_prev else None
        return render_template('index.html', title='Home', users=users.items,
                            next_url=next_url, prev_url=prev_url)

    if str(request.form.get('View Orders'))[:11] == 'View Orders':
        orders = view_orders(int(str(request.form.get('View Orders'))[23:]))
        order_list=[]
        for order in orders:
            movie = Movie.query.filter_by(id = order.movie_id).first()
            order_list.append((order,movie))
        if len(order_list)>0:
            return render_template('index.html', order_list=order_list)
        else:
            flash('No orders found.')
            return render_template('index.html', title='Home')

    if str(request.form.get('View Deadlines'))[:14] == 'View Deadlines':
        orders = view_orders(int(str(request.form.get('View Deadlines'))[26:]))
        order_list=[]
        for order in orders:
            movie = Movie.query.filter_by(id = order.movie_id).first()
            if order.status == 'NO':
                order_list.append((order,movie))
        if len(order_list)>0:
            return render_template('index.html', order_list=order_list)
        else:
            flash('No approaching deadlines found.')
            return render_template('index.html', title='Home')

    if str(request.form.get('Delete User'))[:11] == 'Delete User':
        tbd_user = User.query.filter_by(id = int(str(request.form.get('Delete User'))[15:])).first()
        if tbd_user is not None:
            db.session.delete(tbd_user)
            db.session.commit()
            flash('User deleted.')
        else:
            flash('User not found.')
    
    if str(request.form.get("Return Order"))[:12] == "Return Order":
        return_movie(int(str(request.form.get('Return Order'))[16:]))
    
    if str(request.form.get("Generate Receipt"))[:16] == "Generate Receipt":
        generate_receipt(int(str(request.form.get('Generate Receipt'))[30:]))
    
    if request.form.get("Audit") == "Audit":
        audit()
    
    return render_template('index.html', title='Home')
                                                     
# The landing page.
@app.route('/', methods=['GET', 'POST'])
def landing():
    return redirect(url_for('explore'))

# All movies can be explored via the explore page.
@app.route('/explore', methods=['GET', 'POST'])
def explore():
    if str(request.form.get('Rent Movie'))[:10] == 'Rent Movie':
        rent_movie(current_user.id, int(str(request.form.get('Rent Movie'))[14:]))
    page = request.args.get('page', 1, type=int)
    movies = Movie.query.order_by(Movie.timestamp.desc()).paginate(
        page, app.config['MOVIES_PER_PAGE'], False)
    next_url = url_for('explore', page=movies.next_num) \
        if movies.has_next else None
    prev_url = url_for('explore', page=movies.prev_num) \
        if movies.has_prev else None
    return render_template('explore.html', title='Explore', movies=movies.items,
                           next_url=next_url, prev_url=prev_url)

# Login page.
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

# Logout page.
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('explore'))

# Registration page for customer user.
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

# Registration page for staff user.
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

# Reset Password request page.
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

# Reset Password page.
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

# Personal profile for each user.
@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    return render_template('user.html', user=user)

# Personal page for each movie.
@app.route('/movie/<id>', methods=['GET', 'POST'])
def movie(id):
    if str(request.form.get('Rent Movie'))[:10] == 'Rent Movie':
        if(current_user.is_authenticated):
            rent_movie(current_user.id, int(str(request.form.get('Rent Movie'))[14:]))
        else:
            flash('Please login to rent a movie')
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

# Edit Profile page.
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

# Edit Movie page.
@app.route('/edit_movie/<id>', methods=['GET', 'POST'])
@login_required
def edit_movie(id):
    movie = Movie.query.filter_by(id=id).first_or_404()
    if movie is None:
        flash('Movie not found')
        return redirect(url_for('explore'))
    form = EditMovieForm(movie)
    if form.validate_on_submit():
        if form.name.data is not None:
            movie.name = form.name.data
        if form.img_path.data is not None:
            movie.img_path = form.img_path.data
        if form.description.data is not None:
            movie.description = form.description.data
        if form.genre.data is not None:
            movie.genre = form.genre.data
        if form.rating.data is not None:
            movie.rating = form.rating.data
        if form.price.data is not None:
            movie.price = form.price.data
        if form.quantity.data is not None:
            movie.quantity = form.quantity.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('explore'))
    elif request.method == 'GET':
        form.name.data = movie.name
        form.img_path.data = movie.img_path
        form.description.data = movie.description
        form.genre.data = movie.genre
        form.rating.data = movie.rating
        form.price.data = movie.price
        form.quantity.data = movie.quantity
    return render_template('add_movie.html', title='Edit Movie',
                           form=form)

# Add funds page.
@app.route('/add_funds', methods=['GET', 'POST'])
@login_required
def add_funds():
    form = AddFundsForm()
    if form.validate_on_submit():
        current_user.balance += form.balance.data
        db.session.commit()
        flash('Funds successfully added.')
        return redirect(url_for('user',username=current_user.username))
    elif request.method == 'GET':
        form.balance.data = current_user.balance
    return render_template('add_funds.html', title='Add Funds',
                           form=form)

# Add stock page.
@app.route('/add_stock', methods=['GET', 'POST'])
@login_required
def add_stock():
    form = AddStockForm()
    if form.validate_on_submit():
        movie = Movie.query.filter_by(id=form.id.data).first_or_404()
        if movie is None:
            flash('Movie not found')
            return redirect(url_for('add_stock'))
        movie.quantity += form.stock.data
        db.session.commit()
        flash('Stock successfully added.')
        return redirect(url_for('movie',id=form.id.data))

    return render_template('add_funds.html', title='Add Stock of Movie',
                           form=form)

# Add movie page.
@app.route('/add_movie', methods=['GET', 'POST'])
@login_required
def add_movie():
    if request.form.get('Back to Dashboard') == 'Dashboard':
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = MovieForm()
    if form.validate_on_submit():
        movie = Movie(name=form.name.data,description = form.description.data, genre = form.genre.data,rating=form.rating.data,price = form.price.data,quantity=form.quantity.data, img_path=form.img_path.data)
        db.session.add(movie)
        db.session.commit()
        flash('The movie is now live on the store!')
        return redirect(url_for('add_movie'))
    return render_template('add_movie.html', title='Home', form=form)

# Search page.
@app.route('/search', methods=['GET', 'POST'])
def search():
    if str(request.form.get('Rent Movie'))[:10] == 'Rent Movie':
        if(current_user.is_authenticated):
            rent_movie(current_user.id, int(str(request.form.get('Rent Movie'))[14:]))
        else:
            flash("Login to rent the movie.")
        
    if not g.search_form.validate():
        return redirect(url_for('explore'))
    page = request.args.get('page', 1, type=int)
    movies, total = Movie.search(g.search_form.q.data, page,
                               app.config['MOVIES_PER_PAGE'])
    next_url = url_for('search', q=g.search_form.q.data, page=page + 1) \
        if total > page * app.config['MOVIES_PER_PAGE'] else None
    prev_url = url_for('search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title='Search', movies=movies,
                           next_url=next_url, prev_url=prev_url)