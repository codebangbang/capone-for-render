import os

from flask import Flask, render_template, request, flash, redirect, session, g, abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, UserEditForm, LoginForm
from models import db, connect_db, User

import requests

BASE_URL = "https://api.openbrewerydb.org/v1/breweries/search?query="

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///database-name'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)
with app.app_context():
    db.create_all()

def get_brewery_by_id(brewery_id):
    response = requests.get(f"{BASE_URL}{brewery_id}")
    if response.status_code == 200:
        return response.json()
    else:
        return None


##############################################################################
# root route - Allows a user to search for a brewery.  By using the search field, the API will return a list of breweries that has any field (name, city, etc.) that matches the search query. The user will be able to click on a brewery and see more details about the brewery.

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        search_query = request.form.get("search_query")
        response = requests.get(BASE_URL + search_query)

        if response.status_code == 200:
            breweries = response.json()
            processed_breweries = []
            for brewery in breweries:
                processed_brewery = {
                    'id': brewery['id'],
                    'name': brewery['name'],
                    'city': brewery['city'],
                    'state': brewery['state'],
                    'country': brewery['country'],
                    'website_url': brewery['website_url'],
                    'phone': brewery['phone'],
                    'brewery_type': brewery['brewery_type']
                }
                processed_breweries.append(processed_brewery)
            return render_template('breweries/results.html', breweries=processed_breweries)
        else:
            return "Error: Unable to fetch brewery data"
        
    return render_template('index.html')


# Provides brewery details when a user clicks on a brewery from the search results. The user will be able to see the name, city, state, country, website URL, phone number, and brewery type. The user will also be able to see a description of the brewery if it is available. If the description is not available, the user will see a message that says "No description available".
@app.route('/breweries/<name>') 
def show_brewery(name):
    """Show brewery details"""
    api_url= f"https://api.openbrewerydb.org/breweries?by_name={name}&per_page=1"
    response = requests.get(api_url)

    if response.status_code == 200:
        breweries = response.json()
        if breweries:
            brewery = breweries[0]
            return render_template('breweries/details.html', brewery=brewery)
        else:
            return "Error: Unable to fetch brewery data"
    else:
        return "Error: Unable to fetch brewery data"



##############################################################################
# User signup/login/logout

# Checks to see if a user is logged in. If the user is logged in, the user will be able to see the user's profile, edit the user's profile, and delete the user's profile. If the user is not logged in, the user will be redirected to the login page.
@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


# Route to the signup page. The user will be able to sign up for an account by providing a username, password, email, and bio. If the user tries to sign up with a username that is already taken, the user will see an error message that says "Username already taken". If the user successfully signs up, the user will be redirected to the home page.
@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
                bio=form.bio.data,
            )
            db.session.commit()

        except IntegrityError as e:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


# Route to the login page. The user will be able to log in by providing a username and password. If the user provides invalid credentials, the user will see an error message that says "Invalid credentials". If the user successfully logs in, the user will be redirected to the home page.  
@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


# Route to the logout page. The user will be able to log out of the account. If the user successfully logs out, the user will see a message that says "You have successfully logged out." and will be redirected to the login page.
@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("You have successfully logged out.", 'success')
    return redirect("/login")



# Route to the user profile page. The user will be able to see the user's profile, including the user's username, email, bio, image, and header image. The user will also be able to see a list of the user's favorite breweries. If the user is not logged in, the user will be redirected to the login page.
@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)
    return render_template('users/detail.html', user=user)


# Route to edit the user's profile. The user will be able to edit the user's profile by providing a new username, email, bio, image, and header image. If the user provides the wrong password, the user will see an error message that says "Wrong password, please try again." If the user successfully updates the profile, the user will be redirected to the user's profile page.
@app.route('/users/profile', methods=["GET", "POST"])
def edit_profile():
    """Update profile for current user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = g.user
    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.username = form.username.data
            user.email = form.email.data
            user.image_url = form.image_url.data or "/static/images/beer_foam.png"
            user.header_image_url = form.header_image_url.data or "/static/images/beerMugs.jpg"
            user.bio = form.bio.data

            db.session.commit()
            return redirect(f"/users/{user.id}")

        flash("Wrong password, please try again.", 'danger')

    return render_template('users/edit.html', form=form, user_id=user.id)

