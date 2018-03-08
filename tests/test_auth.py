
import unittest
import json
from app import create_app, db
from app.models import User, RevokedToken

class AuthTestCase(unittest.TestCase):
    """Test case for the authentication blueprint."""
    def setUp(self):
        """Set up test variables."""
        self.app = create_app(config_name="testing")
        # initialize the test client
        self.client = self.app.test_client
        # This is the user test json data with a predefined email and password
        self.user_data = {
            'email': 'test@example.com',
            'password': 'test_password'
        }
        with self.app.app_context():
            # create all tables
            db.session.close()
            db.drop_all()
            db.create_all()
    def test_registration(self):
        """Test user registration works correcty."""
        res = self.client().post('/api/v1/auth/register',data=self.user_data)
        result = json.loads(res.data.decode())
        self.assertEqual(
            result['message'], "You registered successfully. Please login.")
        self.assertEqual(res.status_code, 201)
        
    def test_registration_with_no_password(self):
        """Test user registration with no password."""
        half_data={"email":"example@gmail.com","password":""}
        res = self.client().post('/api/v1/auth/register',data=half_data)
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 401)

    def test_already_registered_user(self):
        """Test that a user cannot be registered twice."""
        res = self.client().post('/api/v1/auth/register',data=self.user_data)
        second_res = self.client().post('/api/v1/auth/register',
        data=self.user_data)
        self.assertEqual(second_res.status_code, 409)
        # get the results returned in json format
        result = json.loads(second_res.data.decode())
        self.assertEqual(
            result['message'], "User already exists. Please login.")

    def test_user_login(self):
        """Test registered user can login."""
        res = self.client().post('/api/v1/auth/register',data=self.user_data)
        login_res = self.client().post('/api/v1/auth/login',
        data=self.user_data)
        # get the results in json format
        result = json.loads(login_res.data.decode())
        # Test that the response contains success message
        self.assertEqual(result['message'], "You logged in successfully.")
        # Assert that the status code is equal to 200
        self.assertEqual(login_res.status_code, 200)
        self.assertTrue(result['access_token'])

    def test_non_registered_user_login(self):
        """Test non registered users cannot login."""
        # define a dictionary to represent an unregistered user
        not_a_user = {
            'email': 'not_a_user@example.com',
            'password': 'nope'
        }
        # send a POST request to /auth/login with the data above
        res = self.client().post('/api/v1/auth/login',data=not_a_user)
        result = json.loads(res.data.decode())
        # and an error status code 401(Unauthorized)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(
            result['message'], "Invalid email or password, Please try again")

    def test_user_registers_with_valid_email(self):
        """Test for invalid email and password on registration"""
        user1 = {
            "email": "hadijah", "password": "1234567"
        }
        res = self.client().post('/api/v1/auth/register',data=user1)
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
        result['message'], 'Invalid email format')

    def test_user_registers_with_valid_password(self):
        """Test for short password on registration"""
        user2 = {
            "email": "hadijah@gmail.com", "password": "123"
        }
        res = self.client().post('/api/v1/auth/register',data=user2)
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
        result['message'], ' Ensure password is morethan 6 characters')

    def test_user_logout(self):
        """ Test a user can logout from the session"""
        res = self.client().post('/api/v1/auth/register', 
        data=self.user_data)
        login_res = self.client().post('/api/v1/auth/login', 
        data=self.user_data)
        result = json.loads(login_res.data.decode())
        access_token = result['access_token']
        res1 = self.client().post('/api/v1/auth/logout', headers=dict(
            Authorization="Bearer " + access_token))
        data = json.loads(res1.data.decode())
        self.assertTrue(data['message'] == 'Your have been logged out.')
        self.assertEqual(res.status_code, 201)

    def test_when_token_expired_or_invalid(self):
        """Test for expired or invalid"""
        response = self.client().post('/api/v1/categories/',
            headers=dict(Authorization='Bearer ' + 'Invalid.token'))
        self.assertEqual(response.status_code, 401)
        self.assertIn('invalid'or 'expired', str(response.data).lower())


    def test_new_password_length_is_morethan_6(self):
        """Test for the length of new password"""
        res = self.client().put('/api/v1/auth/register', 
                            data=self.user_data)
        new_data = {'email': 'test@example.com',
                    'password': 'test_password', 'retyped_password': '123'}
        res = self.client().post('/api/v1/auth/reset_password', data=new_data)
        self.assertEqual(res.status_code, 405)
    
