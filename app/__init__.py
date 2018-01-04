from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort, make_response


# local import
from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()

def is_valid(name_string):    
    special_character = "~!@#$%^&*()_={}|\[]<>?/,;:"
    return any(char in special_character for char in name_string)
def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


def create_app(config_name):
    from .models import Category, User, Recipe
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/api/v1/categories/', methods=['POST'])
    def add_categories():
        """
        Method for posting categories
        ---
        tags:
          - Category functions
        parameters:
          - in: body
            name: body
            required: true
            type: string
            description: input json data for a category
        security:
          - TokenHeader: []

        responses:
          200:
            description:  category successfully created   
          201:
            description: Category created successfully 
            schema:
              id: Add category 
              properties:
                name:
                  type: string
                  default: Dinner
                response:
                  type: string
                  default: {'id': 1, 'name': Dinner, 'date_created': 22-12-2017, 'date_modified': 22-12-2017, 'created_by': 1} 
          400:
            description: For exceptions like not json data, special characters or numbers 
            schema:
              id: Invalid name with special characters or numbers or invalid json being added
              properties:
                name:
                  type: string
                  default: '@@@@111'
                response:
                  type: string
                  default: Category name should not have special characters or numbers
          422:
            description: If space or nothing is entered for name
            schema:
              id: Add empty category
              properties:
                name:
                  type: string
                  default: " "
                response:
                  type: string
                  default: Category name required
        """
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
         # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # Go ahead and handle the request, the user is authenticated

                if request.method == "POST":
                    # name = str(request.data.get('name', ''))
                    name = request.data.get('name')
                    
                    if isinstance(name, int):
                        return jsonify({"message": "category name should not be an integer" }),400
                    if not name or name.isspace():
                        return jsonify({'message': 'Category name is required'}),422
                    if is_valid(name):
                        return jsonify({'message': 'Category name should not have special characters'}),400
                    if hasNumbers(name):
                        return jsonify({'message': 'Category name should not have numbers'}),400
                    
                    name = name.title()
                    result = Category.query.filter_by(name=name, created_by=user_id).first()

                    if result:
                        return jsonify({"message": "Category already exists"}),400

                    category = Category(name=name, created_by=user_id)
                    category.save()
                    response = jsonify({
                        'message': 'Category ' + category.name +
                        ' has been created',
                        'category': {
                            'id': category.id,
                            'name': category.name,
                            'date_created': category.date_created,
                            'date_modified': category.date_modified,
                            'created_by': user_id,
                            'status': True
                        }
                    })

                    return make_response(response), 201
            else:
                # user is not legit, so the payload is an error message for expired token
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401

    @app.route('/api/v1/categories/', methods=['GET'])
    def get_categories():
        """
        This method is for getting categories
        ---
        tags:
          - Category functions
        parameters:

          - in: query
            name: q
            required: false
            type: string
            description: search category by querying the name
          - in: query
            name: page
            required: false
            type: integer
            description: search categories by querying the page number
          - in: query
            name: per_page
            required: false
            type: integer
            description: search by specifying number of items on a page
        security:
          - TokenHeader: []

        responses:
          200:
            description:  category successfully retrieved 
          201:
            description: For getting a valid categoryname by q or pagination
            schema:
              id: successful retrieve of category
              properties:
                name:
                  type: string
                  default: Lunch
                response:
                  type: string
                  default: {'id': 1, 'name': Lunch, 'date_created': 22-12-2017, 'date_modified': 22-12-2017, 'created_by': 1}
          400:
            description: Searching for a name that is not there or invalid
            schema:
              id: invalid GET
              properties:
                name:
                  type: string
                  default: '33erdg@@'
                response:
                  type: string
                  default: No category found
        """
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]
        if access_token:
         # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                    # GET all the categories created by this user
                    # GET METHOD/categories/
                page = int(request.args.get('page', 1))
                per_page = int(request.args.get('per_page', 5))
                q = str(request.args.get('q', '')).title()
                categories = Category.query.filter_by(
                    created_by=user_id).paginate(page=page, per_page=per_page)
                results = []
                # if not categories:
                #     return jsonify({'message': 'No categories available'}),404
                if q:
                    for category in categories.items:
                        if q in category.name:
                            obj = {}
                            obj = {
                                'id': category.id,
                                'name': category.name,
                                'date_created': category.date_created,
                                'date_modified': category.date_modified,
                                'created_by': category.created_by
                            }
                            results.append(obj)
                else:
                    for category in categories.items:
                        obj = {}
                        obj = {
                            'id': category.id,
                            'name': category.name,
                            'date_created': category.date_created,
                            'date_modified': category.date_modified,
                            'created_by': category.created_by
                        }
                        results.append(obj)

                # return make_response(jsonify(results)), 200
                if results:
                    return jsonify({'categories': results})
                else:
                    return jsonify({"message": "No category found"}),404
            else:
                # user is not legit, so the payload is an error message for expired token
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401

    @app.route('/api/v1/categories/<int:id>', methods=['DELETE'])
    def delete_category(id, **kwargs):
        """
        This method is for delete category by id
        ---
        tags:
          - Category functions
        parameters:

          - in: path
            name: id
            required: true
            type: integer
            description: delete a category by specifying its id
        security:
          - TokenHeader: []

        responses:
          200:
            description:  category successfully deleted 
          201:
            description: For successful deletion of an existing category
            schema:
              id: successful deletion
              properties:
                id:
                  default: 1
                response:
                  type: string
                  default: category 1 deleted
          400:
            description: Deleting a category which doesnot exist
            schema:
              id: invalid Delete
              properties:
                id:
                  type: string
                  default: 100
                response:
                  type: string
                  default: No category found to delete

        """
        # retrieve a category using it's ID
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Get the user id related to this access token
            user_id = User.decode_token(access_token)

            if not isinstance(user_id, str):
                # If the id is not a string(error), we have a user id
                # Get the category with the id specified from the URL (<int:id>)
                category = Category.query.filter_by(id=id).first()
                if not category:
                    # There is no category with this ID for this User, so return http code
                    return jsonify({"message": "No category to delete"}),204
                if request.method == "DELETE":
                    # delete the category using our delete method
                    category.delete()
                    return {
                        "message": "category {} deleted".format(category.id)
                    }, 200
            else:
                # user is not legit, so the payload is an error message to handle expired token
                message = user_id
                response = {
                    'message': message
                }
                # return an error response, telling the user he is Unauthorized
                return make_response(jsonify(response)), 401

    @app.route('/api/v1/categories/<int:id>', methods=['PUT'])
    def edit_category(id, **kwargs):
        """
        This method is for editing categories
        ---
        tags:
          - Category functions
        parameters:
          - in: path
            name: id
            required: true
            type: integer
            description: first specify the category id
          - in: body
            name: body
            required: true
            type: string
            description: input new json data to replace the existing on
        security:
          - TokenHeader: []
        responses:
          200:
            description:  category successfully updated 
          201:
            description: For successful update of an existing category
            schema:
              id: successful update
              properties:
                id:
                  default: 1
                name:
                  type: string
                  default: Supper
                response:
                  type: string
                  default: {'id': 1, 'name': Supper, 'date_created': 22-12-2017, 'date_modified': 22-12-2017, 'created_by': 1}
          400:
            description: updating category which doesnot exist
            schema:
              id: invalid update
              properties:
                id:
                  type: string
                  default: 100
                response:
                  type: string
                  default: No category found to edit
        """
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                category = Category.query.filter_by(id=id).first()
                if not category:
                    return jsonify({"message": "No category found to edit"}),204
                else:
                    name = str(request.data.get('name', ''))
                    category.name = name
                    category.save()
                    response = {
                        'message': 'Category has been updated',
                        'newcategory': {
                            'id': category.id,
                            'name': category.name,
                            'date_created': category.date_created,
                            'date_modified': category.date_modified,
                            'created_by': category.created_by
                        }
                    }
                    return make_response(jsonify(response)), 200
            else:
                # user is not legit, so the payload is an error message to handle expired token
                message = user_id
                response = {
                    'message': message
                }
                # return an error response, telling the user he is Unauthorized
                return make_response(jsonify(response)), 401

    @app.route('/api/v1/categories/<int:id>', methods=['GET'])
    def get_category_by_id(id, **kwargs):
        """
        This method is for getting category by id
        ---
        tags:
          - Category functions
        parameters:
          - in: path
            name: id
            required: true
            type: integer
            description: search by a category id
        security:
          - TokenHeader: []

        responses:
          200:
            description:  category successfully retrieved 
          201:
            description: For getting a valid categoryname by id
            schema:
              id: successful retrieve by id
              properties:
                id:
                  type: integer
                  default: 1
                response:
                  type: string
                  default: {'id': 1, 'name': Lunch, 'date_created': 22-12-2017, 'date_modified': 22-12-2017, 'created_by': 1}
          400:
            description: Searching for the id that is not there
            schema:
              id: invalid GET by id
              properties:
                name:
                  type: integer
                  default: 100
                response:
                  type: string
                  default: No category found with that id
        """
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                category = Category.query.filter_by(id=id).first()
                if not category:
                    return jsonify({"message": "No category found by id"}),404
                else:
                    # Handle GET request, sending back category to the user
                    response = {
                        "message": "category {} found".format(category.id),
                        'category': {
                            'id': category.id,
                            'name': category.name,
                            'date_created': category.date_created,
                            'date_modified': category.date_modified,
                            'created_by': category.created_by
                        }
                    }
                    return make_response(jsonify(response)), 200
            else:
                # user is not legit, so the payload is an error message to handle expired token
                message = user_id
                response = {
                    'message': message
                }
                # return an error response, telling the user he is Unauthorized
                return make_response(jsonify(response)), 401

    @app.route('/api/v1/categories/<int:id>/recipes', methods=['POST'])
    def add_recipes(id,  **kwargs):
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
                  default: {'id': 1, 'title': pilau, 'description': burn onions, 'date_created': 22-12-2017, 'date_modified': 22-12-2017, 'category_identity': 1} 
          400:
            description: For exceptions like not json data, special characters or numbers in the recipes
            schema:
              id: Invalid name with special characters or numbers or invalid json being added in the recipe
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
        if request.method == "POST":
            title = str(request.data.get('title', ''))
            description = str(request.data.get('description', ''))
            if isinstance(title, int):
                return jsonify({"message": "Recipe title should not be an integer"}),400
            if is_valid(title):
                return jsonify({'message': 'Recipe title should not have special characters'}),400
            if hasNumbers(title):
                return jsonify({'message': 'Recipe title should not have numbers'}),400
            if not title or title.isspace():
                return jsonify({'message': 'Recipe title is mostly required'}),422
            result = Recipe.query.filter_by(title=title, category_identity=id).first()
            if result:
                return jsonify({"message": "Recipe already exists"}),400
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

    @app.route('/api/v1/categories/<int:id>/recipes', methods=['GET'])
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
                  default: {'id': 1, 'title': pilau, 'description': burn onions, 'date_created': 22-12-2017, 'date_modified': 22-12-2017, 'category_identity': 1} 
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
        # GET all the categories created by this user
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 5))
        q = str(request.args.get('q', '')).lower()
        recipes = Recipe.query.filter_by(
            category_identity=id).paginate(page=page, per_page=per_page)
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
                    'category_identity': id

                }
                results.append(obj)
            # return make_response(jsonify(results)), 200
        if results:
            return jsonify({'recipes': results})
        else:
            return jsonify({"message": "No recipes found"}),404

    @app.route('/api/v1/categories/<int:id>/recipes/<int:recipe_id>', methods=['DELETE'])
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
        # retrieve a recipe using it's ID
        recipe = Recipe.query.filter_by(id=recipe_id).first()
        if not recipe:
            return jsonify({"message":"No recipes with that id to delete "}),204

        else:
            recipe.delete()
            return {
                "message": "recipe {} deleted successfully".format(recipe.id)
            }, 200
    @app.route('/api/v1/categories/<int:id>/recipes/<int:recipe_id>', methods=['PUT'])
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
                  default: {'id': 1, 'title': milkshake, 'description': mix with coffee, date_created': 22-12-2017, 'date_modified': 22-12-2017, 'category_id': 1}
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
                # retrieve a recipe using it's ID
        recipe = Recipe.query.filter_by(id=recipe_id).first()
        if not recipe:
            return jsonify({"message":"No recipes with that id to edit "}),204
        else:
            title = str(request.data.get('title', ''))
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
    @app.route('/api/v1/categories/<int:id>/recipes/<int:recipe_id>', methods=['GET'])
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
        # retrieve a recipe using it's ID
        recipe = Recipe.query.filter_by(id=recipe_id).first()
        if not recipe:
            return jsonify({"message":"No recipes with that id to get"}),400
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
    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
# app = create_app(config_name="development")
