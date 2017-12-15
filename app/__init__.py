from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort, make_response

# local import
from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()


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
                    if not name or name.isspace():
                        return jsonify({'message': 'Category name is required'}),422
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
                    abort(404)

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
        """
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                category = Category.query.filter_by(id=id).first()
                if not category:
                    abort(404)
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

        """
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                category = Category.query.filter_by(id=id).first()
                if not category:
                    abort(404)
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

        """
        if request.method == "POST":
            title = str(request.data.get('title', ''))
            description = str(request.data.get('description', ''))
            if not title or not description or title.isspace() or description.isspace():
                return jsonify({'message': 'Recipe title and description are required', 'status': False})
            result = Recipe.query.filter_by(title=title).first()
            if result:
                return jsonify({"message": "Recipe already exists"})
            if title and description:
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

        """
        # retrieve a recipe using it's ID
        recipe = Recipe.query.filter_by(id=recipe_id).first()
        if not recipe:
            # Raise an HTTPException with a 404 not found status code
            abort(404)

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
            description:  category successfully updated 
        """
                # retrieve a recipe using it's ID
        recipe = Recipe.query.filter_by(id=recipe_id).first()
        if not recipe:
            # Raise an HTTPException with a 404 not found status code
            abort(404)
        title = str(request.data.get('title', ''))
        description = str(request.data.get('description', ''))
        if not title or not description or title.isspace() or description.isspace():
            return jsonify({'message': 'Recipe title and description are required', 'status': False})
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

        """
        # retrieve a recipe using it's ID
        recipe = Recipe.query.filter_by(id=recipe_id).first()
        if not recipe:
            # Raise an HTTPException with a 404 not found status code
            abort(404)
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
