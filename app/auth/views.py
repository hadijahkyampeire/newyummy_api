from . import auth_blueprint
import re

from flask.views import MethodView
from flask import make_response, request, jsonify, json, abort
from app.models import User, RevokedToken
from flask_bcrypt import Bcrypt


class RegistrationView(MethodView):
    """This class registers a new user."""

    def post(self):
        """
        Handle POST request for this view. Url ---> /api/v1/auth/register 
        ---
        tags:
          - User Authentication
        parameters:
          - in: body
            name: body
            required: true
            type: string
            description: This route registers a new user
        responses:
          200:
            description: You successfully registered 
          201:
            description: You successfully registered , please login
            schema:
              id: successful Register 
              properties:
                email:
                  type: string
                  default: hadijah.kyampeire@andela.com
                password:
                  type: string
                  default: 1234567
                response:
                  type: string
                  default: You registered successfully. Please login.
          400:
            description: For invalid data
            schema:
              id: Register User with invalid
              properties:
                email:
                  type: string
                  default: hadijah
                password:
                  type: string
                  default: 12345
                response:
                  type: string
                  default: Invalid email or password, Please try again with a valid email and a password with morethan 6 characters
          400:
            description: wrong json
            schema:
              id: Invalid Register
              properties:
                email:
                  default: hadijah@gmail.com
                password:
                  type: string
                  default: 1234897
                response:
                  type: string
                  default: please input both email and password in json form'
          202:
            description: Duplication
            schema:
              id: Exceptions
              properties:
                email:
                  type: string
                  default: hadijah.kyampeire@andela.com
                password:
                  type: string
                  default: 1234567
                response:
                  type: string
                  default: User already exists. Please login.'
        """
        
        try:
            user = User.query.filter_by(email=request.data['email']).first()
            if not user:
                post_data = request.data
                # Register the user
                email = post_data['email']
                password = post_data['password']

                if len(password) > 6 and re.match("[^@]+@[^@]+\.[^@]+", email):
                    user = User(email=email, password=password)
                    user.save()

                    response = {
                        'message': 'You registered successfully. Please login.'
                    }
                    # return a response notifying the user that they registered successfully
                    return make_response(jsonify(response)), 201
                response = {
                    'message': 'Invalid email or password, Please try again with a valid email and a password with morethan 6 characters'
                }
                return make_response(jsonify(response)), 400
            else:
                # There is an existing user. We don't want to register users twice
                # Return a message to the user telling them that they they already exist
                response = {
                    'message': 'User already exists. Please login.'
                }

                return make_response(jsonify(response)), 202
        except Exception as e:# pragma: no cover
            # An error occured, therefore return a string message containing the error
            response = {
                # 'message': str(e)
                'message': 'please input both email and password in json form'
            }
            return make_response(jsonify(response)), 400
    

class LoginView(MethodView):
    """This class-based view handles user login and access token generation."""

    def post(self):
        """
        Handle POST request for this view. Url ---> /api/v1/auth/login
        ---
        tags:
          - User Authentication
        parameters:
          - in: body
            name: body
            required: true
            type: string
            description: This route logs in a user
        responses:
          200:
            description: User logged in successfully
          201:
            description: You successfully registered , please login
            schema:
              id: successful login
              properties:
                email:
                  type: string
                  default: hadijah.kyampeire@andela.com
                password:
                  type: string
                  default: 1234567
                response:
                  type: string
                  default: access_token="eyJ0eXAiOiJKV1QiLCJhbGci" You logged in successfully..
          400:
            description: login before signup
            schema:
              id: Register User with invalid
              properties:
                email:
                  type: string
                  default: hadijah@gmail.com
                password:
                  type: string
                  default: 0987654
                response:
                  type: string
                  default: Invalid email or password, Please try again' 
        """
        try:
            # Get the user object using their email (unique to every user)
            user = User.query.filter_by(email=request.data['email']).first()

            # Try to authenticate the found user using their password
            if user and user.password_is_valid(request.data['password']):
                # Generate the access token. This will be used as the authorization header
                access_token = user.generate_token(user.id)
                print(access_token)
                if access_token:
                    response = {
                        'message': 'You logged in successfully.',
                        'access_token': access_token.decode()
                    }
                    return make_response(jsonify(response)), 200
            else:
                # User does not exist. Therefore, we return an error message
                response = {
                    'message': 'Invalid email or password, Please try again'
                }
                return make_response(jsonify(response)), 401

        except Exception as e:# pragma: no cover
            # Create a response containing an string error message
            response = {
                # 'message': str(e)
                'message': "An error occured ensure proper login"
            }
            # Return a server error using the HTTP Error Code 500 (Internal Server Error)
            return make_response(jsonify(response)), 401
class ResetPasswordView(MethodView):
    
    def post(self):
        """
        Allows user to change password. Url ---> /api/v1/auth/reset_password 
        ---
        tags:
          - User Authentication
        parameters:
          - in: body
            name: body
            required: true
            type: string
            description: first input your credentials then Input new password 
        security:
          - TokenHeader: []
        responses:
          200:
            description: User successfully created   
          201:
            description: You successfully registered , please login
            schema:
              id: successful reset password
              properties:
                email:
                  type: string
                  default: hadijah.kyampeire@andela.com
                password:
                  type: string
                  default: 0987654
                response:
                  type: string
                  default: password reset successfully..

        """
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]
        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                try:
                    
                    post_data = request.data
                # Register the user
                    email = post_data['email']
                    password = post_data['password']
                    new = post_data['new_password']
                    reset_data=[new]
                    user = User.query.filter_by(email=email).first()
                    if not user:
                        response = jsonify({
                            'message': 'User not found'
                        })
                        return make_response(response),401
                    if reset_data:
                        if len(new) > 6 :
                            user.password = Bcrypt().generate_password_hash(new).decode()
                            user.save()
                            response = {'message': 'Your password has been reset.'}
                            return make_response(jsonify(response)), 200
                        response = {
                                'message': "Password needs to be more than 6 characters"
                            }
                        return make_response(jsonify(response)), 400
                except Exception as e:# pragma: no cover
                    response = {'message': str(e)}
                    return make_response(jsonify(response)), 401
class Logout_view(MethodView):
    def post(self):
        """
        Handle POST request for this view. Url ---> /api/v1/auth/logout
        ---
        tags:
          - User Authentication
        security:
          - TokenHeader: []
        responses:
          200:
            description: you logged out successfully   
        """
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]
        if access_token:
            user_id = User.decode_token(access_token)
            try:
                if not isinstance(user_id, str):
                    revoked_token = RevokedToken(token=access_token)
                    revoked_token.save()
                    response = {'message': 'Your have been logged out.'}
                    return make_response(jsonify(response)), 200
                else:
                    message = user_id
                    response = {'message': message}
                    return make_response(jsonify(response)), 401
            except Exception as e:#pragma no cover
                response = {'message': str(e)}
                return make_response(jsonify(response)), 401



# Define the API resource
registration_view = RegistrationView.as_view('registration_view')
login_view = LoginView.as_view('login_view')
reset_password_view = ResetPasswordView.as_view('reset_password_view')
logout_view = Logout_view.as_view('logout_view')

# Define the rule for the registration url --->  /auth/register
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/api/v1/auth/register',
    view_func=registration_view,
    methods=['POST'])

# Define the rule for the registration url --->  /auth/login
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/api/v1/auth/login',
    view_func=login_view,
    methods=['POST'])

auth_blueprint.add_url_rule(
    '/api/v1/auth/reset_password', view_func=reset_password_view, 
        methods=['POST'])
auth_blueprint.add_url_rule(
    '/api/v1/auth/logout', view_func=logout_view, 
        methods=['POST'])

