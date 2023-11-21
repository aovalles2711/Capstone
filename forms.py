from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    DateField,
    SelectField,
    TextAreaField,
    SelectMultipleField,
    BooleanField,
    SubmitField,
    HiddenField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    ValidationError,
    InputRequired,
    optional,
)

from models import User, bcrypt
from flask import g
from wtforms.widgets import ListWidget, CheckboxInput
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.file import FileField, FileAllowed

bcrypt = Bcrypt()
db = SQLAlchemy()


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[Length(min=8), DataRequired()])
    submit = SubmitField("Login")


class SignupForm(FlaskForm):
    """Signup form."""

    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[Email(), DataRequired()])
    password = PasswordField("Password", validators=[Length(min=8), DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            EqualTo("password", message="Passwords must match"),
            DataRequired(),
        ],
    )
    submit = SubmitField("Sign Up")

    # Verify if username already exists
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already exists.")

    # Verify if email already exists
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email address already exists.")


class WorkoutEntryForm(FlaskForm):
    """Specific day of the week for exercise entry."""

    entry_id = HiddenField("Entry ID")  # Hidden Field
    day = DateField("Date", validators=[DataRequired()])
    entry = TextAreaField("Workout Entry", validators=[DataRequired()])


class DayOfTheWeekForm(FlaskForm):
    day_today = SelectMultipleField(
        "Select a day of the week.",
        choices=[
            ("1.", "Monday"),
            ("2.", "Tuesday"),
            ("3.", "Wednesday"),
            ("4.", "Thursday"),
            ("5.", "Friday"),
            ("6.", "Saturday"),
            ("7.", "Sunday"),
        ],
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput(),
    )


class WorkoutofTheDay(FlaskForm):
    muscle_group = SelectMultipleField(
        "Select muscle group to focus on.",
        choices=[
            ("1.", "Upper Body"),
            ("2.", "Core"),
            ("3.", "Lower Body"),
        ],
    )

    exercises = SelectField(
        "Select your desired exercise(s).",
        choices=[
            ("Pushup"),
            ("Bench Press"),
            ("Overhead Press"),
            ("Push Press"),
            ("Incline Bench Press"),
            ("Clean and Press"),
            ("Landmine Press"),
            ("Bentover Row"),
            ("One Arm Row"),
            ("Inverted Row"),
            ("Chinup/Pullup"),
            ("Deadlift"),
            ("EZ Bar Curl"),
            ("Dumbbell Curl"),
            ("Hammer Curl"),
            ("Cross-Body Curl"),
            ("Triceps Push-Down"),
            ("Dip"),
            ("Lying Triceps Extension"),
            ("Hang Clean"),
            ("Lateral Raise"),
            ("Bent Over Lateral Raise"),
            ("Face Pull"),
            ("Incline YTW"),
            ("Close-Grip Dumbbell Press"),
            ("Dumbbell Thruster"),
            ("Pullover"),
            ("Halo to Shoulder Press"),
            ("Front Squat"),
            ("Bulgarian Split Squat"),
            ("Romanian Deadlift"),
            ("Barbell Squat"),
            ("Dumbbell Stepup"),
            ("Swiss Ball Leg Curl"),
            ("Single-Leg Romanian Deadlift"),
            ("Leg Press"),
            ("Bodyweight Calf Raise"),
            ("Walking Lunge"),
            ("Pause Squat"),
            ("Reverse Lunge"),
            ("Dumbbell Squat"),
            ("Kettlebell Swing"),
            ("Jump Squat"),
            ("Barbell Calf Raise"),
            ("Barbell Hip Thrust"),
            ("Glute Bridge"),
            ("Single-Leg Glute Bridge"),
            ("Seated Calf Raise"),
            ("Kettlebell Press-Out"),
            ("Overhead Lunge"),
            ("Standing Calf Raise"),
            ("Goblet Squat"),
        ],
    )

    sets = SelectField(
        "Select set of each workout.",
        choices=[
            ("1"),
            ("2"),
            ("3"),
            ("4"),
            ("5"),
            ("6"),
            ("7"),
            ("8"),
            ("9"),
            ("10"),
        ],
    )

    repetitions = SelectField(
        "Select repitions of each workout.",
        choices=[
            ("1"),
            ("2"),
            ("3"),
            ("4"),
            ("5"),
            ("6"),
            ("7"),
            ("8"),
            ("9"),
            ("10"),
            ("11"),
            ("12"),
            ("13"),
            ("14"),
            ("15"),
            ("16"),
            ("17"),
            ("18"),
            ("19"),
            ("20"),
        ],
    )


class ProfileEditForm(FlaskForm):
    """Edit User Profile."""

    username = StringField("Username", validators=[optional()])
    email = StringField("Email", validators=[optional(), Email()])
    bio = TextAreaField("Bio", validators=[optional()])
    image_url = FileField(
        "Profile Picture",
        validators=[FileAllowed(["jpg", "png", "jpeg", "gif"], "Add Image")],
    )

    current_password = PasswordField("Current Password", validators=[DataRequired()])

    def validate_password(self, field):
        # Verify if the entered password matches user's current password
        user = User.query.get_or_404(
            g.user.user_id
        )  # assuming g.user is the current user

        if not bcrypt.check_password_hash(user.password, field.data):
            raise ValidationError("Wrong Password")
