# Utility functions that are called to perform tasks when respective buttons are pressed.
from datetime import datetime
from app.models import User, Movie, Order
from app import db
from flask import flash
from fpdf import FPDF
import os
import statistics

# Utility function to implement necessary changes in the database when a movie is rented.
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

# Utility function to generate a PDF receipt of the order of a user.
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
            receipt.image(movie_obj.img_path, x=98, w=25, h=25)
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

            if not os.path.exists('Receipts'):
                os.makedirs('Receipts')
            receipt.output("Receipts/receipt" + str(order_obj.id)+".pdf")
            flash("Receipt Generated Successfully and downloaded.")
        
        else:
            raise KeyError("Order Not Found!")
    except KeyError as e:
        flash(e)

# Utility function to return an outstanding order.
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

# Utility function to return a list of all orders that the user has created on the VRS.
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

# Utility function to search for a movie by its indexed fields.
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
    
# Utility function to generate a PDF audit report of all orders on the VRS.
def audit():
    auditpdf = FPDF()
    try:
        auditpdf.add_page()
        auditpdf.set_font('Arial', 'B', 16)
        auditpdf.cell(200, 10, 'Manager Audit Report', 0, 1, 'C')
        auditpdf.cell(200, 10, 'VRS Movie Rentals', 0, 1, 'C')
        auditpdf.set_font('Arial', '', 12)
        auditpdf.cell(200, 10, 'Audit Date: ' + str(datetime.today().strftime('%Y-%m-%d')), 0, 1, 'C')
        movie_revenue_dict = {}
        total = 0
        revenue_returned = 0
        for order in Order.query.all():
            if order.movie_id in movie_revenue_dict:
                movie_revenue_dict[order.movie_id] += order.price
            else:
                movie_revenue_dict[order.movie_id] = order.price
            total += order.price
            if order.status == "YES":
                revenue_returned += order.price
        auditpdf.set_font('Arial', 'B', 16)
        auditpdf.cell(200, 10, 'Total Revenue: Rs. ' + str(total), 0, 1, 'C')
        auditpdf.cell(200, 10, str(int(100 - (revenue_returned/total*100))) + '% of Rentals Outstanding.', 0, 1, 'C')
        auditpdf.cell(200, 10, 'Top Revenue Generators:', 0, 1, 'C')
        auditpdf.set_font('Arial', '', 12)
        num = max(len(movie_revenue_dict),5)
        col_width = auditpdf.epw / 3 
        line_height = auditpdf.font_size * 2.5
        auditpdf.multi_cell(col_width, line_height, 'Movie ID', border=1, ln=3, max_line_height=auditpdf.font_size)
        auditpdf.multi_cell(col_width, line_height, 'Movie Name', border=1, ln=3, max_line_height=auditpdf.font_size)
        auditpdf.multi_cell(col_width, line_height, 'Revenue', border=1, ln=3, max_line_height=auditpdf.font_size)
        auditpdf.ln(line_height)
        for movieID in sorted(movie_revenue_dict, key=movie_revenue_dict.get, reverse=True)[:num]:
            movie_obj = Movie.query.filter_by(id=movieID).first()
            auditpdf.multi_cell(col_width, line_height, str(movieID), border=1, ln=3, max_line_height=auditpdf.font_size)
            auditpdf.multi_cell(col_width, line_height, str(movie_obj.name), border=1, ln=3, max_line_height=auditpdf.font_size)
            auditpdf.multi_cell(col_width, line_height, 'Rs.' + str(movie_revenue_dict[movieID]), border=1, ln=3, max_line_height=auditpdf.font_size)
            auditpdf.ln(line_height)
        auditpdf.set_font('Arial', 'B', 16)
        auditpdf.cell(200, 10, 'Remaining Inventory:', 0, 1, 'C')
        auditpdf.set_font('Arial', '', 12)
        auditpdf.multi_cell(col_width, line_height, 'Movie ID', border=1, ln=3, max_line_height=auditpdf.font_size)
        auditpdf.multi_cell(col_width, line_height, 'Movie Name', border=1, ln=3, max_line_height=auditpdf.font_size)
        auditpdf.multi_cell(col_width, line_height, 'Quantity Left', border=1, ln=3, max_line_height=auditpdf.font_size)
        auditpdf.ln(line_height) 
        for movie in Movie.query.all():
            auditpdf.multi_cell(col_width, line_height, str(movie.id), border=1, ln=3, max_line_height=auditpdf.font_size)
            auditpdf.multi_cell(col_width, line_height, str(movie.name), border=1, ln=3, max_line_height=auditpdf.font_size)
            auditpdf.multi_cell(col_width, line_height, str(movie.quantity), border=1, ln=3, max_line_height=auditpdf.font_size)
            auditpdf.ln(line_height) 
        if not os.path.exists('Audits'):
            os.makedirs('Audits')
        auditpdf.output("Audits/audit.pdf")
        flash("Audit Generated Successfully and Downloaded.")

    except KeyError as e:
        flash(e)

def generate_reccomendations(user):
    orders = Order.query.filter_by(user_id=user.id).all()
    if orders is None:
        return None
    genre_list=[]
    for order in orders:
        movie = Movie.query.filter_by(id=order.movie_id).first()
        genre_list.append(movie.genre)
    try:
        fav_genre = statistics.mode(genre_list)
    except:
        try:
            fav_genre = max([p[0] for p in statistics._counts(genre_list)])
        except :
            return None
    rec_movies = Movie.query.filter_by(genre=fav_genre).order_by(Movie.rating.desc()).all()
    return rec_movies
