from flask import request, jsonify
from app.categories.validations import is_valid, has_numbers, authentication


def valid_recipe_title(title):
    """Function to handle validations in inputs"""
    if title == "None":
        return {"message": "Nothing is provided"}
    if isinstance(title, int):
        return {"message": "Recipe title"
                           " should not be an integer"}
    if is_valid(title):
        return {'message': 'Recipe title should'
                           ' not have special characters'}
    if has_numbers(title):
        return {'message': 'Recipe title'
                                    ' should not have numbers'}
    if not title or title.isspace():
        return {'message': 'Recipe title'
                                    ' is mostly required'}