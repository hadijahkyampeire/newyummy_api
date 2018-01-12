from flask import request, jsonify, make_response


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

