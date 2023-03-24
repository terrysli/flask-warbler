"""User view function tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Like
from app import CURR_USER_KEY

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Don't req CSRF for testing
app.config['WTF_CSRF_ENABLED'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserRoutesTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()


    def test_list_users(self):
        """Test page listing all users"""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            resp = client.get("/users")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("u2", html)


    def test_show_user(self):
        """Test page showing user profile"""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            resp = client.get(f"/users/{self.u1_id}", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("u1", html)
            self.assertIn("<!-- Test: show page -->", html)


    def test_show_following_logged_in(self):
        """Test page showing people user is following if logged in"""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            resp = client.get(f"/users/{self.u1_id}/following")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!-- Test: following page -->", html)


    def test_show_following_logged_out(self):
        """Test following page is blocked if not logged in"""

        with app.test_client() as client:
            resp = client.get(
                f"/users/{self.u1_id}/following",
                follow_redirects=True
            )
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!-- Test: home-anon page -->", html)

    def test_show_followers_logged_in(self):
            """Test page showing people following user if logged in"""

            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.u1_id
                resp = client.get(f"/users/{self.u1_id}/followers")
                html = resp.get_data(as_text=True)
                self.assertEqual(resp.status_code, 200)
                self.assertIn("<!-- Test: followers page -->", html)


    def test_show_followers_logged_out(self):
        """Test followers page is blocked if not logged in"""

        with app.test_client() as client:
            resp = client.get(
                f"/users/{self.u1_id}/followers",
                follow_redirects=True
            )
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!-- Test: home-anon page -->", html)

    def test_start_following_logged_in(self):
        """Test following a person if user is logged in"""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            resp = client.post(f"/users/follow/{self.u2_id}")
            u1 = User.query.get(self.u1_id)
            u2 = User.query.get(self.u2_id)
            self.assertEqual(u2.followers, [u1])

