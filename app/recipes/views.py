from .import recipe
from flask import request, jsonify, abort, make_response
from app.models import Category, User, Recipe
from app.categories.views import is_valid, has_numbers
from flasgger import swag_from
from .validations import valid_recipe_title

@recipe.route('/api/v1/categories/<int:id>/recipes', methods=['POST'])
@swag_from('/app/docs/addrecipe.yml')
def add_recipes(id, **kwargs):
    """This route handles posting a recipe"""
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return jsonify({"message": "No token, please provide a token"}), 401
    access_token = auth_header.split()[1]
    if access_token:
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):
            if request.method == "POST":
                title = str(request.data.get('title', '')).strip()
                description = str(request.data.get('description', ''))
                result1 = valid_recipe_title(title)
                if result1:
                    return jsonify(result1), 400
                identity = Category.find_user_by_id(id, user_id)
                if not identity:
                    return jsonify({"message": "Category doesn't exist"}), 400
                title = title.lower()
                result = Recipe.find_by_id(title, id)
                if result:
                    return jsonify({"message": "Recipe already exists"}), 400
                if title:
                    recipe = Recipe(title=title, description=description,
                                    category_identity=id)
                    recipe.save()
                    return recipe.json(), 201
        else:
            message = user_id
            return jsonify({'message': message}), 401


@recipe.route('/api/v1/categories/<int:id>/recipes', methods=['GET'])
@swag_from('/app/docs/getrecipes.yml')
def get_recipes(id, **kwargs):
    """This route handles getting recipes"""
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return jsonify({"message": "No token, please provide a token"}),401
    access_token = auth_header.split(" ")[1]
    if access_token:
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):
            page = request.args.get('page', 1, type=int)
            limit = request.args.get('limit', 3, type=int)
            q = str(request.args.get('q', '')).lower()
            identity = Category.find_user_by_id(id, user_id)
            if not identity:
                return jsonify({"message":"You don't have"
                                      " the recipes in that category"}), 400
            recipes = Recipe.query.filter_by(
                category_identity=id).paginate(page=page,
                                            per_page=limit, error_out=False)
            results = []
            if q:
                for recipe in recipes.items:
                    if q in recipe.title.lower() or q in recipe.description:
                        obj = recipe.json()
                        results.append(obj)
            else:
                for recipe in recipes.items:
                    obj = {
                        'id': recipe.id,
                        'title': recipe.title,
                        'description': recipe.description,
                        'date_created': recipe.date_created,
                        'date_modified': recipe.date_modified,
                        'category_identity': id,
                        'Next_page': recipes.next_num,
                        'Previous_page': recipes.prev_num,
                        'Page_number': recipes.page
                    }
                    results.append(obj)
            if len(results) <= 0:
                return jsonify({"Error": "No recipes on that page"}), 404
            if results:
                return jsonify({'recipes': results}), 200
            else:
                return jsonify({"message": "No recipes found"}), 404
        else:
            # user is not legit,an error message to handle expired token
            message = user_id
            return jsonify({'message': message}), 401


@recipe.route('/api/v1/categories/<int:id>/recipes/<int:recipe_id>', 
              methods=['DELETE'])
@swag_from('/app/docs/deleterecipe.yml')
def delete_recipe(id, recipe_id, **kwargs):
    """This route handles deleting a recipe by id"""
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return jsonify({"message": "No token, please provide a token"}), 401
    access_token = auth_header.split()[1]
    if access_token :
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):
            identity = Category.find_user_by_id(id, user_id)
            if not identity :
                return jsonify({"message": "You don't have"
                                " that recipe in that category"}), 400
            recipe = Recipe.find_recipe_by_id(recipe_id, id)
            if not recipe :
                return jsonify({"message": "No recipes with"
                                " that id to delete "}), 404
            else:
                recipe.delete()
                return {"message": "recipe {} deleted"
                               " successfully".format(recipe.id)}, 200
        else:
            message = user_id
            return jsonify({'message': message}), 401


@recipe.route('/api/v1/categories/<int:id>/recipes/<int:recipe_id>',
              methods=['PUT'])
@swag_from('/app/docs/updaterecipes.yml')
def edit_recipe(id, recipe_id, **kwargs):
    """This route handles update a recipe by id"""
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return jsonify({"message": "No token, please provide a token"}), 401
    access_token = auth_header.split()[1]
    if access_token:
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):
            title = str(request.data.get('title', '')).strip()
            description = str(request.data.get('description', '')).strip()
            identity = Category.find_user_by_id(id, user_id)
            if not identity :
                return jsonify({"message": "You don't have"
                                " that recipe in that category"}), 400
            result2 = valid_recipe_title(title)
            if result2:
                return jsonify(result2), 400
            title = title.lower()
            result = Recipe.find_by_id(title, id)
            if result:
                return jsonify({"message": "Recipe already exists"}), 400
            recipe = Recipe.find_recipe_by_id(recipe_id, id)
            if not recipe :
                return jsonify({"message":"No recipes"
                                          " with that id to edit "}), 404
            else:
                title = str(request.data.get('title', '')).lower()
                description = str(request.data.get('description', ''))
                recipe.title = title
                recipe.description = description
                recipe.save()
                return recipe.json(), 200
        else:
            # user is not legit, an error message to handle expired token
            message = user_id
            return jsonify({'message': message}), 401


@recipe.route('/api/v1/categories/<int:id>/recipes/<int:recipe_id>', 
               methods=['GET'])
@swag_from('/app/docs/getrecipe.yml')
def get_recipe_by_id(id, recipe_id, **kwargs):
    """This route handles getting a recipe by id"""
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return jsonify({"message": "No token, please provide a token"}), 401
    access_token = auth_header.split(" ")[1]
    if access_token:
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):
            identity = Category.find_user_by_id(id, user_id)
            if not identity:
                return jsonify({"message": "You don't have"
                               " that recipe in that category"}), 400
            recipe = Recipe.find_recipe_by_id(recipe_id, id)
            if not recipe:
                return jsonify({"message":"No recipes with"
                                          " that id to get"}), 400
            else:
                return recipe.json(), 200
        else:
            # user is not legit,an error message to handle expired token
            message = user_id
            return jsonify({'message': message}), 401