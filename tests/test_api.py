import unittest
import os
import json
from app import create_app, db

class CategoryTestCase(unittest.TestCase):
    """This class represents the category test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.category = {'name': 'supper'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()
    def register_user(self, email="user@test.com", password="test1234"):
        """This helper method helps register a test user."""
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/auth/register', data=user_data)

    def login_user(self, email="user@test.com", password="test1234"):
        """This helper method helps log in a test user."""
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/auth/login', data=user_data)

    def test_category_creation(self):
        """Test the API can create a category (POST request)"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']

        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        self.assertEqual(res.status_code, 201)
        self.assertIn('supper', str(res.data))

    def test_api_can_get_all_categories(self):
        """Test API can get a category (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        self.assertEqual(res.status_code, 201)

        # get all the categories that belong to the test user by making a GET request
        res = self.client().get(
            '/categories/',
            headers=dict(Authorization="Bearer " + access_token),
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('supper', str(res.data))

    def test_api_can_get_category_by_id(self):
        """Test API can get a single category by using it's id."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        self.assertEqual(rv.status_code, 201)
        results = json.loads(rv.data.decode())

        result = self.client().get(
            '/categories/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        # assert that the category is actually returned given its ID
        self.assertEqual(result.status_code, 200)
        self.assertIn('supper', str(result.data))

    def test_category_can_be_edited(self):
        """Test API can edit an existing category. (PUT request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # first, we create a category by making a POST request
        rv = self.client().post(
            '/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'lunch, supper'})
        self.assertEqual(rv.status_code, 201)
        # get the json with the category
        results = json.loads(rv.data.decode())

        # then, we edit the created category by making a PUT request
        rv = self.client().put(
            '/categories/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "name": "dinner, dissert :-)"
            })
        self.assertEqual(rv.status_code, 200)

        # finally, we get the edited category to see if it is actually edited.
        results = self.client().get(
            '/categories/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('dinner', str(results.data))
    def test_category_deletion(self):
        """Test API can delete an existing category. (DELETE request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'lunch'})
        self.assertEqual(rv.status_code, 201)
        # get the category in json
        results = json.loads(rv.data.decode())

        # delete the category we just created
        res = self.client().delete(
            '/categories/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),)
        self.assertEqual(res.status_code, 200)

        # Test to see if it exists, should return a 404
        result = self.client().get(
            '/categories/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 404)

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()
class RecipeTestCase(unittest.TestCase):
    """This class represents the recipes test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.recipe = {'title': 'milk', 'description': 'mix well'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def test_recipe_creation(self):
        """Test API can create a recipe (POST request)"""
        res = self.client().post('/recipes/', data=self.recipe)
        self.assertEqual(res.status_code, 201)
        # self.assertIn( (res.data))

    def test_api_can_get_all_recipes(self):
        """Test API can get a recipe (GET request)."""
        res = self.client().post('/recipes/', data=self.recipe)
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/recipes/')
        self.assertEqual(res.status_code, 200)
        # self.assertIn('milk','mix well', str(res.data))

    def test_api_can_get_recipe_by_id(self):
        """Test API can get a single recipe by using it's id."""
        rv = self.client().post('/recipes/', data=self.recipe)
        self.assertEqual(rv.status_code, 201)
        result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
        result = self.client().get(
            '/recipes/{}'.format(result_in_json['id']))
        self.assertEqual(result.status_code, 200)
        # self.assertIn('milk','mix well', str(result.data))

    def test_recipe_can_be_edited(self):
        """Test API can edit an existing recipe. (PUT request)"""
        rv = self.client().post(
            '/recipes/',
            data={'title': 'milk' , 'description':'mix well'})
        self.assertEqual(rv.status_code, 201)
        rv = self.client().put(
            '/recipes/1',
            data={
                "title": "juice :-)", "description": " blend :-)"
            })
        self.assertEqual(rv.status_code, 200)
        results = self.client().get('/recipes/1')
        # self.assertIn('juice', 'blend',str(results.data))

    def test_recipe_deletion(self):
        """Test API can delete an existing recipe. (DELETE request)."""
        rv = self.client().post(
            '/recipes/',
            data={'title': 'milk', 'description': 'mix well'})
        self.assertEqual(rv.status_code, 201)
        res = self.client().delete('/recipes/1')
        self.assertEqual(res.status_code, 200)
        # Test to see if it exists, should return a 404
        result = self.client().get('/recipes/1')
        self.assertEqual(result.status_code, 404)

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()