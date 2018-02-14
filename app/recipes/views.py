from .import recipe
from flask import request, jsonify, abort, make_response
from sqlalchemy import or_
from app.models import Category, User, Recipe
from app.categories.views import is_valid, has_numbers
from flasgger import swag_from
from .validations import valid_recipe_title, authentication


@recipe.route('/api/v1/categories/<int:id>/recipes', methods=['POST'])
@authentication
@swag_from('/app/docs/addrecipe.yml')
def add_recipes(user_id, id, **kwargs):
    """This route handles posting a recipe"""

    if request.method == "POST":
        title = str(request.data.get('title', '')).strip().lower()
        description = str(request.data.get('description', ''))
        result1 = valid_recipe_title(title)
        if result1:
            return jsonify(result1), 400
        identity = Category.find_user_by_id(id, user_id)
        if not identity:
            return jsonify({"message": "Category doesn't exist"}), 400
        result = Recipe.find_by_id(title, id)
        if result:
            return jsonify({"message": "Recipe already exists"}), 400
        if title:
            recipe = Recipe(title=title, description=description,
                            category_identity=id)
            recipe.save()
            return recipe.json(), 201


@recipe.route('/api/v1/categories/<int:id>/recipes', methods=['GET'])
@authentication
@swag_from('/app/docs/getrecipes.yml')
def get_recipes(user_id, id, **kwargs):
    """This route handles getting recipes"""

    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 6, type=int)
    search_query = str(request.args.get('q', '')).lower()
    identity = Category.find_user_by_id(id, user_id)
    if not identity:
        return jsonify({"message": "You don't have"
                        " the recipes in that category"}), 400
    recipes = Recipe.query.filter(
        Recipe.category_identity == id)
    if search_query:
        recipes = recipes.filter(
            or_(Recipe.title.like('%' + search_query.strip().lower() + '%'),
                Recipe.description.like('%' + search_query.strip().lower() + '%')))
    recipes = recipes.paginate(
        page=page, per_page=limit, error_out=False)
    results = []
    for recipe in recipes.items:
        results.append({
            'recipe': recipe.json(),
            'Next_page': recipes.next_num,
            'Previous_page': recipes.prev_num,
            'Total_pages': recipes.pages
        })
    if results:
        return jsonify({'recipes': results}), 200
    return jsonify({"message": "No recipes found"}), 404


@recipe.route('/api/v1/categories/<int:id>/recipes/<int:recipe_id>',
              methods=['DELETE'])
@authentication
@swag_from('/app/docs/deleterecipe.yml')
def delete_recipe(user_id, id, recipe_id, **kwargs):
    """This route handles deleting a recipe by id"""

    identity = Category.find_user_by_id(id, user_id)
    if not identity:
        return jsonify({"message": "You don't have"
                        " that recipe in that category"}), 400
    recipe = Recipe.find_recipe_by_id(recipe_id, id)
    if not recipe:
        return jsonify({"message": "No recipes with"
                        " that id to delete "}), 404
    recipe.delete()
    return {"message": "recipe {} deleted"
            " successfully".format(recipe.id)}, 200


@recipe.route('/api/v1/categories/<int:id>/recipes/<int:recipe_id>',
              methods=['PUT'])
@authentication
@swag_from('/app/docs/updaterecipes.yml')
def edit_recipe(user_id, id, recipe_id, **kwargs):
    """This route handles update a recipe by id"""

    title = str(request.data.get('title', '')).strip()
    description = str(request.data.get('description', '')).strip()
    identity = Category.find_user_by_id(id, user_id)
    if not identity:
        return jsonify({"message": "You don't have"
                        " that recipe in that category"}), 400
    result2 = valid_recipe_title(title)
    if result2:
        return jsonify(result2), 400
    title = title.lower()
    result = Recipe.find_by_id(title, id)
    if result and result.description == description:
        return jsonify({"message": "Recipe already exists"}), 400
    recipe = Recipe.find_recipe_by_id(recipe_id, id)
    if not recipe:
        return jsonify({"message": "No recipes"
                        " with that id to edit "}), 404
    title = str(request.data.get('title', '')).lower()
    description = str(request.data.get('description', ''))
    recipe.title = title
    recipe.description = description
    recipe.save()
    return recipe.json(), 200


@recipe.route('/api/v1/categories/<int:id>/recipes/<int:recipe_id>',
              methods=['GET'])
@authentication
@swag_from('/app/docs/getrecipe.yml')
def get_recipe_by_id(user_id, id, recipe_id, **kwargs):
    """This route handles getting a recipe by id"""
    identity = Category.find_user_by_id(id, user_id)
    if not identity:
        return jsonify({"message": "You don't have"
                        " that recipe in that category"}), 400
    recipe = Recipe.find_recipe_by_id(recipe_id, id)
    if not recipe:
        return jsonify({"message": "No recipes with"
                        " that id to get"}), 400
    return recipe.json(), 200
