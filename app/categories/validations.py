from flask import request, jsonify, make_response
from functools import wraps
from app.models import User


def is_valid(name_string):
    """Function to handle special characters in inputs"""
    special_character = "~!@#$%^&*()_={}|\[]<>?/,;:"
    return any(char in special_character for char in name_string)


def has_numbers(input_string):
    """Function to handle digits in inputs"""
    return any(char.isdigit() for char in input_string)

def valid_category(name):
    """Function to handle validations in inputs"""
    if name == "None":
        return {"message": "Nothing is provided"}
    if isinstance(name, int):
        print(name)
        return {"message": "category name"
                           " should not be an integer"}
    if not name or name.isspace():
        return {'message': 'Category name'
                           ' is required'}
    if is_valid(name):
        return {'message': 'Category name should'
                           ' not have special characters'}
    if has_numbers(name):
        return {'message': 'Category name should'
                           ' not have numbers'}               
def authentication(func):
    @wraps(func)
    def auth(*args,**kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header is None:
            return jsonify({"message": "No token, please provide a token"}), 401
        access_token = auth_header.split(" ")[1]
        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                return func(user_id,*args,**kwargs)
            return jsonify({'message': user_id}),401
    return auth
