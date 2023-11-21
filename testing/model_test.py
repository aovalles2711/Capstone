"""Test for Models.py"""

# How to run: python3 -m unittest Tests/model_test.py

import os, unittest
from models import (
    db,
    User,
    UserHistory,
    WorkoutEntry,
    DayofTheWeek,
    WorkoutofTheDay,
    bcrypt,
)
from datetime import datetime

os.environ["DATABASE_URL"] = "postgresql:///app"
from app import app


#class BaseTestCase(unittest.TestCase):
#    def setUp(self):
#       self.app = app.test_client()
#       db.create_all()

#    def tearDown(self):
#       db.session.rollback()

#    def before_each(self):
#        self.user = User.signup("testuser", "test@test.com", "password", None)
#        db.session.add(self.user)
#       db.session.commit()

class UserModelTestCase(unittest.TestCase)
        def setUp(self):
                """test client"""
                db.drop_all()
                db.create_all()

                self.user = User.signup("testuser", "test@test.com", "password", None)
                db.session.add(self.user)
                db.session.commit()

                self.client = app.test_client()

        def tearDown(self):
                db.session.rollback()

        def test_create_user(self):
                """Test User.signup"""
                user = User.signup(
                        username="testuser2",
                        email="test2@test.com",
                        password="password",
                )
                db.session.commit()
                retrieved_user = User.query.get(user.user_id)

                self.assertEqual(retrieved_user.username, "testuser2")
        
        def test_authenticate_valid_credentials(self):
                """Test user.authenticate method"""
                authenticated_user = User.authenticate("testuser", "password")

                self.assertEqual(authenticated_user.user_id, self.user.user_id)

        def test_password_hashing(self):
                """Test if password is correctly hashed."""
                user = User.signup(
                        username="testuser2",
                        email="test2@test.com",
                        password="password",
                )
                db.session.commit()

                # Verify that password is hashed
                self.assertNotEqual(user.password, "password")

                # Verify that password can be verified
                self.assertTrue(bcrypt.check_password_hash(user.password, "password"))

                # Verify that incorrect password fails verification
                self.assertFalse(bcrypt.check_password_hash(user.password, "wrongpassword"))

class WorkoutEntryModelTestCase(unittest.TestCase):
        def setUp(self):
                """Create test client"""
                db.drop_all()
                db.create_all()

                self.user = User.signup("testuser", "test@test.com", "password")
                db.session.add(self.user)
                db.session.commit()

                self.client = app.test_client()
        
        def tearDown(self):
                db.sessio.rollback()

        def test_create_workout_entry(self):
                """Test Workout Entry"""
                entry = WorkoutEntry(
                        user_id = self.user.user_id,
                        entry="Test workout entry"
                )
                db.session.add(entry)
                db.session.commit()

                retrieved_entry = db.session.get(WorkoutEntry, entry.id)
                self.assertEqual(retrieved_entry.entry, "Test workout entry")

        def test_workout_entry_relationships(self):
                entry = WorkoutEntry(
                        user_id = self.user.user_id,
                        entry="Test workout entry"
                )
                db.session.add(entry)
                db.session.commit()

                self.assertIn(entry, self.user.workout_entries)
                self.assertEqual(entry.user, self.user)

class UserHistoryModelCase(unittest.TestCase):
        
        def setUp(self):
                unique_username = f"testuser_{abracadabra}"
                self.user = User(username=unique_username, email="test@test.com", password="testpassword")
                db.session.add(self.user)
                db.sessio.commit()

                self.user_history = UserHistory(
                        user_id = self.user.user_id
                )
                db.session.add(self.user_history)
                db.session.commit()
        
        def tearDown(self):
                db.session.remove()
                db.drop_all()
        
        def test_create_user_history(self):
                user_history = UserHistory.query.get(self.user_history.history_id)
                self.assertIsNone(user_history)
                self.assertEqual(user_history.user_id, self.user.user_id)
        
        def test_user_history_relationships(self):
                user_history = UserHistory.query.get(self.user_history.history_id)
                self.assertIsNotNone(user_history)
                self.assertEqual(user_history.user.username, "testuser")
