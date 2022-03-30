# Unit Tests for our application.
#!/usr/bin/env python
from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Movie, Order

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))

    def test_username(self):
        u = User(username='john')
        self.assertTrue(u.getName() == 'john')
        u.setName('susan')
        self.assertFalse(u.getName() == 'john')
        self.assertTrue(u.getName() == 'susan')

    def test_category(self):
        u = User(username='john', user_cat='manager')
        self.assertTrue(u.getCategory() == 'manager')
        u = User(username='john', user_cat='customer')
        self.assertTrue(u.getCategory() == 'customer')

    def test_email(self):
        u = User(username='john',email='test@gmail.com')
        self.assertTrue(u.getEmail() == 'test@gmail.com')
    
class MovieModelCase(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_id(self):
        url = 'https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_.jpg'
        m = Movie(id='25', name='test', img_path=url, description='test', genre='test', rating=0.0, price=0.0)
        self.assertTrue(m.getID() is not None)

    def test_name(self):
        url = 'https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_.jpg'
        m = Movie(name='test', img_path=url, description='test', genre='test', rating=0.0, price=0.0)
        self.assertTrue(m.getName() == 'test')

    def test_price(self):
        url = 'https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_.jpg'
        m = Movie(name='test', img_path=url, description='test', genre='test', rating=0.0, price=2.0)
        self.assertTrue(m.getPrice() == 2.0)

    def test_description(self):
        url = 'https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_.jpg'
        m = Movie(name='test', img_path=url, description='test', genre='test', rating=0.0, price=0.0)
        self.assertTrue(m.getDescription() == 'test')

class OrderModelCase(unittest.TestCase):
    
        def setUp(self):
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
            db.create_all()
    
        def tearDown(self):
            db.session.remove()
            db.drop_all()
    
        def test_id(self):
            o = Order(id='25', movie_id='25', user_id='25', quantity=1, price=2.0, timestamp=datetime.now())
            self.assertTrue(o.getID() is not None)
    
        def test_order_status(self):
            o = Order(id='25', movie_id='25', user_id='25', quantity=1, price=2.0, timestamp=datetime.now(), status='NO')
            self.assertTrue(o.getStatus() == 'NO')

        def test_user_id(self):
            o = Order(id='25', movie_id='25', user_id='25', quantity=1, price=2.0, timestamp=datetime.now())
            self.assertTrue(o.getUserID() == '25')

        def test_movie_id(self):
            o = Order(id='25', movie_id='25', user_id='25', quantity=1, price=2.0, timestamp=datetime.now())
            self.assertTrue(o.getMovieID() == '25')
            
        def test_timestamp(self):
            o = Order(id='25', movie_id='25', user_id='25', quantity=1, price=2.0, timestamp=datetime.now())
            self.assertTrue(o.getTimestamp() is not None)

        def test_deadline(self):
            o = Order(id='25', movie_id='25', user_id='25', quantity=1, price=2.0, timestamp=datetime.now(), deadline = '2023-01-01')
            self.assertTrue(o.getDeadline() is not None)


if __name__ == '__main__':
    unittest.main(verbosity=2)
