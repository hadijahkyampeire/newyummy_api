from flask import request, jsonify, make_response
from app.models import Category, User
from .import category
from flasgger import swag_from
from .validations import valid_category, is_valid, has_numbers

@category.route('/api/v1/categories/', methods=['POST'])
@swag_from('/app/docs/addcategories.yml')
def add_categories():
    """This route handles posting categories"""
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return jsonify({"message": "No token, please provide a token"}),401
    access_token = auth_header.split(" ")[1]
    if access_token:
        # Attempt to decode the token and get the User ID
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):
            # Go ahead and handle the request, the user is authenticated
            if request.method == "POST":
                name = str(request.data.get('name')).strip()
                resultn = valid_category(name)
                if resultn:
                    return jsonify(resultn), 400
                name = name.title()
                result = Category.find_by_name(name, user_id)
                if result:
                    return jsonify({"message": "Category already exists"}),400
                category = Category(name= name, created_by= user_id)
                category.save()
                response1 = category.category_json()
                response = jsonify({
                    'message': 'Category ' + category.name +
                    ' has been created', 
                     'category': response1
                })
                return make_response(response), 201
        else:
            # user is not legit,an error message for expired token
            message = user_id
            return jsonify({'message': message}), 401


@category.route('/api/v1/categories/', methods=['GET'])
@swag_from('/app/docs/getcategories.yml')
def get_categories():
    """This route handles getting categories"""
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return jsonify({"message": "No token, please provide a token"}), 401
    access_token = auth_header.split()[1]
    if access_token:
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):
            # GET all the categories by q or pagination
            page = request.args.get('page', 1, type=int)
            limit = request.args.get('limit', 2, type=int)
            q = str(request.args.get('q', '')).title()
            categories = Category.query.filter_by(
                created_by=user_id).paginate(page=page, per_page=limit,
                                             error_out=False)
            results = []
            if q:
                for category in categories.items:
                    if q in category.name:
                        obj = category.category_json()
                        results.append(obj)
            else:
                for category in categories.items:
                    obj = {}
                    obj = {
                        'id': category.id,
                        'name': category.name,
                        'date_created': category.date_created,
                        'date_modified': category.date_modified,
                        'created_by': category.created_by,
                        'Next_page': categories.next_num,
                        'Previous_page': categories.prev_num
                    }
                    results.append(obj)

            if len(results) <= 0:
                return jsonify({"message": "No categories on that page"}), 404
            if results:
                return jsonify({'categories': results}), 200
            else:
                return jsonify({"message": "No category found"}), 404
        else:
            message = user_id
            return jsonify({'message': message}), 401


@category.route('/api/v1/categories/<int:id>', methods=['DELETE'])
@swag_from('/app/docs/deletecategory.yml')
def delete_category(id, **kwargs):
    """This route handles deleting categories by id"""
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return jsonify({"message": "No token, please provide a token"}), 401
    access_token = auth_header.split(" ")[1]
    if access_token:
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):
            category = Category.find_by_id(id, user_id)
            if not category:
                return jsonify({"message": "No category to delete"}), 404
            if request.method == "DELETE":
                category.delete()
                return {"message": "category {} deleted".format(category.id)}, 200
        else:
            message = user_id
            return jsonify({'message': message}), 401


@category.route('/api/v1/categories/<int:id>', methods=['PUT'])
@swag_from('/app/docs/updatecategory.yml')
def edit_category(id, **kwargs):
    """This route handles updating categories by id"""
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return jsonify({"message": "No token, please provide a token"}), 401
    access_token = auth_header.split(" ")[1]
    if access_token:
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):
            name = str(request.data.get('name')).strip()
            result2 = valid_category(name)
            if result2:
                return jsonify(result2), 400
            name = name.title()
            result = Category.find_by_name(name, user_id)
            if result:
                return jsonify({"message": "name already exists"}), 400
            category = Category.find_by_id(id, user_id)
            if not category:
                return jsonify({"message": "No category found to edit"}), 404
            else:
                name = str(request.data.get('name', ''))
                category.name = name
                category.save()
                response2 = category.category_json()
                response = {
                    'message': 'Category has been updated',
                    'newcategory': response2
                }
                return make_response(jsonify(response)), 200
        else:
            # user is not legit,an error message to handle expired token
            message = user_id
            return jsonify({'message': message}), 401


@category.route('/api/v1/categories/<int:id>', methods=['GET'])
@swag_from('/app/docs/getcategory.yml')
def get_category_by_id(id, **kwargs):
    """This route handles getting categories by id"""
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return jsonify({"message": "No token, please provide a token"}), 401
    access_token = auth_header.split()[1]
    if access_token:
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):
            category = Category.find_by_id(id, user_id)
            if not category:
                return jsonify({"message": "No category found by id"}), 404
            else:
                response3 = category.category_json()
                response = {
                    "message": "category {} found".format(category.id),
                    'category': response3
                }
                return make_response(jsonify(response)), 200
        else:
            message = user_id
            return jsonify({'message': message}), 401


