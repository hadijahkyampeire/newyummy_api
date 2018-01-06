import unittest
import json
from app import create_app, db
from app.models import Category, User, Recipe

class RecipeTestCase(unittest.TestCase):
    """This class represents the recipes test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.category = {'name': 'Supper'}
        self.recipe = {'title': 'fruit', 'description': 'mix well'}
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
        return self.client().post('/api/v1/auth/register', data=user_data)

    def login_user(self, email="user@test.com", password="test1234"):
        """This helper method helps log in a test user."""
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/api/v1/auth/login', data=user_data)

    def test_recipe_creation(self):
        """Test API can create a recipe (POST request)"""
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']

        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        self.assertIn('Supper', str(res.data))

        result = self.client().post(
            '/api/v1/categories/1/recipes',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.recipe)
        self.assertEqual(res.status_code, 201)
        self.assertIn('fruit', str(result.data))

    def test_api_can_get_all_recipes(self):
        """Test API can get a recipe (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        result = self.client().get(
            '/api/v1/categories/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('Supper', str(result.data))
        res = self.client().post('/api/v1/categories/1/recipes', 
         headers=dict(Authorization="Bearer " + access_token),
         data=self.recipe)
        res = self.client().get('/api/v1/categories/1/recipes',
         headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)
        self.assertIn('fruit',str(res.data))
        
    def test_api_can_get_recipes_by_pagination(self):
        """Test API can get a recipe by pagination (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        result = self.client().get(
            '/api/v1/categories/1',
            headers=dict(Authorization="Bearer " + access_token))
        # assert that the category is actually returned by pagination
        self.assertIn('Supper', str(result.data))
        res = self.client().post('/api/v1/categories/1/recipes', 
           headers=dict(Authorization="Bearer " + access_token),
           data=self.recipe)
        res = self.client().get('/api/v1/categories/1/recipes?page=1&per_page=1',
         headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)
        self.assertIn('fruit',str(res.data))
        
    def test_api_can_get_arecipe_by_q(self):
        """Test API can get a recipe by q search (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        result = self.client().get(
            '/api/v1/categories/1',
            headers=dict(Authorization="Bearer " + access_token))
        # assert that the category is actually returned by q
        self.assertIn('Supper', str(result.data))
        res = self.client().post('/api/v1/categories/1/recipes', 
         headers=dict(Authorization="Bearer " + access_token),
         data=self.recipe)
        res = self.client().get('/api/v1/categories/1/recipes?q=fruit',
         headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)
        self.assertIn('fruit',str(res.data))

    def test_api_can_get_recipe_by_id(self):
        """Test API can get a single recipe by using it's id."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        result = self.client().get(
            '/api/v1/categories/1',
            headers=dict(Authorization="Bearer " + access_token))
        # assert that the category is actually returned given its ID
        self.assertIn('Supper', str(result.data))
        res = self.client().post('/api/v1/categories/1/recipes', 
         headers=dict(Authorization="Bearer " + access_token),
         data=self.recipe)
        result = self.client().get(
            '/api/v1/categories/1/recipes/1',headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 200)
        self.assertIn('fruit',str(result.data))

    def test_recipe_can_be_edited(self):
        """Test API can edit an existing recipe. (PUT request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        result = self.client().get(
            '/api/v1/categories/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('Supper', str(result.data))
        res = self.client().post('/api/v1/categories/1/recipes', 
         headers=dict(Authorization="Bearer " + access_token),
         data=self.recipe)
        rv = self.client().put(
            '/api/v1/categories/1/recipes/1',headers=dict(Authorization="Bearer " + access_token),
            data={
                "title": "salads" ,"description":"blend"
            })
        self.assertEqual(rv.status_code, 200)
        results = self.client().get('/api/v1/categories/1/recipes/1',
         headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('salads',str(results.data))  

    def test_recipe_deletion(self):
        """Test API can delete an existing recipe. (DELETE request)."""
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        self.assertIn('Supper', str(res.data))
        result = self.client().post(
            '/api/v1/categories/1/recipes',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.recipe)
        self.assertIn('fruit', str(result.data))
        rv = self.client().delete(
            '/api/v1/categories/1/recipes/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(rv.status_code, 200)
        # Test to see if it exists, should return a 400
        result = self.client().get('/api/v1/categories/1/recipes/1',
         headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 400) 
    def test_deleting_a_recipe_that_doesnot_exist(self):
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        self.assertIn('Supper', str(res.data))
        rv = self.client().delete(
            '/api/v1/categories/1/recipes/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(rv.status_code, 204)

    def test_if_recipe_to_get_doesnot_exist(self):
        """Test if recipe to get doesnot exists already"""
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        self.assertIn('Supper', str(res.data))
        res = self.client().get(
            '/api/v1/categories/1/recipes',
            headers=dict(Authorization="Bearer " + access_token),
        )
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 404)
        self.assertEqual(
            result['message'], 'No recipes found')
    def test_if_recipe_to_edit_doesnot_exist(self):
        """Test if recipe to edit doesnot exist """
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        self.assertIn('Supper', str(res.data))
        result = self.client().post(
            '/api/v1/categories/1/recipes/',
            headers=dict(Authorization="Bearer " + access_token) )
        result = self.client().put(
            '/api/v1/categories/1/recipes/1',
            headers=dict(Authorization="Bearer " + access_token),
            data={"title":"salads", "description":"chop"})
        self.assertEqual(result.status_code, 204)
        
    def test_recipe_added_is_space(self):
        """Test API can't add a space as recipe (POST request)"""
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        recipe={"title":" "}
        res = self.client().post(
            '/api/v1/categories/1/recipes',
            headers=dict(Authorization="Bearer " + access_token),
            data=recipe)
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 422)
        self.assertEqual(
            result['message'], 'Recipe title is mostly required')
    def test_recipe_added_already_exists(self):
        """Test API can't add existing recipe (POST request)"""
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        # ensure the request has an authorization header set with the access token in it
        result = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        recipes={"title":"veggies","description":"half cook" }
        result = self.client().post(
            '/api/v1/categories/1/recipes',
            headers=dict(Authorization="Bearer " + access_token),
            data=recipes)
        result = self.client().post(
            '/api/v1/categories/1/recipes',
            headers=dict(Authorization="Bearer " + access_token),
            data=recipes)
        self.assertEqual(result.status_code, 400)
    def test_if_recipe_has_special_characters(self):
        """Test API can't add recipe title with special characters (POST request)"""
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        # ensure the request has an authorization header set with the access token in it
        result = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category) 
        recipetitle={"title":"~!@#$%^&*()_={}|\[]<>?/,;:"} 
        res = self.client().post('/api/v1/categories/1/recipes',
             headers=dict(Authorization="Bearer " + access_token), data=recipetitle)
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            result['message'],'Recipe title should not have special characters')
    def test_recipetitle_is_not_numbers(self):
        """Test if recipe title can allow numbers"""
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        # ensure the request has an authorization header set with the access token in it
        result = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category) 
        inttitle={"title":"987654"}
        res = self.client().post('/api/v1/categories/1/recipes',
             headers=dict(Authorization= "Bearer " + access_token), data=inttitle)
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            result['message'], 'Recipe title should not have numbers')
    def test_when_token_expired_or_invalid_when_getting_recipes(self):
        """Test for expired or invalid when getting recipes"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        result = self.client().get(
            '/api/v1/categories/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('Supper', str(result.data))
        res = self.client().post('/api/v1/categories/1/recipes', 
         headers=dict(Authorization="Bearer " + access_token),
         data=self.recipe)
        response = self.client().get('/api/v1/categories/1/recipes',
                                  headers=dict(Authorization='Bearer '+ 'Invalid.token'))
        self.assertEqual(response.status_code, 401)   
        self.assertIn('invalid'or 'expired', str(response.data).lower()) 
    def test_when_token_expired_or_invalid_when_posting_recipes(self):
        """Test for expired or invalid when posting recipes"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        result = self.client().get(
            '/api/v1/categories/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('Supper', str(result.data))
        response = self.client().post('/api/v1/categories/1/recipes',
                                  headers=dict(Authorization='Bearer '+ 'Invalid.token'),
                                  data=self.recipe)
        self.assertEqual(response.status_code, 401)   
        self.assertIn('invalid'or 'expired', str(response.data).lower()) 
    def test_when_token_expired_or_invalid_when_editing_recipes(self):
        """Test for expired or invalid when editing recipes"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        result = self.client().get(
            '/api/v1/categories/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('Supper', str(result.data))
        response = self.client().put('/api/v1/categories/1/recipes/1',
                                  headers=dict(Authorization='Bearer '+ 'Invalid.token'),
                                  )
        self.assertEqual(response.status_code, 401)   
        self.assertIn('invalid'or 'expired', str(response.data).lower()) 
    def test_when_token_expired_or_invalid_when_getting_recipe_by_id(self):
        """Test for expired or invalid when getting recipes by id"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        result = self.client().get(
            '/api/v1/categories/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('Supper', str(result.data))
        response = self.client().get('/api/v1/categories/1/recipes/1',
                                  headers=dict(Authorization='Bearer '+ 'Invalid.token'),
                                  )
        self.assertEqual(response.status_code, 401)   
        self.assertIn('invalid'or 'expired', str(response.data).lower()) 
    def test_when_token_expired_or_invalid_when_deleting_recipes(self):
        """Test for expired or invalid when deleting recipes"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        result = self.client().get(
            '/api/v1/categories/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('Supper', str(result.data))
        response = self.client().delete('/api/v1/categories/1/recipes/1',
                                  headers=dict(Authorization='Bearer '+ 'Invalid.token'),
                                  )
        self.assertEqual(response.status_code, 401)   
        self.assertIn('invalid'or 'expired', str(response.data).lower()) 
    def test_when_user_is_getting_arecipe_not_his(self):
        """test_when_user_is_getting_arecipe_not_his"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().get('/api/v1/categories/1/recipes',
         headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 400)
    def test_when_user_is_posting_arecipe_in_a_category_not_his(self):
        """test_when_user_is_posting_arecipe_in_a_category_not_his"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('/api/v1/categories/1/recipes',
         headers=dict(Authorization="Bearer " + access_token),data={"title":"veggies","description":"just half cook"})
        self.assertEqual(res.status_code, 400)
    def test_when_user_is_deleting_arecipe_not_his(self):
        """test_when_user_is_deleting_arecipe_not_his"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().delete('/api/v1/categories/1/recipes/1',
         headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 400)
    def test_when_user_is_editing_arecipe_not_his(self):
        """test_when_user_is_editin_arecipe_not_his"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().put('/api/v1/categories/1/recipes/1',
         headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 400)
    def test_when_user_is_getting_arecipe_by_id_not_his(self):
        """test_when_user_is_getting_arecipe_not_his_by_id"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().get('/api/v1/categories/1/recipes/1',
         headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 400)
    def test_if_recipe_edited_has_special_characters(self):
        """Test API can't put recipe title with special characters (Put request)"""
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        # ensure the request has an authorization header set with the access token in it
        result = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category) 
        title={"title":"~!@#$%^&*()_={}|\[]<>?/,;:"} 
        res = self.client().put('/api/v1/categories/1/recipes/1',
             headers=dict(Authorization="Bearer " + access_token), data=title)
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            result['message'],'Recipe title should not have special characters')
    def test_recipetitle_is_not_numbers_on_edit(self):
        """Test if recipe title can allow numbers when putting"""
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        # ensure the request has an authorization header set with the access token in it
        result = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category) 
        newtitle={"title":"987654"}
        res = self.client().put('/api/v1/categories/1/recipes/1',
             headers=dict(Authorization= "Bearer " + access_token), data=newtitle)
        self.assertEqual(res.status_code, 400)
    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()    

if __name__ == "__main__":
    unittest.main()
