from . import auth_blueprint
import os
import datetime
import re
import jwt
from flask.views import MethodView
from flask import Flask, make_response, request, jsonify, json, abort
from app.models import User, RevokedToken
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flasgger import swag_from

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

recipients = []
class RegistrationView(MethodView):
    """This class registers a new user."""
    @swag_from('/app/docs/register.yml')
    def post(self):
        """This route is for registering a user """
        try:
            user = User.query.filter_by(email=request.data['email']).first()
            if not user:
                post_data = request.data
                # Register the user
                email = post_data['email'].strip()
                password = post_data['password'].strip()
                if not email:
                    return jsonify({"message": "email"
                                    " required please"}), 401
                if not password:
                    return jsonify({"message": "password"
                                    " required please"}), 401
                if len(password) > 6 and re.match("[^@]+@[^@]+\.[^@]+", email):
                    user = User(email=email, password=password)
                    user.save()
                    return jsonify({'message': 'You registered'
                                    ' successfully. Please login.'}), 201
                return jsonify({'message':
                                'Invalid email or password,'
                                ' Please try again'}), 400
            return jsonify({'message': 'User already exists.'
                            ' Please login.'}), 409
        except Exception as e:  # pragma: no cover
            # An error occured, then return a message containing the error
            return jsonify({'message': 'Invalid data,'
                            ' ensure proper json'}), 400


class LoginView(MethodView):
    """This class-based view handles user login and access token generation."""
    @swag_from('/app/docs/login.yml')
    def post(self):
        """This route is for handling login"""
        try:
            post_data = request.data
            email = post_data['email'].strip()
            password = post_data['password'].strip()
            if not email and not password:
                return make_response(jsonify({'message': 'Please fill all the fields'})), 400
            # Get the user object using their email (unique to every user)
            user = User.query.filter_by(email=request.data['email']).first()
            # Try to authenticate the found user using their password
            if user and user.password_is_valid(request.data['password']):
                # Generate the access token to be used as the header
                access_token = user.generate_token(user.id)
                if access_token:
                    return jsonify({'message': 'You logged in successfully.',
                                    'access_token': access_token.decode()}), 200

            return jsonify({'message': 'Invalid email or password,'
                            ' Please try again'}), 401
        except Exception as e:  # pragma: no cover
            # Create a response containing an string error message
            return jsonify({'message': 'An error occured'
                            ' ensure proper login'}), 401


class ResetPasswordView(MethodView):
    """This class will handle the resetting of password"""
    @swag_from('/app/docs/change.yml')
    def put(self):
        auth_header = request.headers.get('Authorization')
        if auth_header is None:
            return jsonify({"message": "No token,"
                            " please provide a token"}), 401
        access_token = auth_header.split()[1]
        if access_token:
            # This method will edit the already existing password
            post_data = request.data
            email = post_data['email'].strip()
            password = post_data['password'].strip()
            retyped_password = post_data['retyped_password'].strip()

            if not email or not password or not retyped_password:
                return make_response(jsonify({'message': 'Please fill all the fields'})), 400

            if not re.match("[^@]+@[^@]+\.[^@]+", email):
                return make_response(jsonify({'message': 'Invalid email given'})), 400

            if len(password) < 7 and len(retyped_password) < 7:
                return make_response(jsonify({'message': 'The password is too short'})), 400

            if password != retyped_password:
                return make_response(jsonify({'message': 'Password mismatch'})), 400
            user = User.query.filter_by(email=request.data['email']).first()
            if user:
                user.password = Bcrypt().generate_password_hash(retyped_password).decode()
                user.save()
                return make_response(jsonify({'message': 'Password resetting is successful'})), 200
            return make_response(jsonify({'message': 'User does not exist!'})), 404
        return jsonify({'message': 'please provide a  valid token'})
class Send_reset_password_emailView(MethodView):
    """ This will send an email with the token to reset password."""
    @swag_from('/app/docs/resetemail.yml')
    def post(self):
    # This method will edit the already existing password
        post_data = request.data
        email = post_data['email'].strip()
        user = User.query.filter_by(email=email).first()
        if not email:
            return make_response(jsonify({'message': 'Please input the email'})), 412

        if not re.match("[^@]+@[^@]+\.[^@]+", email):
            return make_response(jsonify({'message': 'Invalid email given'})), 400

        if not user:
            return make_response(jsonify({'message': 'User does not exist!'})), 404

        try:
            access_token = jwt.encode({'id': user.id, 'expiry_time': str(datetime.datetime.utcnow() +
            datetime.timedelta(minutes=30))},
            os.getenv('SECRET', '$#%^%$^%@@@@@56634@@@'))
            subject = "Yummy Recipes Reset Password"
            recipients.append(email)
            msg = Message(subject, sender="Admin", recipients=recipients)
            styles = "background-color:green; color:white; padding: 5px 10px; border-radius:3px; text-decoration: none;"
            msg.html = f"Click the link to reset password:\n \n<h3><a href='https://hadijahz-recipes-react.herokuapp.com/reset?tk={access_token.decode()}' style='{styles}'>Reset Password</a></h3>"
            with app.app_context():
                mail.send(msg)
            return make_response(jsonify({'message': 'Password Reset link sent successfully to '+email+''})), 201
        except Exception:
            return make_response(jsonify({'message': 'Invalid request sent.'})), 400


class Logout_view(MethodView):
    @swag_from('/app/docs/logout.yml')
    def post(self):
        """This route handles logout """
        auth_header = request.headers.get('Authorization')
        if auth_header is None:
            return jsonify({"message": "No token,"
                            " please provide a token"}), 401
        access_token = auth_header.split()[1]
        if access_token:
            user_id = User.decode_token(access_token)
            if isinstance(user_id, int):
                revoked_token = RevokedToken(token=access_token)
                revoked_token.save()
                return jsonify({'message': 'Your have been logged out.'}), 201
            else:
                message = user_id
                response = {'message': message}
                return make_response(jsonify(response)), 401
        else:
            return jsonify({'message': 'please provide a  valid token'})


# Define the API resource
registration_view = RegistrationView.as_view('registration_view')
login_view = LoginView.as_view('login_view')
reset_password_view = ResetPasswordView.as_view('reset_password_view')
send_email_view = Send_reset_password_emailView.as_view('send_email_view')
logout_view = Logout_view.as_view('logout_view')

# Define the rule for the registration url --->  /api/v1/auth/register
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/api/v1/auth/register',
    view_func=registration_view,
    methods=['POST'])

# Define the rule for the registration url --->  /api/v1/auth/login
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/api/v1/auth/login',
    view_func=login_view,
    methods=['POST'])
# Define the rule for the registration url --->  /api/v1/reset_passsword
auth_blueprint.add_url_rule(
    '/api/v1/auth/reset_password', view_func=reset_password_view,
    methods=['PUT'])

auth_blueprint.add_url_rule(
    '/api/v1/auth/send_email', view_func=send_email_view,
    methods=['POST'])
# Define the rule for the registration url --->  /api/v1/auth/logout
auth_blueprint.add_url_rule(
    '/api/v1/auth/logout', view_func=logout_view,
    methods=['POST'])
