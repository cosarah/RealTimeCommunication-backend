import random
from django.test import TestCase, Client
from user.models import User
import datetime
import hashlib
import hmac
import time
import json
import base64
from utils.utils_jwt import generate_jwt_token, check_jwt_token
from utils.utils_jwt import EXPIRE_IN_SECONDS, SALT, b64url_encode
from user.views import validate_age, validate_email, validate_phone, validate_name, validate_password, validate_birthday, validate_gender_type, validate_info_length, validate_info_length, validate_portrait_type
import bcrypt

class ValidateFunctionsTestCase(TestCase):


    def test_validate_age(self):
        self.assertTrue(validate_age(18))
        self.assertTrue(validate_age('19'))
        self.assertFalse(validate_age(0))
        self.assertTrue(validate_age(10.0))

    def test_validate_email(self):
        self.assertTrue(validate_email('test@example.com'))
        self.assertFalse(validate_email('testexample.com'))
        self.assertFalse(validate_email('test@example'))
    def test_validate_phone(self):
        self.assertTrue(validate_phone('12345678901'))
        self.assertFalse(validate_phone('1234567890'))
        self.assertFalse(validate_phone('1234567890a'))
    def test_validate_name(self):
        self.assertTrue(validate_name('Test_User123'))
        self.assertFalse(validate_name('Test User'))
        self.assertFalse(validate_name('Test_User123'*100))
    def test_validate_password(self):
        self.assertTrue(validate_password('password123'))
        self.assertFalse(validate_password('pa'))
        self.assertFalse(validate_password('p'*100))
    def test_validate_birthday(self):
        self.assertTrue(validate_birthday('1990-01-01'))
        self.assertFalse(validate_birthday('1990-13-01'))
        self.assertFalse(validate_birthday('1990-01-32'))
    def test_validate_gender_type(self):
        self.assertTrue(validate_gender_type(1))
        self.assertFalse(validate_gender_type('-1'))
        self.assertFalse(validate_gender_type(3))
    def test_validate_info_length(self):
        self.assertTrue(validate_info_length('This is a test introduction.'))
        self.assertFalse(validate_info_length('T'*1001))

# -*- coding: UTF-8 -*-
# Create your tests here.
class UserTestCase(TestCase):

    def setUp(self):

        self.user = User.objects.create(
            name='TestUser',
            password='password123',
            email='test@example.com',
            phone='12345678901'
        )

    def test_user_creation(self):
        """测试 User 模型对象的创建是否成功"""
        self.assertEqual(self.user.name, 'TestUser')
        self.assertTrue(self.user.password, 'password123')
        self.assertFalse(self.user.is_online)
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.phone, '12345678901')
        self.assertEqual(self.user.gender,0)


    def test_user_str(self):
        """测试 User 模型的 __str__ 方法"""
        self.assertEqual(str(self.user), 'TestUser')

    def test_user_serialize1(self):
        """测试 User 模型的 serialize 方法"""
        serialized_data = self.user.__all_info__()
        self.assertEqual(serialized_data['email'], 'test@example.com')
    
    def test_user_serialize2(self):
        """测试 User 模型的 serialize 方法"""
        serialized_data = self.user.__friend_info__()
        self.assertNotIn('email', serialized_data)

class LoginTests(TestCase):
    # Initializer
    # ! Test section
    # * Tests for login view
    def test_login_existing_user_correct_password(self):

        data = {"userName": "Ashitemaru", "password": "123456"}
        res = self.client.post('/register', data=data, content_type='application/json')
        res = self.client.post('/login', data=data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertTrue(res.json()['token'].count('.') == 2)

    def test_login_existing_user_wrong_password(self):

        right_data = {"userName": "Ashitemaru", "password": "rightpassword"}
        wrong_data = {"userName": "Ashitemaru", "password": "wrongpassword"}
        res = self.client.post('/register', data=right_data, content_type='application/json')
        res = self.client.post('/login', data=wrong_data, content_type='application/json')
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 2)
        self.assertEqual(res.json()['info'], 'Wrong password')

    def test_login_unregistered_user(self):

        data = {"userName": "NewUser", "password": "123456"}
        res = self.client.post('/login', data=data, content_type='application/json')
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()['code'], -5)
        self.assertEqual(res.json()['info'], 'User not found')
        self.assertFalse(User.objects.filter(name="NewUser").exists())

    def test_login_with_bad_method(self):

        data = {"userName": "Ashitemaru", "password": "123456"}
        res = self.client.get('/login', data=data, content_type='application/json')
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')

class RegisterTests(TestCase):
    # Initializer
    # ! Test section
    # * Tests for register view
    def setUp(self):
        self.data = {"userName": "Ashitemaru", "password": "123456"}

    def test_register_with_bad_method(self):

        res = self.client.get('/register', data=self.data, content_type='application/json')
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')

    def test_register_existing_user(self):

        res = self.client.post('/register', data=self.data, content_type='application/json')
        res = self.client.post('/register', data=self.data, content_type='application/json')
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.json()['code'], -7)
        self.assertEqual(res.json()['info'], 'Already exist')   

class InfoTests(TestCase):
    # Initializer
    # ! Test section
    # * Tests for info view    
    def setUp(self):
        self.data = {"userName": "Ashitemaru", "password": "123456"}
        self.client.post('/register', data=self.data, content_type='application/json')
        self.headers = {
            "Authorization": generate_jwt_token("Ashitemaru"),
            "Content-Type": "application/json"
        }
        self.token = generate_jwt_token("Ashitemaru")

    def test_get_info_with_bad_method(self):

        res = self.client.post('/user', data=self.data, content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')

        res = self.client.put('/user', data=self.data, content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')

        res = self.client.delete('/user', data=self.data, content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')

    
    def test_get_info(self):
        res = self.client.post('/login', data=self.data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertTrue(res.json()['token'], generate_jwt_token("Ashitemaru"))

        res = self.client.get('/user', data=self.data, content_type='application/json', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()["userName"], "Ashitemaru")

    def test_fix_info(self):
        new_data = {
            "userName": "Ashitemaru",
            "nickName": "Johnny",
            "phone": "12345678901",
            "email": "john.doe@example.com",
            "gender": "male",
            "portrait": "https://example.com/profile_picture.jpg",
            "introduction": "Hello, I'm John Doe.",
            "birthday": "1990-01-01",
            "age": 34,
            "location": "New York"
        }
        res = self.client.post('/user/fix', data=new_data, content_type='application/json', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')


        res = self.client.get('/user', data={"userName": "Ashitemaru"}, content_type='application/json', headers=self.headers)
 
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()["userName"], "Ashitemaru")
        self.assertEqual(res.json()["nickName"], "Johnny")
        self.assertEqual(res.json()["phone"], "12345678901")
        self.assertEqual(res.json()["email"], "john.doe@example.com")
        
    def test_fix_not_exist_user(self):

        data = {"userName": "Ashitemaru", "nickName": "Ashitemaru", "phone": "12345678901", "email": "ashitemaru@gmail.com", "gender": "male", "portrait": "https://example.com/portrait.jpg", "introduction": "Ashitemaru is a cool guy", "birthday": "1990-01-01", "age": "34", "location": "Beijing"}
        res = self.client.post('/user/fix', data=data, content_type='application/json')
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], -15)
        self.assertEqual(res.json()['info'], 'Invalid or expired JWT')

    def test_fix_info_with_bad_method(self):

        data = {"userName": "Ashitemaru", "nickName": "Ashitemaru", "phone": "12345678901", "email": "ashitemaru@gmail.com", "gender": "male", "portrait": "https://example.com/portrait.jpg", "introduction": "Ashitemaru is a cool guy", "birthday": "1990-01-01", "age": "34", "location": "Beijing"}
        res = self.client.post('/register', data=data, content_type='application/json')
        res = self.client.put('/user/fix', data=data, content_type='application/json', headers=self.headers)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')

class CloseTests(TestCase):
    # Initializer
    def setUp(self):
        self.data = {"userName": "Ashitemaru", "password": "123456"}
        self.user = User.objects.create(name='Ashitemaru', password='123456')
        self.headers = {
            "Authorization": generate_jwt_token("Ashitemaru"),
            "Content-Type": "application/json"
        }

    # ! Test section
    # * Tests for close view
    def test_close_account(self):

        res = self.client.post('/user/close', data=self.data, content_type='application/json', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['info'], 'User closed')

    def test_close_account_with_bad_method(self):

        res = self.client.put('/user/close', data=self.data, content_type='application/json' , **self.headers)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')
    
    def test_close_not_exist_user(self):
        new_data = {"userName": "NewUser", "password": "123456"}
        res = self.client.post('/user/close', data=new_data, content_type='application/json', headers=self.headers)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.json()['code'], -12)
        self.assertEqual(res.json()['info'], 'Permission denied')



class LogoutTests(TestCase):
    def setUp(self):
        self.data = {"userName": "Ashitemaru", "password": "123456"}
        self.client.post('/register', data=self.data, content_type='application/json')
        self.headers = {
            "Authorization": generate_jwt_token("Ashitemaru"),
            "Content-Type": "application/json"
        }

    def test_logout(self):
        """测试用户登出"""
        res = self.client.post('/login', data=self.data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertTrue(res.json()['token'].count('.') == 2)
        res = self.client.post('/logout', data=self.data, content_type='application/json', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['info'], 'Logout succeed')

    def test_logout_with_bad_method(self):
        """测试用户登出时使用错误的 HTTP 方法"""

        res = self.client.get('/logout', data=self.data, content_type='application/json', headers=self.headers)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')

    def test_logout_not_exist_user(self):
        """测试不存在的用户登出"""

        new_data = {"userName": "NewUser", "password": "123456"}
        res = self.client.post('/logout', data=new_data, content_type='application/json', headers=self.headers)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.json()['code'], -12)
        self.assertEqual(res.json()['info'], 'Permission denied')

    def test_logout_without_login(self):
        """测试未登录用户登出"""

        res = self.client.post('/logout', data=self.data, content_type='application/json', headers=self.headers)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], 'User not logged in')

class FixUserPasswordTests(TestCase):
    def setUp(self):
        self.data = {"userName": "Ashitemaru", "oldPassword": "123456", "newPassword":"123456789"}
        self.client.post('/register', data={"userName": "Ashitemaru", "password": "123456"}, content_type='application/json')
        self.headers = {
            "Authorization": generate_jwt_token("Ashitemaru"),
            "Content-Type": "application/json"
        }

    def test_fix_user_password(self):
        """测试修改用户密码"""
        res = self.client.post('/user/fix/password', data=self.data, content_type='application/json', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['info'], 'Succeed')

        self.assertEqual(res.json()['code'], 0)
        self.assertTrue(bcrypt.checkpw(self.data["newPassword"].encode('utf-8'), User.objects.get(name='Ashitemaru').password.encode('utf-8')))

    def test_fix_user_password_with_bad_method(self):
        """测试修改用户密码时使用错误的 HTTP 方法"""

        res = self.client.get('/user/fix/password', data=self.data, content_type='application/json', headers=self.headers)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')

    def test_fix_user_password_not_exist_user(self):
        """测试不存在的用户修改密码"""

        new_data = self.data.copy()
        new_data["userName"] = "NewUser"
        res = self.client.post('/user/fix/password', data=new_data, content_type='application/json', headers=self.headers)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.json()['code'], -12)
        self.assertEqual(res.json()['info'], 'Permission denied')
