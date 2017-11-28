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
    app.config.from_object(app_config["development"])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    @app.route('/categories/', methods=['POST', 'GET'])
    def categories():
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
         # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # Go ahead and handle the request, the user is authenticated

                if request.method == "POST":
                    name = str(request.data.get('name', ''))
                    if name:
                        category = Category(name=name, created_by=user_id)
                        category.save()
                        response = jsonify({
                            'id': category.id,
                            'name': category.name,
                            'date_created': category.date_created,
                            'date_modified': category.date_modified,
                            'created_by': user_id
                        })

                        return make_response(response), 201

                else:
                    # GET all the bucketlists created by this user
                    categories = Category.query.filter_by(created_by=user_id)
                    results = []

                    for category in categories:
                        obj = {
                            'id': category.id,
                            'name': category.name,
                            'date_created': category.date_created,
                            'date_modified': category.date_modified,
                            'created_by': category.created_by
                        }
                        results.append(obj)

                    return make_response(jsonify(results)), 200
            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401
    
    @app.route('/categories/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def category_manipulation(id, **kwargs):
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
                    # There is no category with this ID for this User, so
                    # Raise an HTTPException with a 404 not found status code
                    abort(404)

                if request.method == "DELETE":
                    # delete the category using our delete method
                    category.delete()
                    return {
                        "message": "category {} deleted".format(category.id)
                    }, 200

                elif request.method == 'PUT':
                    # Obtain the new name of the category from the request data
                    name = str(request.data.get('name', ''))

                    category.name = name
                    category.save()

                    response = {
                        'id': category.id,
                        'name': category.name,
                        'date_created': category.date_created,
                        'date_modified':category.date_modified,
                        'created_by': category.created_by
                    }
                    return make_response(jsonify(response)), 200
                else:
                    # Handle GET request, sending back category to the user
                    response = {
                        'id': category.id,
                        'name': category.name,
                        'date_created': category.date_created,
                        'date_modified': category.date_modified,
                        'created_by': category.created_by
                    }
                    return make_response(jsonify(response)), 200
            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                # return an error response, telling the user he is Unauthorized
                return make_response(jsonify(response)), 401
    @app.route('/categories/<int:id>/recipes', methods=['POST', 'GET'])
    def recipes(id, **kwargs):
        
        Category.query.filter_by(id = id ).first()
        if request.method == "POST":
            title = str(request.data.get('title', ''))
            description = str(request.data.get('description', ''))
            if title and description:
                recipe = Recipe(title=title, description=description, category_identity = id)
                recipe.save()
                response = jsonify({
                'id': recipe.id,
                'title': recipe.title,
                'description': recipe.description,
                'date_created': recipe.date_created,
                'date_modified': recipe.date_modified,
                'category_identity':id

            })
        
            response.status_code = 201
            return response
            
        else:
            # GET
            recipes = Recipe.query.filter_by(category_identity=id)
            results = []

            for recipe in recipes:
                obj = {
                    'id': recipe.id,
                    'title': recipe.title,
                    'description': recipe.description,
                    'date_created': recipe.date_created,
                    'date_modified': recipe.date_modified,
                    'category_identity':id
                    
                }
                results.append(obj)
            response = jsonify(results)
            response.status_code = 200
            return response

    @app.route('/categories/<int:id>/recipes/<int:recipe_id>', methods=['GET', 'PUT', 'DELETE'])
    def recipe_manipulation(id, recipe_id, **kwargs):
        Category.query.filter_by(id = id ).first()
     # retrieve a recipe using it's ID
        recipe = Recipe.query.filter_by(id=recipe_id).first()
        if not recipe:
            # Raise an HTTPException with a 404 not found status code
            abort(404)

        if request.method == 'DELETE':
            recipe.delete()
            return {
            "message": "recipe {} deleted successfully".format(recipe.id) 
         }, 200

        elif request.method == 'PUT':
            title = str(request.data.get('title', ''))
            description = str(request.data.get('description', ''))
            recipe.title= title
            recipe.description=description
            recipe.save()
            response = jsonify({
                'id': recipe.id,
                'title': recipe.title,
                'description': recipe.description,
                'date_created': recipe.date_created,
                'date_modified': recipe.date_modified,
                'category_identity':id
            })
            response.status_code = 200
            return response
        else:
            # GET
            response = jsonify({
                'id': recipe.id,
                'title': recipe.title,
                'description': recipe.description,
                'date_created': recipe.date_created,
                'date_modified': recipe.date_modified,
                'category_identity':id
            })
            response.status_code = 200
            return response
    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
