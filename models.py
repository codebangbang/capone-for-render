"""SQLAlchemy models for Beer Search."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()

def connect_db(app):
    with app.app_context():
        db.app = app
        db.init_app(app)

db = SQLAlchemy();

class Brewery(db.Model):
    """Brewery in the system."""

    __tablename__ = 'brewery'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    brewery_type = db.Column(
        db.Text,
        nullable=False,
    )

    address_1 = db.Column(
        db.Text,
        nullable=False,
    )

    address_2 = db.Column(
        db.Text,
    )

    address_3 = db.Column(
        db.Text,
    )

    city = db.Column(
        db.Text,
        nullable=False,
    )   

    state_province = db.Column(
        db.Text,
        nullable=False,
    )

    postal_code = db.Column(
        db.Text,
        nullable=False,
    )

    country = db.Column(
        db.Text,
        nullable=False,
    )

    longitude = db.Column(
        db.Float,
        nullable=False,
    )   

    latitude = db.Column(
        db.Float,
        nullable=False,
    )

    phone = db.Column(  
        db.Text,
    )   

    website_url = db.Column(
        db.Text,
    )       

    state = db.Column(
        db.Text,
    )

    street = db.Column(
        db.Text,
    )
    


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/beer_sample.jpg",
    )

    header_image_url = db.Column(
        db.Text,
        default="/static/images/beer_foam.jpg"
    )

    bio = db.Column(
        db.Text,
    )

    location = db.Column(
        db.Text,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    
    @classmethod
    def signup(cls, username, email, password, image_url, bio):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
            bio=bio
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
