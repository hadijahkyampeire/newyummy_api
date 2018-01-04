
import unittest
import json
from app import create_app, db
from app.models import User

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

    def test_already_registered_user(self):
        """Test that a user cannot be registered twice."""
        res = self.client().post('/api/v1/auth/register',data=self.user_data)
        self.assertEqual(res.status_code, 201)
        second_res = self.client().post('/api/v1/auth/register',
        data=self.user_data)
        self.assertEqual(second_res.status_code, 202)
        # get the results returned in json format
        result = json.loads(second_res.data.decode())
        self.assertEqual(
            result['message'], "User already exists. Please login.")

    def test_user_login(self):
        """Test registered user can login."""
        res = self.client().post('/api/v1/auth/register',data=self.user_data)
        self.assertEqual(res.status_code, 201)
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
        user = {
            "email": "hadijah", "password": "123"
        }
        res = self.client().post('/api/v1/auth/register',data=user)
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
        result['message'], 'Invalid email or password, Please try again')

    def test_password_reset(self):
        """Test API for password reset (Post request)"""
        res = self.client().post('/api/v1/auth/register',
                                 data=self.user_data)
        self.assertEqual(res.status_code, 201)
        login_res = self.client().post('/api/v1/auth/login',
                                       data=self.user_data)
        self.assertEqual(login_res.status_code, 200)
        result = json.loads(login_res.data.decode())
        access_token = result['access_token']
        new_data = {'email': 'test@example.com',
                'password': 'test_password', 'new_password': 'test12345'}
        res = self.client().post('/api/v1/auth/reset_password',headers=
         dict(Authorization="Bearer " + access_token), data=new_data)
        self.assertEqual(res.status_code, 200)
        result = json.loads(res.data.decode())
        self.assertEqual(result['message'], "Your password has been reset.")

    def test_user_logout(self):
        """ Test a user can logout from the session"""
        res = self.client().post('/api/v1/auth/register', 
        data=self.user_data)
        self.assertEqual(res.status_code, 201)
        login_res = self.client().post('/api/v1/auth/login', 
        data=self.user_data)
        self.assertEqual(login_res.status_code, 200)
        result = json.loads(login_res.data.decode())
        access_token = result['access_token']
        res = self.client().post('/api/v1/auth/logout', headers=dict(
            Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data.decode())
        self.assertTrue(data['message'] == 'Your have been logged out.')

    def test_when_token_expired_or_invalid(self):
        """Test for expired or invalid"""
        response = self.client().post('/api/v1/categories/',
            headers=dict(Authorization='Bearer ' + 'Invalid.token'))
        self.assertEqual(response.status_code, 401)
        self.assertIn('invalid'or 'expired', str(response.data).lower())

    def test_if_the_user_is_registered_on_reset_password(self):
        """Test if user is registered before reset password"""
        firstuser = {"email": " kyampeire@gmail.com", "password": "12234567"}
        res = self.client().post('/api/v1/auth/register', data=firstuser)
        self.assertEqual(res.status_code, 201)
        login_res = self.client().post('/api/v1/auth/login', data=firstuser)
        self.assertEqual(login_res.status_code, 200)
        result = json.loads(login_res.data.decode())
        access_token = result['access_token']
        user_data = {"email": " hadijah@gmail.com",
                     "password": "7890654", "new_password": "8765432"}
        res = self.client().post('/api/v1/auth/reset_password', headers=dict(
            Authorization="Bearer " + access_token), data=user_data)
        self.assertEqual(res.status_code, 401)

    def test_new_password_length_is_morethan_6(self):
        """Test for the length of new password"""
        res = self.client().post('/api/v1/auth/register', 
        data=self.user_data)
        self.assertEqual(res.status_code, 201)
        login_res = self.client().post('/api/v1/auth/login',
         data=self.user_data)
        self.assertEqual(login_res.status_code, 200)
        result = json.loads(login_res.data.decode())
        access_token = result['access_token']
        new_data = {'email': 'test@example.com',
                    'password': 'test_password', 'new_password': '123'}
        res = self.client().post('/api/v1/auth/reset_password',
        headers=dict(Authorization="Bearer " + access_token), data=new_data)
        self.assertEqual(res.status_code, 400)
        result = json.loads(res.data.decode())
        self.assertEqual(result['message'],
             "Password needs to be more than 6 characters")
