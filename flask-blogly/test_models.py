from unittest import TestCase
from app import app
from models import db, User, Post, DEFAULT_IMAGE

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///blogly_test"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True


db.drop_all()
db.create_all()

class ModelsTestCase(TestCase):

    def setUp(self):
        """ setup checks for models setup"""

        # user creation test
        user = User(first_name="John", last_name="Doe")
        db.session.add(user)
        db.session.commit()

        self.user = user

    def tearDown(self):
        """ teardown session from any bad commits or adds"""

        db.session.rollback()

        User.query.delete()

    def test_default_url(self):
        """checks if default url is used"""

        user = User(first_name="John", last_name="Doe")
        image_url = user.image_url

        self.assertFalse(image_url)
        db.session.add(user)
        db.session.commit()
        image_url = user.image_url
        self.assertTrue(image_url)

