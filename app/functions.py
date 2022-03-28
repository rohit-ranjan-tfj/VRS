from datetime import datetime
from app.models import User, Movie, Order
from app import db
from flask import flash
from fpdf import FPDF

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

def generate_receipt(order_id):
    try:
        order_obj = Order.query.filter_by(id=order_id).first()
        movie_obj = Movie.query.filter_by(id=order_obj.movie_id).first()
        user_obj = User.query.filter_by(id=order_obj.user_id).first()

        if order_obj is not None and movie_obj is not None and user_obj is not None:
            receipt = FPDF()
            receipt.add_page()
            receipt.set_font('Arial', 'B', 16)
            receipt.cell(200, 10, 'VRS Movie Rentals', 0, 1, 'C')
            receipt.cell(200, 10, 'Receipt', 0, 1, 'C')
            receipt.set_font('Arial', '', 12)
            receipt.cell(200, 10, 'Order ID: {}'.format(order_obj.id), 0, 1, 'L')
            receipt.cell(200, 10, txt=f"Customer ID: {order_obj.user_id}", ln=1, align="L")
            receipt.cell(200, 10, txt=f"Customer Name: {user_obj.username}", ln=1, align="L")
            receipt.cell(200, 10, txt=f"Movie ID: {order_obj.movie_id}", ln=1, align="L")   
            receipt.cell(200, 10, txt=f"Movie Name: {movie_obj.name}", ln=1, align="L")
            receipt.cell(200, 10, txt=f"Movie Genre: {movie_obj.genre}", ln=1, align="L")
            receipt.cell(200, 10, txt=f" Date: {order_obj.timestamp.date()}", ln=1, align="L")
            receipt.set_font('Arial', 'B', 16)
            if order_obj.status=="YES":
                receipt.cell(200, 10, txt=f"Status: Returned", ln=1, align="C")
            else:
                receipt.cell(200, 10, txt=f"Status: Not Returned", ln=1, align="C")
            receipt.cell(200, 10, txt=f"Total Price: {order_obj.price}", ln=1, align="C")
            receipt.output("Receipts/receipt" + str(order_obj.id)+".pdf")
            flash("Receipt Generated Successfully and downloaded.")
        
        else:
            raise KeyError("Order Not Found!")
    except KeyError as e:
        flash(e)

def return_movie( order_id):
    try:
        
        order_obj = Order.query.filter_by(id=order_id).first()

        if order_obj is not None:
            if order_obj.status == "YES":
                raise ValueError("Movie already returned.")
            else:
                order_obj.status = "YES"
                order_obj.returned = datetime.utcnow()
                db.session.commit()
                flash("Movie returned successfully.")
        else:
            raise ValueError("Order Not Found!")

    except ValueError as e:
        flash(e)

def view_orders(user_id):
    try:
        user_obj = User.query.filter_by(id=user_id).first()

        if user_obj is not None:
            if (user_obj.user_cat == 'user'):
                return(Order.query.filter_by(user_id=user_id))
            else:
                flash('Applicable for users only.')
        else:
            raise KeyError("User Not Found!")

    except KeyError as e:
        flash(e)
    return None

def search_movies(keyword):
    for movie in Movie.query.order_by(Movie.name):
        if keyword in movie.name or keyword in movie.genre or keyword in movie.description:
            flash(movie.id)
            flash(movie.name)
            flash(movie.genre)
            flash(movie.price)
            flash(movie.qty)
            flash("\n")
    flash("Search complete.")
    
    
def audit():
    auditpdf = FPDF()
    try:
        auditpdf.add_page()
        auditpdf.set_font('Arial', 'B', 16)
        auditpdf.cell(200, 10, 'Audit', 0, 1, 'C')
        auditpdf.set_font('Arial', '', 12)

        total = 0
        for order in Order.query.all():
            auditpdf.cell(200, 10, 'Order ID: ' + str(order.id) + ', Price: '+ str(order.price), 0, 1, 'L')
            total += order.price
        auditpdf.cell(200, 10, 'Total Revenue: ' + str(total), 0, 0, 'C')
        
        auditpdf.output("Audits/audit.pdf")
        flash("Audit Generated Successfully and downloaded.")

    except KeyError as e:
        flash(e)