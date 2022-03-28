from keyring import set_password
from app import app, db
from werkzeug.security import generate_password_hash
from app.models import User, Movie, Order


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Movie': Movie, 'Order': Order}

if(User.query.filter_by(username='admin').first() is None):
    admin = User(user_cat='manager',username='admin',email='admin@gmail.com')
    admin.password_hash = generate_password_hash(app.config['ADMIN_PASSWORD'])
    db.session.add(admin)
    db.session.commit()