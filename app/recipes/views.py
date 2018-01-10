from .import recipe
from flask import request, jsonify, abort, make_response
from app.models import Category, User, Recipe
from app.categories.views import is_valid, has_numbers


@recipe.route('/api/v1/categories/<int:id>/recipes', methods=['POST'])
def add_recipes(id, **kwargs):
    """
    Method for posting recipes
    ---
    tags:
        - Recipe functions
    parameters:
        - in: path
          name: id
          required: true
          type: integer
          description: input the category id where you want to add recipes
        - in: body
          name: body
          required: true
          type: string
          description: input json data as recipe details
    security:
        - TokenHeader: []

    responses:
      200:
        description:  recipe successfully created
      201:
        description: Recipe created successfully
        schema:
          id: Add recipe
          properties:
            title:
              type: string
              default: pilau
            description:
              type: string
              default: burn onions
            response:
              type: string
              default: {'id': 1, 'title': pilau, 'description': burn onions,
                        'date_created': 22-12-2017, 'date_modified': 22-12-2017,
                        'category_identity': 1}
      400:
        description: For exceptions like not json data, special characters or numbers in the recipes
        schema:
          id: Invalid name
          properties:
            title:
              type: string
              default: '@@@kl'
            description:
              type: string
              default: burn onions
            response:
              type: string
              default: Recipe title should not have special characters or numbers
      422:
        description: If space or nothing is entered for title
        schema:
          id: Add empty recipe
          properties:
            title:
              type: string
              default: " "
            description:
              type: string
              default: burn onions
            response:
              type: string
              default: Recipe title mostly required
    """
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return jsonify({"message": "No token, please provide a token"}), 401
    access_token = auth_header.split(" ")[1]

    if access_token:
        # Attempt to decode the token and get the User ID
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):
            if request.method == "POST":
                title = str(request.data.get('title', '')).strip()
                description = str(request.data.get('description', ''))
                if title =="None":
                    return jsonify({"message": "Nothing is provided for title" }), 400
                if isinstance(title, int):
                    return jsonify({"message": "Recipe title should not be an integer"}), 400
                if is_valid(title):
                    return jsonify({'message': 'Recipe title should'
                                               'not have special characters'}), 400
                if has_numbers(title):
                    return jsonify({'message': 'Recipe title should not have numbers'}), 400
                if not title or title.isspace():
                    return jsonify({'message': 'Recipe title is mostly required'}), 422
                identity = Category.query.filter_by(id=id, created_by=user_id).first()
                if not identity:
                    return jsonify({"message": "Category does not exist"}), 400
                title = title.lower()
                result = Recipe.query.filter_by(title=title, category_identity=id).first()
                if result:
                    return jsonify({"message": "Recipe already exists"}), 400
                if title:
                    recipe = Recipe(
                        title=title, description=description, category_identity=id)
                    recipe.save()
                    response = jsonify({
                        'message': 'Recipe ' + recipe.title + ' has been created',
                        'recipe': {
                            'id': recipe.id,
                            'title': recipe.title,
                            'description': recipe.description,
                            'date_created': recipe.date_created,
                            'date_modified': recipe.date_modified,
                            'category_identity': id

                        }
                    })

                    response.status_code = 201
                    return response
        else:
            # user is not legit, so the payload is an error message to handle expired token
            message = user_id
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401


@recipe.route('/api/v1/categories/<int:id>/recipes', methods=['GET'])
def get_recipes(id, **kwargs):
    """
    This route is for a user to get recipes by q or pagination
    ---
    tags:
        - Recipe functions

    parameters:
        - in: path
          name: id
          required: true
          type: integer
          description: specify the category id where the recipe belongs
        - in: query
          name: q
          required: false
          type: string
          description: query by recipe name
        - in: query
          name: page
          required: false
          type: integer
          description: query by specifying the page number
        - in: query
          name: per_page
          required: false
          type: integer
          description: query by specifying the number of items per_page
    security:
        - TokenHeader: []
    responses:
      200:
        description:  recipe successfully retrieved
      201:
        description: For getting a valid recipe by q or pagination
        schema:
          id: successful retrieve of recipe
          properties:
            q search by title:
              type: string
              default: ?q=p
            pagination search:
              type: string
              default: ?page=1&per_page=1
            response:
              type: string
              default: {'id': 1, 'title': pilau,
                'description': burn onions,
                'date_created': 22-12-2017,
                'date_modified': 22-12-2017, 'category_identity': 1}
      400:
        description: Searching for a title that is not there or invalid
        schema:
          id: invalid GET recipe
          properties:
            title:
              type: string
              default: '33erdg@@'
            response:
              type: string
              default: No recipe found
    """
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return jsonify({"message": "No token, please provide a token" }),401
    access_token = auth_header.split(" ")[1]
    if access_token:
        # Attempt to decode the token and get the User ID
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):
            # GET all the categories created by this user
            page = request.args.get('page', 1, type=int)
            limit = request.args.get('limit', 2, type=int)
            q = str(request.args.get('q', '')).lower()
            identity = Category.query.filter_by(id=id,created_by=user_id).first()
            if not identity:
                return jsonify({"message": "You don't have the recipes in that category"}),400
            recipes = Recipe.query.filter_by(
                category_identity=id).paginate(page=page, per_page=limit, error_out=False)
            results = []
            if q:
                for recipe in recipes.items:
                    if q in recipe.title.lower() or q in recipe.description.lower():
                        obj = {}
                        obj = {
                            'id': recipe.id,
                            'title': recipe.title,
                            'description': recipe.description,
                            'date_created': recipe.date_created,
                            'date_modified': recipe.date_modified,
                            'category_identity': id
                        }
                        results.append(obj)
            else:
                # GET
                for recipe in recipes.items:
                    obj = {
                        'id': recipe.id,
                        'title': recipe.title,
                        'description': recipe.description,
                        'date_created': recipe.date_created,
                        'date_modified': recipe.date_modified,
                        'category_identity': id,
                        'Next_page': recipes.next_num,
                        'Previous_page':recipes.prev_num

                    }
                    results.append(obj)
                # return make_response(jsonify(results)), 200
                print(results)
            if len(results) <= 0:
                return jsonify({"Error": "No recipes on that page"})
            if results:
                return jsonify({'recipes': results})
            else:
                return jsonify({"message": "No recipes found"}),404
        else:
            # user is not legit, so the payload is an error message to handle expired token
            message = user_id
            response = {
                'message': message
            }
            # return an error response, telling the user he is Unauthorized
            return make_response(jsonify(response)), 401


@recipe.route('/api/v1/categories/<int:id>/recipes/<int:recipe_id>', methods=['DELETE'])
def delete_recipe(id, recipe_id, **kwargs):
    """
    This method is for deleting recipe by id
    ---
    tags:
        - Recipe functions
    parameters:
        - in: path
          name: id
          required: true
          type: integer
          description: specify the category id for the recipe
        - in: path
          name: recipe_id
          required: true
          type: integer
          description: specify the recipe id you want to delete
    security:
        - TokenHeader: []

    responses:
      200:
        description:  recipe successfully deleted
      201:
        description: For successful deletion of an existing recipe
        schema:
          id: successful deletion of recipe
          properties:
            id:
              default: 1
            response:
              type: string
              default: recipe 1 deleted
      204:
        description: Deleting a recipe which doesnot exist
        schema:
          id: invalid Delete of recipes
          properties:
            id:
              type: string
              default: 50
            response:
              type: string
              default: No recipe with that id  found to delete
    """
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return jsonify({"message": "No token, please provide a token" }), 401
    access_token = auth_header.split(" ")[1]

    if access_token:
        # Get the user id related to this access token
        user_id = User.decode_token(access_token)

        if not isinstance(user_id, str):
            # retrieve a recipe using it's ID
            identity = Category.query.filter_by(id=id, created_by=user_id).first()
            if not identity:
                return jsonify({"message": "You don't have that recipe in that category"}),400
            recipe = Recipe.query.filter_by(id=recipe_id, category_identity=id).first()
            if not recipe:
                return jsonify({"message":"No recipes with that id to delete "}),404

            else:
                recipe.delete()
                return {
                    "message": "recipe {} deleted successfully".format(recipe.id)
                }, 200
        else:
            # user is not legit, so the payload is an error message to handle expired token
            message = user_id
            response = {
                'message': message
            }
            # return an error response, telling the user he is Unauthorized
            return make_response(jsonify(response)), 401


@recipe.route('/api/v1/categories/<int:id>/recipes/<int:recipe_id>', methods=['PUT'])
def edit_recipe(id, recipe_id, **kwargs):
    """
    This method is for editing categories
    ---
    tags:
        - Recipe functions
    parameters:
        - in: path
          name: id
          required: true
          type: integer
          description: specify the category id for the recipe
        - in: path
          name: recipe_id
          required: true
          type: integer
          description: specify the recipe id you want to update
        - in: body
          name: body
          required: true
          type: string
          description: input new recipe details to edit a recipe
    security:
        - TokenHeader: []
    responses:
      200:
        description:  recipe successfully updated
      201:
        description: For successful update of an existing recipe
        schema:
          id: successful update of recipe
          properties:
            id:
              default: 1
            title:
              type: string
              default: milkshake
            description:
              type: string
              default: mix with coffee
            response:
              type: string
              default: {'id': 1, 'title': milkshake,
                    'description': mix with coffee,
                     date_created': 22-12-2017,
                     'date_modified': 22-12-2017, 'category_id': 1}
      400:
        description: updating recipe which doesnot exist
        schema:
          id: invalid update of recipes
          properties:
            id:
              type: string
              default: 100
            response:
              type: string
              default: No recipe found to edit
    """
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return jsonify({"message": "No token, please provide a token" }), 401
    access_token = auth_header.split(" ")[1]
    if access_token:
        # Get the user id related to this access token
        user_id = User.decode_token(access_token)

        if not isinstance(user_id, str):
            title = str(request.data.get('title', '')).strip()
            description = str(request.data.get('description', ''))
            identity = Category.query.filter_by(id=id, created_by=user_id).first()
            if not identity:
                return jsonify({"message": "You do not have that recipe in that category"}), 400
            if isinstance(title, int):
                return jsonify({"message": "Recipe title should not be an integer"}), 400
            if is_valid(title):
                return jsonify({'message': 'Recipe title'
                                           'should not have special characters'}), 400
            if has_numbers(title):
                return jsonify({'message': 'Recipe title should not have numbers'}), 400
            if not title or title.isspace():
                return jsonify({'message': 'Recipe title is mostly required'}), 422
            title=title.lower()
            result = Recipe.query.filter_by(title=title, category_identity=id).first()
            if result:
                return jsonify({"message": "Recipe already exists"}), 400
            # retrieve a recipe using it's ID
            recipe = Recipe.query.filter_by(id=recipe_id, category_identity=id).first()
            if not recipe:
                return jsonify({"message":"No recipes with that id to edit "}), 404

            else:
                title = str(request.data.get('title', '')).lower()
                description = str(request.data.get('description', ''))
                recipe.title = title
                recipe.description = description
                recipe.save()
                response = jsonify({
                    'id': recipe.id,
                    'title': recipe.title,
                    'description': recipe.description,
                    'date_created': recipe.date_created,
                    'date_modified': recipe.date_modified,
                    'category_identity': id
                })
                response.status_code = 200
                return response

        else:
            # user is not legit, so the payload is an error message to handle expired token
            message = user_id
            response = {
                'message': message
            }
            # return an error response, telling the user he is Unauthorized
            return make_response(jsonify(response)), 401


@recipe.route('/api/v1/categories/<int:id>/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe_by_id(id, recipe_id, **kwargs):
    """
    This method is for getting category by id
    ---
    tags:
        - Recipe functions
    parameters:
        - in: path
          name: id
          required: true
          type: integer
          description: specify the category id for the recipe
        - in: path
          name: recipe_id
          required: true
          type: integer
          description: specify the recipe id you want to get
    security:
        - TokenHeader: []

    responses:
      200:
        description:  recipe successfully retrieved
      201:
        description: For getting a valid recipe title by id
        schema:
          id: successful retrieve recipe by id
          properties:
            name:
              type: integer
              default: 1
            response:
              type: string
              default: {'id': 1, 'title': milkshake, 'description': mix with coffee, date_created': 22-12-2017, 'date_modified': 22-12-2017, 'category_id': 1}
      400:
        description: Searching for the recipe id that is not there
        schema:
          id: invalid GET recipe by id
          properties:
            id:
              type: integer
              default: 100
            response:
              type: string
              default: No recipe found with that id
    """
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return jsonify({"message": "No token, please provide a token" }), 401
    access_token = auth_header.split(" ")[1]
    if access_token:
        # Get the user id related to this access token
        user_id = User.decode_token(access_token)

        if not isinstance(user_id, str):
            identity = Category.query.filter_by(id=id, created_by=user_id).first()
            if not identity:
                return jsonify({"message": "You don't have that recipe in that category"}), 400
            # retrieve a recipe using it's ID
            recipe = Recipe.query.filter_by(id=recipe_id, category_identity=id).first()
            if not recipe:
                return jsonify({"message":"No recipes with that id to get"}), 400
            else:
                # GET
                response = jsonify({
                    'id': recipe.id,
                    'title': recipe.title,
                    'description': recipe.description,
                    'date_created': recipe.date_created,
                    'date_modified': recipe.date_modified,
                    'category_identity': id
                })
                response.status_code = 200
                return response
        else:
            # user is not legit, so the payload is an error message to handle expired token
            message = user_id
            response = {
                'message': message
            }
            # return an error response, telling the user he is Unauthorized
            return make_response(jsonify(response)), 401