
import jwt
from app import db
from datetime import datetime, timedelta
from flask import current_app
from flask_bcrypt import Bcrypt


class User(db.Model):
    """This class defines the users table """

    __tablename__ = 'users'

    # Define the columns of the users table, starting with the primary key
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    categories = db.relationship(
        'Category', order_by='Category.id', cascade="all, delete-orphan", lazy='dynamic')

    def __init__(self, email, password, username):
        """Initialize the user with an email and a password."""
        self.email = email
        self.username = username
        self.password = Bcrypt().generate_password_hash(password).decode()

    def password_is_valid(self, password):
        """
        Checks the password against it's hash to validates the user's password
        """
        return Bcrypt().check_password_hash(self.password, password)

    def save(self):
        """Save a user to the database.
        This includes creating a new user and editing one.
        """
        db.session.add(self)
        db.session.commit()

    def generate_token(self, user_id):
        """ Generates the access token"""

        try:
            # set up a payload with an expiration time
            payload = {
                'exp': datetime.utcnow() + timedelta(days=30),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            # create the byte string token using the payload and the SECRET key
            jwt_string = jwt.encode(
                payload,
                current_app.config.get('SECRET'),
                algorithm='HS256'
            )
            return jwt_string

        except Exception as e:
            # return an error in string format if an exception occurs
            return str(e)

    @staticmethod
    def decode_token(token):
        """Decodes the access token from the Authorization header."""
        try:
            # try to decode the token using our SECRET variable
            payload = jwt.decode(token, current_app.config.get('SECRET'))
            token_is_revoked = RevokedToken.check_revoked_token(auth_token=token)
            if token_is_revoked:
                return 'Revoked token. please login to get a new token'
            else:
                return payload['sub']
        except jwt.ExpiredSignatureError:
            # the token is expired, return an error string
            return "Expired token. Please login to get a new token"
        except jwt.InvalidTokenError:
            # the token is invalid, return an error string
            return "Invalid token. Please register or login"
    def __repr__(self):
        return "<User: {}>".format(self.email)

class RevokedToken(db.Model):
    """Define the 'RevokedToken' model mapped to database table 'revoked_tokens'."""

    __tablename__ = 'revoked_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    revoked_on = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

    def __init__(self, token):
        self.token = token

    def save(self):
        """Save to database table"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def check_revoked_token(auth_token):
        """function to check if token is revoked
        """
        # check whether token has been revoked
        res = RevokedToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False

    def __repr__(self):
        return '<id: token: {}'.format(self.token)


class Category(db.Model):
    """This class represents the categories table."""

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    recipes = db.relationship(
        'Recipe', order_by='Recipe.id', cascade="all, delete-orphan", lazy='dynamic')
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey(User.id))

    def category_json(self):
        """This method jsonifies the recipe model"""
        return {'id':self.id, 'name': self.name, 'date_created':self.date_created,
                'date_modified':self.date_modified, 'created_by':self.created_by}

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_name(cls, name, user_id):
        return cls.query.filter_by(name = name, created_by = user_id).first()

    @classmethod
    def find_user_by_id(cls, id, user_id):
        return cls.query.filter_by(id = id, created_by = user_id).first()

    @staticmethod
    def get(user_id):
        """This method gets all the categories for a given user."""
        return Category.query.filter_by(created_by=user_id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Category: {}>".format(self.name)


class Recipe(db.Model):
    """ Models the recipe table """

    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    description = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())
    category_identity = db.Column(db.Integer, db.ForeignKey(Category.id))

    def json(self):
        """This method jsonifies the recipe model"""
        return {'id':self.id,'title': self.title, 'description': self.description, 'date_created':self.date_created,
                'date_modified':self.date_modified, 'category_identity':self.category_identity}

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_title(cls, title, id):
        return cls.query.filter_by(title = title, category_identity = id).first()

    @classmethod
    def find_by_id(cls, title, id):
        return cls.query.filter_by(title = title, category_identity = id).first()

    @classmethod
    def find_recipe_by_id(cls, recipe_id, id):
        return cls.query.filter_by(id = recipe_id, category_identity = id).first()

    @staticmethod
    def get():
        return Recipe.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Recipe: {}>".format(self.title)
