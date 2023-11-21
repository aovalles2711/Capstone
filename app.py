import requests, os, uuid, logging
from flask import Flask, render_template, request, flash, redirect, session, g, jsonify, url_for, send_from_directory
from sqlalchemy.exc import IntegrityError
# from flask_debugtoolbar import DebugToolbarExtension
from forms import LoginForm, SignupForm, ProfileEditForm
from models import db, connect_db, User, UserHistory, Group
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from sqlalchemy import update
# from flask_wtf.csrf import CSRFProtect

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postfresql:///app"
)
app.secret_key = "your_secret_key"
app.config['UPLOAD FOLDER'] = os.path.join(app.static_folder, 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["DEBUG_TB_INTERCEPTS_REDIRECTS"] = False
app.config["SECRET_KEY"] = "AlPHABETACHARLIE"
toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


################################ User signup/login/logout
@app.before_request
def add_user_to_g():
    """If logged in, add curr user to global."""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None


def do_login(user):
    """Log user in."""
    session[CURR_USER_KEY] = user.user_id


def do_logout():
    """Log user out."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
            )
            db.session.add(user)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            flash("Username or email already exists", "danger")
            return render_template("signup.html", form=form)

        do_login(user)  # Log user in using do_login
        flash("Congrats! You have successfully signed up.", "success")

        return redirect("/")
    return render_template("signup.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Authenticate User
        user = User.authenticate(username, password)
        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")

            return redirect("/")


@app.route("/logout")
def logout():
    """Logout user."""
    try:
        session.pop(CURR_USER_KEY)
        flash("You have logged out successfully", "success")
    except KeyError:
        flash("Login unsuccessful", "danger")

        return redirect("/")


###############################Retrieving Information from API
@app.route("/all", methods=["GET", "POST"])
def all():
    """See all exercises available."""
    all_exercises_data = None

    if request.method == "POST":
        exercise = request.form.get("exercise")
        all_exercises_data = get_all_exercises(exercise)

    # If no exercise has been entered, set all_exercises to None
    if not all_exercises_data:
        all_exercises_data = None

    return render_template(
        "api/exercise.html", all_exercises_data=all_exercises_data, user=g.user
    )


def get_all_exercises(exercise):
    url = "https://exerciseapi3.p.rapidapi.com/exercise/all"
    headers = {
        "X-RapidAPI-Key": "bee9607560msh913b3de27b43520p161031jsna0154a5562c8",
        "X-RapidAPI-Host": "exerciseapi3.p.rapidapi.com",
    }
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            flash(f"Failed to fetch exercises for {exercise}. Try again.", "error")
            return None

    except Exception as e:
        print("Error:", str(e))  # debugging
        flash(
            f"An error occurred while fetching exercises for {exercise}. Please try again.",
            "error",
        )
        return None


@app.route("/muscles", methods=["GET", "POST"])
def muscles():
    """Retrieve information regarding muscles to be targeted."""
    muscles_data = None

    if request.method == "POST":
        targeted = request.form.get("targeted")
        muscles_data = get_muscles(targeted)

    if not muscles_data:
        muscles_data = None

    return render_template("api/muscles.html", muscles_data=muscles_data, user=g.user)


def get_muscles(targeted):
    url = "https://exerciseapi3.p.rapidapi.com/muscles"
    headers = {
        "X-RapidAPI-Key": "bee9607560msh913b3de27b43520p161031jsna0154a5562c8"
        
        "X-RapidAPI-Host": "exerciseapi3.p.rapidapi.com",
        }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            flash(f"Failed to fetch muscles for {targeted}. Try again.", "error")
            return None
    
    except Exception as e:
        print("Error:", str(e))  # debugging
        flash(
            f"An error occurred while fetching muscles for {targeted}. Please try again.",
            "error",
        )
        return None

@app.route("/experiences", methods=["GET", "POST"])
def experiences():
    """Retrieve information regarding experience levels."""
    experiences_data = None

    if request.method == "POST":
        mastery = request.form.get("mastery")
        experiences_data = experiences(mastery)

    if not experiences_data:
        experiences_data = None

    return render_template("api/experiences.html", experiences_data=experiences_data, user=g.user)


def get_experiences(mastery):
    url = "https://exerciseapi3.p.rapidapi.com/experiences"
    headers = {
        "X-RapidAPI-Key": "bee9607560msh913b3de27b43520p161031jsna0154a5562c8"
        
        "X-RapidAPI-Host": "exerciseapi3.p.rapidapi.com",
        }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            flash(f"Failed to fetch experiences for {mastery}. Try again.", "error")
            return None
    
    except Exception as e:
        print("Error:", str(e))  # debugging
        flash(
            f"An error occurred while fetching experiences for {mastery}. Please try again.",
            "error",
        )
        return None

@app.route("/mechanics", methods=["GET", "POST"])
def mechanics():
    """Retrieve information regarding mechanics."""
    mechanics_data = None

    if request.method == "POST":
        movement = request.form.get("movement")
        mechanics_data = get_mechanics(movement)

    if not mechanics_data:
        mechanics_data = None

    return render_template("api/mechanics.html", mechanics_data=mechanics_data, user=g.user)


def get_mechanics(movement):
    url = "https://exerciseapi3.p.rapidapi.com/mechanics"
    headers = {
        "X-RapidAPI-Key": "bee9607560msh913b3de27b43520p161031jsna0154a5562c8"
        
        "X-RapidAPI-Host": "exerciseapi3.p.rapidapi.com",
        }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            flash(f"Failed to fetch mechanics for {movement}. Try again.", "error")
            return None
    
    except Exception as e:
        print("Error:", str(e))  # debugging
        flash(
            f"An error occurred while fetching mechanics for {movement}. Please try again.",
            "error",
        )
        return None

@app.route("/forces", methods=["GET", "POST"])
def forces():
    """Retrieve information regarding force types (ie. push, pull)."""
    forces_data = None

    if request.method == "POST":
        force = request.form.get("force")
        forces_data = get_forces(force)

    if not forces_data:
        forces_data= None

    return render_template("api/force_types.html", forces_data=forces_data, user=g.user)


def get_forces(force):
    url = "https://exerciseapi3.p.rapidapi.com/force_types"
    headers = {
        "X-RapidAPI-Key": "bee9607560msh913b3de27b43520p161031jsna0154a5562c8"
        
        "X-RapidAPI-Host": "exerciseapi3.p.rapidapi.com",
        }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            flash(f"Failed to fetch forces for {force}. Try again.", "error")
            return None
    
    except Exception as e:
        print("Error:", str(e))  # debugging
        flash(
            f"An error occurred while fetching forces for {force}. Please try again.",
            "error",
        )
        return None

@app.route("/equipment", methods=["GET", "POST"])
def equipment():
    """Retrieve information regarding equipment needed."""
    equipment_data = None

    if request.method == "POST":
        needed = request.form.get("needed")
        equipment_data = get_equipment_data(needed)

    if not equipment_data:
        equipment_data = None

    return render_template("api/equipment.html", equipment_data=equipment_data, user=g.user)


def get_equipment_data(needed):
    url = "https://exerciseapi3.p.rapidapi.com/equipment"
    headers = {
        "X-RapidAPI-Key": "bee9607560msh913b3de27b43520p161031jsna0154a5562c8"
        
        "X-RapidAPI-Host": "exerciseapi3.p.rapidapi.com",
        }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            flash(f"Failed to fetch equipment for {needed}. Try again.", "error")
            return None
    
    except Exception as e:
        print("Error:", str(e))  # debugging
        flash(
            f"An error occurred while fetching equipment for {needed}. Please try again.",
            "error",
        )
        return None

#################################Search Routes
@app.route('/search', methods=["GET", "POST"])
def search():
    search_data = None
    if request.method == "POST":
        by_name = request.form.get("by_name")
        search_data = get_search_data(by_name)

    if not search_data:
        search_data = None

    return render_template("api/name.html",search_data=search_data, user=g.user)

def get_search_data(by_name):
    url = "https://exerciseapi3.p.rapidapi.com/exercise/name/push%20up"
    headers = {
        "X-RapidAPI-Key": "bee9607560msh913b3de27b43520p161031jsna0154a5562c8"
        "X-RapidAPI-Host": "exerciseapi3.p.rapidapi.com",
        }
    
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            flash(f"Failed to fetch search data for {by_name}. Please try again.", 'error')
    
    except Exception as e:
        print("Error", str(e))
        flash (f"An error occured while fetching search for {by_name}. Please try again.", "error")

@app.route('/primary', methods=["GET", "POST"])
def primary():
    primary_data = None
    if request.method == "POST":
        by_primary = request.form.get("by_primary")
        primary_data = get_primary_data(by_primary)

    if not primary_data:
        primary_data = None

    return render_template("api/primary_muscle.html",primary_data=primary, user=g.user)

def get_primary_data(by_primary):
    url = "https://exerciseapi3.p.rapidapi.com/exercise/primary_muscle/chest"
    headers = {
        "X-RapidAPI-Key": "f314d61f66mshb885851f1612882p16dc9cjsn5a7193cd30df",
	    "X-RapidAPI-Host": "exerciseapi3.p.rapidapi.com",
        }
    
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            flash(f"Failed to fetch primary data for {by_primary}. Please try again.", 'error')
    
    except Exception as e:
        print("Error", str(e))
        flash (f"An error occured while fetching primary for {by_primary}. Please try again.", "error")

@app.route('/secondary', methods=["GET", "POST"])
def secondary():
    secondary_data = None
    if request.method == "POST":
        by_secondary = request.form.get("by_secondary")
        secondary_data = get_secondary_data(by_secondary)

    if not secondary_data:
        secondary_data = None

    return render_template("api/secondary_muscle.html",secondary_data=secondary, user=g.user)

def get_secondary_data(by_secondary):
    url = "https://exerciseapi3.p.rapidapi.com/exercise/secondary_muscle/chest"
    headers = {
        "X-RapidAPI-Key": "f314d61f66mshb885851f1612882p16dc9cjsn5a7193cd30df",
	    "X-RapidAPI-Host": "exerciseapi3.p.rapidapi.com",
        }
    
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            flash(f"Failed to fetch secondary data for {by_secondary}. Please try again.", 'error')
    
    except Exception as e:
        print("Error", str(e))
        flash (f"An error occured while fetching secondary for {by_secondary}. Please try again.", "error")

########################Homepage & User Profiles
@app.route("/")
def homepage():
    exercise_data = None

    if g.user:
        user_history = UserHistory.query.filter_by(user_id=g.user.user_id).all()
        user_groups = g.user.groups
        form = ProfileEditForm(request.form)
        user_profile = User.query.filter_by(user_id=g.user=user_id).first()
        image_url = user.profile.image_url if user_profile else None

        return render_template(
            'home.html',
            user_history=user_history,
            user_groups=user_groups,
            user=g.user,
            form=form,
            user_profile=user_profile,
            image_url=image_url
        )
    else:
        return render_template('home-anon.html')

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if g.user is None:
        flash('You are not logged in. Please log in to edit your profile.', 'warning')
        return redirect(url_for('login'))
    
    user = g.user # Get current user
    form = ProfileEditForm(obj=user) # pass user object to form

    if form.validate_on_submit():
        if user:
            # Image upload
            upload_image = form.image_url.data
            if upload_image:
                # filename
                filename = secure_filename(upload_image.filename)
                unique_filename = str(uuid.uuid4()) + filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                upload_image.save(file_path)

                # Update user's profile via image path
                user.image_url = unique_filename
            
            # update misc profile data
            form.populate_obj(user) # user object with form data

            # Commit updates to db
            db.session.commit()

            flash('Your profile has been updated successfully', 'success')
            return redirect(url_for('homepage'))
        
        else:
            flash('User not found.', 'error')
    
    return render_template('edit_profile.html', form=form, user=user)

# Upload files route
@app.route('/uploads/<filename>')
def upload_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Find friends
@app.route('/friends_profile/<int:user_id>')
def friends(user_id):
    # find user by user_id
    user = User.query.get(user_id)
    user_profile = User.query.filter_by(user_id=user.user_id).first()
    image_url = user_profile.image_url if user_profile else None
    if user:
        # groups user is in
        user_groups = user.groups
        # retrieve user's friends
        friends = user.friends

        return render_template('friends_profile.html', user=user, user_groups=user_groups, friends=friends, image_url=image_url)
    
    else:
        # where user is not found
        return "User not found"

@app.route('/send_friend_request/<int:user_id>', methods=['POST'])
def send_friend_request(user_id):
    if not g.user:
        # flash error message
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    if user_id == g.user.user_id:
        flash('Cannot send self a friend request', 'error')
        return jsonify({'success': False, 'message': 'Cannot send yourself a friend request.'})
    
    receiver: User.query.get(user_id)

    if receiver:
        # check if receiver is already a friend
        if receiver in g.user.friends:
            # flash ('Already friends with this user')
            return jsonify({'success': False, 'message': 'You are already friends with this user.'})
        
        # check if reciver already has your friend request
        if g.user in receiver.friend_requests:
            # flash ('Friend request already sent')
            return jsonify({'success': False, 'message': 'Friend request already sent.'})
        
        # Add sender to receiver's friend requests
        receiver.friend_requests.append(g.user)
        db.session.commit()
        # flash('Friend request sent successfully')
        return jsonify({'success': True, 'message': 'Friend request sent successfully.'})
    
    else:
        # flash error message
        return jsonify({'success': False, 'message': 'User not found'})
    
@app.route('/accept_friend_request/<int:sender_id>', methods=['POST'])
def accept_friend_request(sender_id):
    if not g.user:
        return jsonify(success=False, message='Not logged in.')
    
    sender = User.query.get(sender_id)

    if sender:
        # Verify if sender has sent a friend request to requested user
        if sender in g.user.friend_requests:
            # remove the friend request
            g.user.friend_requests.remove(sender)
            # Add sender to the requested user's friends list
            g.user.friends.append(sender)
            
            # Add current user to the sender's friends list
            sender.friends.append(g.user)

            db.session.commit()
            return jsonify(success=True, message='Friend request accepted')
        else: return jsonify(success=False, message='Friend request not found')
    else:
        return jsonify(success=False, message='User not found')
    
# Remove friend
@app.route('/remove_friend/<int:friend_id', methods=['POST'])
def remove_friend(friend_id):
    if not g.user:
        # Check if user is logged in
        flash('Not logged in.', 'error')
        return redirect(url_for('friends_groups'))
    
    friend = User.query.get(friend_id)
    if friend:
        # Check if friend exists
        if friend in g.user.friends:
            # Remove the friend from user's friends list
            g.user.friends.remove(friend)
            db.session.commit()
            flash('Friend removed successfully', 'success')
        
        else:
            flash('User is not your friend', 'error')
    else:
        flash('Friend not found', 'error')

    return redirect(url_for('friends_groups')) 