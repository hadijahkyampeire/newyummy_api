from .import category
from flask import request, jsonify, abort, make_response
from app.models import Category, User, Recipe

def is_valid(name_string):    
    special_character = "~!@#$%^&*()_={}|\[]<>?/,;:"
    return any(char in special_character for char in name_string)
def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


@category.route('/api/v1/categories/', methods=['POST'])
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

@category.route('/api/v1/categories/', methods=['GET'])
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
    access_token = auth_header.split()[1]
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

@category.route('/api/v1/categories/<int:id>', methods=['DELETE'])
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
            category = Category.query.filter_by(id=id,created_by=user_id).first()
            if not category:
                # There is no category with this ID for this User, so return http code
                return jsonify({"message": "No category to delete"}),404
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

@category.route('/api/v1/categories/<int:id>', methods=['PUT'])
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
                return jsonify({"message": "name already exists"}),400
            category = Category.query.filter_by(id=id,created_by=user_id).first()
            if not category:
                return jsonify({"message": "No category found to edit"}),404
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


@category.route('/api/v1/categories/<int:id>', methods=['GET'])
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
            category = Category.query.filter_by(id=id,created_by=user_id).first()
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


