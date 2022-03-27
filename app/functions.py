from app.models import User, Movie, Order
from app import db
from flask import flash

def rent_movie(user_id, movie_id, qty=1):
    try:
        #get movie details
        user_obj = User.query.filter_by(id=user_id).first() #sure to exist
        movie_obj = Movie.query.filter_by(id=movie_id).first()

        if movie_obj is not None:    
            #check for funds, and stock, and existence of movie
            if user_obj.balance < movie_obj.price*qty :
                raise ValueError("Insufficient Balance")
            elif movie_obj.quantity < qty :
                raise ValueError("Insufficient Quantity in Stock")
            else:
                my_order = Order(user_id = user_obj.id, movie_id = movie_id,
                status="NO", price = movie_obj.price, quantity = qty)
                movie_obj.quantity -= qty
                user_obj.balance -= movie_obj.price*qty
                db.session.add(my_order)
                db.session.commit()
                flash('Congratulations. Movie Rented Successful')
        else:
            raise ValueError("Movie Not Found!")

    except ValueError as e:
        flash(e)