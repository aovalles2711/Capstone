from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

# SQLalchemy instance
db = SQLAlchemy()

# Hash password via Bcrypt
bcrypt = Bcrypt()

# many-to-many tables
user_groups = db.Table(
    "user_groups",
    db.Column("user_id", db.Integer, db.ForeignKey("users.user_id")),
    db.Column("group_id", db.Integer, db.ForeignKey("groups.group_id")),
    extend_existing=True,
)

user_friends = db.Table(
    "user_friends",
    db.Column("user_id", db.Integer, db.ForeignKey("users.user_id"), primary_key=True),
    db.Column(
        "friend_id", db.Integer, db.ForeignKey("users.user_id"), primary_key=True
    ),
)

user_friend_requests = db.Table(
    "user_friend_requests",
    db.Column(
        "sender_id", db.Integer, db.ForeignKey("users.user_id"), primary_key=True
    ),
    db.Column(
        "receiver_id", db.Integer, db.ForeignKey("users.user_id"), primary_key=True
    ),
)


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    bio = db.Column(db.Text)
    image_url = db.Column(db.String(300))
    password = db.Column(db.String(100), nullable=False, unique=True)

    user_history = db.relationships("UserHistory", back_populates="user")

    friends = db.relationship(
        "User",
        secondary=user_friends,
        primaryjoin=(user_friends.c.user_id == user_id),
        secondaryjoin=(user_friends.c.friend_id == user_id),
        backref=db.bacrkref("user_friends"),
    )

    friend_request = db.relationship(
        "User",
        secondary=user_friend_requests,
        primaryjoin=(user_friend_requests.c.sender_id == user_id),
        secodaryjoin=(user_friend_requests.c.receiver_id == user_id),
        backref=db.backref("user_friend_requests"),
    )

    @classmethod
    def signup(cls, username, email, password):
        hash_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")
        user = User(
            username=username,
            email=email,
            password=hash_pwd,
        )
        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        user = cls.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        return None


class UserHistory(db.Model):
    __tablename__ = "user_history"

    history_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.User_id"), nullable=False)
    date_recorded = db.Column(db.Date, nullable=False, unique=True)

    user = db.relationship("User", back_populate="user_histories")


class WorkoutEntry(db.Model):
    __tablename__ = "workout_entries"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    entry = db.Column(db.Text, nullable=False)

    user = db.relationship("User", backref=db.backref("workout_entries"))

    def __init__(self, user_id, date, entry):
        self.user_id = user_id
        self.date = date
        self.entry = entry

        def serialize(self):
            return {
                "id": self.id,
                "user_id": self.user_id,
                "date": self.date.strftime("%m-%d"),
                "entry": self.entry,
            }


class DayOfTheWeek(db.Model):
    __tablename__ = "days"

    days_id = db.Column(db.Integer, primary_key=True)
    days_date = db.Column(db.Date, nullable=False)


class WorkoutofTheDay(db.Model):
    __tablename__ = "muscle_group"

    muscle_group_id = db.Column(db.Integer, primary_key=True)
    muscle_group = db.Column(db.Text, nullable=False, unique=True)
    exercises = db.Column(db.Text, foreign_key=True, nullable=False, unique=True)


def connect_db(app):
    """Connect database to Flask app."""

    db.app = app
    db.init_app(app)
    app.app_context().push()

    # Create the db tables
    db.create_all()
