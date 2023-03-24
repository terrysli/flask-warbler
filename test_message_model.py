"""Message model tests."""

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


class MessageModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        msg = Message(text="Sample Text", user_id=self.u1_id)

        db.session.add(msg)
        db.session.commit()
        self.u1_msg_id = msg.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

##############################################################################
# Test message and author relationship

    def test_message_author_valid(self):
        """Test that message has only the expected author"""

        msg = Message.query.filter_by(id=self.u1_msg_id).one()

        self.assertEqual(msg.author.id, self.u1_id)

    def test_message_author_invalid(self):
        """Test that message will not accept author who does not exist"""

        with self.assertRaises(IntegrityError):
            #create new message instance with user id that doesnt exist
            msg = Message(text="Sample Text", user_id=1000)

            db.session.add(msg)
            db.session.commit()


##############################################################################
# Test message and users_who_liked relationship

    def test_message_users_who_liked_valid(self):
        """Test that a message has expected list of users who like"""

    def test_message_users_who_liked_invalid(self):
        """
        Test that a message will not accept like from user who does not exist
        """