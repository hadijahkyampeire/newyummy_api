# import unittest
# import json
# from app import create_app, db
# from app.models import Category, User, Recipe

# class RecipeTestCase(unittest.TestCase):
#     """This class represents the recipes test case"""

#     def setUp(self):
#         """Define test variables and initialize app."""
#         self.app = create_app(config_name="testing")
#         self.client = self.app.test_client
#         self.recipe = {'title': 'ab', 'description': 'mix well' ,'category_identity': 1}

#         # binds the app to the current context
#         with self.app.app_context():
#             # create all tables
#             db.create_all()
#     def tearDown(self):
#         """teardown all initialized variables."""
#         with self.app.app_context():
#             # drop all tables
#             db.session.remove()
#             db.drop_all()

#     def register_user(self, email="user@test.com", password="test1234"):
#         """This helper method helps register a test user."""
#         user_data = {
#             'email': email,
#             'password': password
#         }
#         return self.client().post('/auth/register', data=user_data)

#     def login_user(self, email="user@test.com", password="test1234"):
#         """This helper method helps log in a test user."""
#         user_data = {
#             'email': email,
#             'password': password
#         }
#         return self.client().post('/auth/login', data=user_data)

#     def test_recipe_creation(self):
#         """Test API can create a recipe (POST request)"""
#         # obtain the access token
#         self.register_user()
#         result = self.login_user()
#         # obtain the access token
#         access_token = json.loads(result.data.decode())['access_token']
#         user_id = User.decode_token(access_token)

#         category = Category(name='lunch', created_by=user_id)
#         category.save()
#         res = self.client().post('/categories/2/recipes', data=self.recipe)
#         self.assertEqual(res.status_code, 201)
#         self.assertIn('b',str(res.data))
#         self.assertIn('mix well',str(res.data))

#     def test_api_can_get_all_recipes(self):
#         """Test API can get a recipe (GET request)."""
#         res = self.client().post('/categories/1/recipes', data=self.recipe)
#         self.assertEqual(res.status_code, 201)

#         res = self.client().get('/categories/1/recipes')
#         self.assertEqual(res.status_code, 200)
#         # self.assertIn('a',str(res.data))
#         # self.assertIn('mix well',str(res.data))

#     def test_api_can_get_recipe_by_id(self):
#         """Test API can get a single recipe by using it's id."""
#         rv = self.client().post('/categories/1/recipes/1', data=self.recipe)
#         self.assertEqual(rv.status_code, 201)
#         # results = json.loads(rv.data.decode())
#         result = self.client().get(
#             'categories/1/recipes/1',)
#         self.assertEqual(result.status_code, 200)
#         self.assertIn('ab',str(result.data))
#         self.assertIn('mix well',str(result.data))

#     def test_recipe_can_be_edited(self):
#         """Test API can edit an existing recipe. (PUT request)"""
#         rv = self.client().post(
#             '/categories/1/recipes/1',
#             data={'title': 'a', 'description': 'mix well'})
#         self.assertEqual(rv.status_code, 201)
#         rv = self.client().put(
#             '/categories/1/recipes/1',
#             data={
#                 "title": "juice :-)", "description": " blend :-)"
#             })
#         self.assertEqual(rv.status_code, 200)
#         results = self.client().get('/categories/<int:id>/recipes/<int:recipe_id>')
#         # self.assertIn('juice', 'blend',str(results.data))

#     def test_recipe_deletion(self):
#         """Test API can delete an existing recipe. (DELETE request)."""
#         rv = self.client().post(
#             '/categories/<int:id>/recipes',
#             data={'title': 'milk', 'description': 'mix well'})
#         self.assertEqual(rv.status_code, 200)
#         res = self.client().delete('/categories/<int:id>/recipes/<int:recipe_id>')
#         self.assertEqual(res.status_code, 200)
#         # Test to see if it exists, should return a 404
#         result = self.client().get('/categories/<int:id>/recipes/<int:recipe_id>')
#         self.assertEqual(result.status_code, 404)
#     if __name__ == "__main__":
#     unittest.main()
