"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
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

    def test_user_model(self):
        u1 = User.query.get(self.u1_id)

        # User should have no messages & no followers
        self.assertEqual(len(u1.authored_messages), 0)
        self.assertEqual(len(u1.followers), 0)

##############################################################################
# is_following tests

    def test_is_following_yes(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)
        u2.followers.append(u1)

        # u1 should be following u2
        self.assertTrue(u1.is_following(u2))

    def test_is_following_no(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        # u1 should not be following u2
        self.assertFalse(u1.is_following(u2))


##############################################################################
# is_followed_by tests

    def test_is_followed_by_yes(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)
        u1.followers.append(u2)

        # u1 should be followed by u2
        self.assertTrue(u1.is_followed_by(u2))

    def test_is_followed_by_no(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        # u1 should not be followed by u2
        self.assertFalse(u1.is_following(u2))


##############################################################################
# User.signup tests

    def test_user_signup_ok(self):
        new_user = User.signup(
            username="test_user",
            email="test_user@email.com",
            password="password",
            image_url=None
        )

        # new_user should equal user added to db
        self.assertEqual(new_user, User.query.filter_by(username="test_user").one())

    def test_user_signup_fail_same_name(self):
        """Test trying to create user with existing username"""

        with self.assertRaises(IntegrityError):
            User.signup(
                username="u1",
                email="test_user@mail.com",
                password="password",
                image_url=None
            )
            db.session.commit()


    def test_user_signup_fail_same_email(self):
        """Test trying to create user with existing email"""

        with self.assertRaises(IntegrityError):
            User.signup(
                username="u3",
                email="u1@email.com",
                password="password",
                image_url=None
            )
            db.session.commit()

    def test_user_signup_fail_no_pw(self):
        """Test trying to create user with no password"""

        with self.assertRaises(ValueError):
            User.signup(
                username="u3",
                email="u3@email.com",
                password=None,
                image_url=None
            )
            db.session.commit()

##############################################################################
# User.authenticate tests

