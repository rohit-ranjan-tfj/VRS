
from app.models import User, Movie, Order
from app import db
from time import time
from flask import flash

def purchase_movie(user_id, movie_id, qty):
    try:
        #get movie details
        user_obj = User.query.filter_by(id=user_id).first() #sure to exist
        movie_obj = Movie.query.filter_by(id=movie_id).first()

        if movie_obj is not None:    
            #check for funds, and stock, and existence of movie
            if user_obj.balance < movie_obj.price :
                raise ValueError("Insufficient Balance")
            elif movie_obj.qty < qty :
                raise ValueError("Insufficient Quantity in Stock")
            else:
                my_order = Order(user_id = user_obj.id, movie_id = movie_id, timestamp = time(),
                status="NO", price = movie_obj.price, quantity = qty)
                movie_obj.qty -= qty
                db.session.add(my_order)
                db.session.commit()
                flash('Congratulations. Purchase Successful')
        else:
            raise ValueError("Movie Not Found!")

    except ValueError as e:
        print(e)