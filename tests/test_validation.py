import unittest
from flask import json
from app.models import User, Category, Recipe
from app import create_app, db

class TestValidation(unittest.TestCase):
    """ Base class for all testing validition """
    valid_category = {
        'name': 'The name',
    }
    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        with self.app.app_context():
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

    def create_valid_category(self):
        """ Creates a valid category to be used for tests """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        response = self.client().post('/api/v1/categories/',
                                    data=json.dumps(self.valid_category),
                                    content_type='application/json',
                                    headers=dict(Authorization="Bearer " + access_token))
        return response
    def test_create_category_with_valid_details(self):
        """ Tests adding a category with valid details """
        response = self.create_valid_category()
        self.assertEqual(response.status_code, 201)
