# Utility functions to handle errors in the application
from flask import render_template
from app import app, db

# route decorator for 404 errors
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

# route decorator for 500 errors
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
