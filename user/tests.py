import random
from django.test import TestCase, Client
from user.models import User
import datetime
import hashlib
import hmac
import time
import json
import base64

from utils.utils_jwt import EXPIRE_IN_SECONDS, SALT, b64url_encode

# -*- coding: UTF-8 -*-
# Create your tests here.
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
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], 'User not exist')
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
    def test_register_with_bad_method(self):

        data = {"userName": "Ashitemaru", "password": "123456"}
        res = self.client.get('/register', data=data, content_type='application/json')
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')

    def test_register_existing_user(self):

        data = {"userName": "Ashitemaru", "password": "123456"}
        res = self.client.post('/register', data=data, content_type='application/json')
        res = self.client.post('/register', data=data, content_type='application/json')
        self.assertEqual(res.status_code, 409)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], 'User already exists')   

class InfoTests(TestCase):
    # Initializer
    # ! Test section
    # * Tests for info view    
    def test_get_info_with_bad_method(self):

        data = {"userName": "Ashitemaru", "password": "123456"}
        res = self.client.post('/register', data=data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        res = self.client.get('/user', data=data, content_type='application/json')
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')

        res = self.client.put('/user', data=data, content_type='application/json')
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')

        res = self.client.delete('/user', data=data, content_type='application/json')
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')

    
    def test_get_info(self):

        data = {"userName": "Ashitemaru", "password": "123456"}
        res = self.client.post('/register', data=data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        res = self.client.post('/user', data=data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()["userName"], "Ashitemaru")

    def test_fix_info(self):

        data = {"userName": "Ashitemaru", "password": "123456", "nickName": "Ashitemaru", "phone": "12345678901", "email": "ashitemaru@gmail.com", "gender": "male", "portrait": "https://example.com/portrait.jpg", "introduction": "Ashitemaru is a cool guy", "birthday": "1990-01-01", "age": "34", "location": "Beijing"}
        res = self.client.post('/register', data=data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')
        
        res = self.client.post('/user/fix', data=data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

        res = self.client.post('/user', data=data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')
        self.assertEqual(res.json()["userName"], "Ashitemaru")
        self.assertEqual(res.json()["nickName"], "Ashitemaru")
        self.assertEqual(res.json()["phone"], "12345678901")
        self.assertEqual(res.json()["email"], "ashitemaru@gmail.com")
        
    def test_fix_not_exist_user(self):

        data = {"userName": "Ashitemaru", "nickName": "Ashitemaru", "phone": "12345678901", "email": "ashitemaru@gmail.com", "gender": "male", "portrait": "https://example.com/portrait.jpg", "introduction": "Ashitemaru is a cool guy", "birthday": "1990-01-01", "age": "34", "location": "Beijing"}
        res = self.client.post('/user/fix', data=data, content_type='application/json')
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], 'User not exist')

    def test_fix_info_with_bad_method(self):

        data = {"userName": "Ashitemaru", "nickName": "Ashitemaru", "phone": "12345678901", "email": "ashitemaru@gmail.com", "gender": "male", "portrait": "https://example.com/portrait.jpg", "introduction": "Ashitemaru is a cool guy", "birthday": "1990-01-01", "age": "34", "location": "Beijing"}
        res = self.client.post('/register', data=data, content_type='application/json')
        res = self.client.put('/user/fix', data=data, content_type='application/json')
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')

class CloseTests(TestCase):
    # Initializer
    # ! Test section
    # * Tests for close view
    def test_close_account(self):

        data = {"userName": "Ashitemaru", "password": "123456"}
        res = self.client.post('/register', data=data, content_type='application/json')
        res = self.client.post('/login', data=data, content_type='application/json')
        res = self.client.post('/user/close', data=data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['info'], 'User closed')

    def test_close_account_with_bad_method(self):

        data = {"userName": "Ashitemaru", "password": "123456"}
        res = self.client.post('/register', data=data, content_type='application/json')
        res = self.client.put('/user/close', data=data, content_type='application/json')
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.json()['info'], 'Bad method')
    
    def test_close_not_exist_user(self):

        data = {"userName": "Ashi", "password": "123456"}
        res = self.client.post('/user/close', data=data, content_type='application/json')
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], 'User not exist')


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

    def test_user_str(self):
        """测试 User 模型的 __str__ 方法"""
        self.assertEqual(str(self.user), 'TestUser')

    def test_user_serialize(self):
        """测试 User 模型的 serialize 方法"""
        serialized_data = self.user.serialize()
        self.assertEqual(serialized_data['email'], 'test@example.com')