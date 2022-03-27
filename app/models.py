from datetime import datetime
from hashlib import md5
from re import S
from time import time
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import app, db, login
from fpdf import FPDF


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

renters = db.Table(
    'renters',
    db.Column('renter_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('rented_id', db.Integer, db.ForeignKey('movie.id'))
)


class User(UserMixin, db.Model):
    user_cat = db.Column(db.String(64), index=True)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    balance = db.Column(db.Integer, default=0)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    def view_balance(self):
        if (self.user_cat == 'user'):
            if not self.balance:
                self.balance = 0
            print('Your balance is Rs. {}'.format(self.balance))
        
        else:
            print('Applicable for users only.')

    def add_balance(self, amount):
        if (self.user_cat == 'user'):
            try:
                if amount <0:
                    raise ValueError('Amount must be positive')
            except ValueError as ve:
                print(ve)
                return
            
            if not self.balance:
                self.balance = 0
            self.balance = amount + self.balance
            print("Amount added successfully. Your new balance is Rs. {}".format(self.balance))
        
        else:
            print('Applicable for users only.')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    img_path = db.Column(db.String(140))
    description = db.Column(db.String(140))
    genre = db.Column(db.String(40))
    rating = db.Column(db.Float)
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    rented_by = db.relationship(
        'User', secondary=renters,
        primaryjoin=(renters.c.rented_id == id),
        secondaryjoin=(renters.c.renter_id == id),
        backref=db.backref('rented', lazy='dynamic'), lazy='dynamic')
    
    def __repr__(self):
        return '<Movie {} {} {} {} {}>'.format(self.id, self.name, self.genre, self.rating, self.price)

    def rent(self, user):
        if not self.is_rented(user):
            self.rented_by.append(user)

    def unrent(self, user):
        if self.is_rented(user):
            self.rented_by.remove(user)

    def is_rented(self, user):
        try :
            if(self.rented_by.all().index(user)>=0):
                return True
        except :
            return False


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    status = db.Column(db.String(40))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    
    def __repr__(self):
        return '<Order {} {} {} {}>'.format(self.id, self.user_id, self.movie_id, self.timestamp)

    def generate_receipt(self):
        receipt = FPDF()
        receipt.add_page()
        receipt.set_font('Arial', 'B', 16)
        receipt.cell(200, 10, 'Movie Rentals', 0, 1, 'C')
        receipt.set_font('Arial', '', 12)
        receipt.cell(200, 10, 'Order ID: {}'.format(self.id), 0, 1, 'C')
        receipt.cell(200, 10, txt=f"Movie ID: {self.movie_id}", ln=1, align="C")
        receipt.cell(200, 10, txt=f"Customer ID: {self.user_id}", ln=1, align="C")
        receipt.cell(200, 10, txt=f"Total Price: {self.price}", ln=1, align="C")
        receipt.cell(200, 10, txt=f" Date: {self.timestamp}", ln=1, align="C")
        #receipt.cell(200, 10, txt=f"End Date: {self.endDate}", ln=1, align="C")
        receipt.cell(200, 10, txt=f"Order Status: {self.status}", ln=1, align="C")
        receipt.output("receipt" + str(self.id)+".pdf")

    
            
        
