import re
from flask import request, jsonify, make_response, url_for
from app.models import Category, User
from .import category
from flasgger import swag_from
from .validations import valid_category, is_valid, has_numbers, authentication


@category.route('/api/v1/categories/', methods=['POST'])
@authentication
@swag_from('/app/docs/addcategories.yml')
def add_categories(user_id):
    """This route handles posting categories"""

    if request.method == "POST":
        name = str(request.data.get('name')).strip()
        name = re.sub(' +',' ', name)
        resultn = valid_category(name)
        if resultn:
            return jsonify(resultn), 400
        name = name.title()
        result = Category.find_by_name(name, user_id)
        if result:
            return jsonify({"message": "Category already exists"}), 400
        category_ = Category(name=name, created_by=user_id)
        category_.save()
        response1 = category_.category_json()
        response = jsonify({
            'message': 'Category' + category_.name +
            'has been created',
            'Recipes': url_for('recipe.get_recipes',
                               id=category_.id,
                               _external=True),
            'category': response1
        })
        return make_response(response), 201


@category.route('/api/v1/categories/', methods=['GET'])
@authentication
@swag_from('/app/docs/getcategories.yml')
def get_categories(user_id):
    """This route handles getting categories"""

    # GET all the categories by q or pagination
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 8, type=int)
    search_query = str(request.args.get('q', '')).title()
    categories = Category.query.filter(
        Category.created_by == user_id)

    if search_query:
        categories = categories.filter(Category.name.ilike(
            '%' + search_query.strip().title() + '%'))
    categories = categories.order_by(Category.date_created.desc()).paginate(
        page=page, per_page=limit, error_out=False)
    results = []
    for cat in categories.items:
        results.append({
            'cat': cat.category_json(),
            'Recipes': url_for('recipe.get_recipes',
                                id=cat.id, _external=True)
        })

    
    pagination_details = {
            'Next_page': categories.next_num,
            'current_page': categories.page,
            'Previous_page': categories.prev_num,
            'total_Items': categories.total,
            'total_pages':categories.pages,}

    if results:
        return jsonify({'categories': results, **pagination_details}), 200
    return jsonify({"message": "No category found"}), 404


@category.route('/api/v1/categories/<int:id>', methods=['DELETE'])
@authentication
@swag_from('/app/docs/deletecategory.yml')
def delete_category(user_id, id, **kwargs):
    """This route handles deleting categories by id"""

    category = Category.find_user_by_id(id, user_id)
    if not category:
        return jsonify({"message": "No category to delete"}), 404
    if request.method == "DELETE":
        category.delete()
        return {"message": "category {} deleted".format(category.name)}, 200


@category.route('/api/v1/categories/<int:id>', methods=['PUT'])
@authentication
@swag_from('/app/docs/updatecategory.yml')
def edit_category(user_id, id, **kwargs):
    """This route handles updating categories by id"""

    name = str(request.data.get('name')).strip()
    result2 = valid_category(name)
    if result2:
        return jsonify(result2), 400
    name = name.title()
    result = Category.find_by_name(name, user_id)
    if result:
        return jsonify({"message": "name already exists"}), 400
    category = Category.find_user_by_id(id, user_id)
    if not category:
        return jsonify({"message": "No category found to edit"}), 404

    name = str(request.data.get('name', ''))
    category.name = name
    category.save()
    response2 = category.category_json()
    response = {
        'message': 'Category has been updated',
        'newcategory': response2,
        'Recipes': url_for('recipe.get_recipes',
                            id=category.id, _external=True)
    }
    return make_response(jsonify(response)), 200


@category.route('/api/v1/categories/<int:id>', methods=['GET'])
@authentication
@swag_from('/app/docs/getcategory.yml')
def get_category_by_id(user_id, id, **kwargs):
    """This route handles getting categories by id"""

    category = Category.find_user_by_id(id, user_id)
    if not category:
        return jsonify({"message": "No category found by id"}), 404
    else:
        response3 = category.category_json()
        response = {
            "message": "category {} found".format(category.id),
            'category': response3,
            'Recipes': url_for('recipe.get_recipes',
                                id=category.id, _external=True)
        }
        return make_response(jsonify(response)), 200

