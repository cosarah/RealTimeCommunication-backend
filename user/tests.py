import random
from django.test import TestCase, Client
from user.models import User, UserProfile, Friendship, FriendRequest
import datetime
import hashlib
import hmac
import time
import json
import base64

from utils.utils_jwt import EXPIRE_IN_SECONDS, SALT, b64url_encode

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
        self.assertTrue(res.json()['token'].count('.') == 2)

    def test_login_existing_user_wrong_password(self):
        data = {"userName": "Ashitemaru", "password": "wrongpassword"}
        res = self.client.post('/login', data=data, content_type='application/json')
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 2)

    def test_login_new_user(self):
        data = {"userName": "NewUser", "password": "123456"}
        res = self.client.post('/login', data=data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
        self.assertTrue(res.json()['token'].count('.') == 2)
        self.assertTrue(User.objects.filter(name="NewUser").exists())

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

class FriendshipTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(name='User1', password='password1', email='user1@example.com')
        self.user2 = User.objects.create(name='User2', password='password2', email='user2@example.com')
        self.friendship = Friendship.objects.create(from_user=self.user1, to_user=self.user2, remark='Best friends')

    def test_friendship_creation(self):
        """测试 Friendship 对象创建"""
        self.assertEqual(self.friendship.from_user.name, 'User1')
        self.assertEqual(self.friendship.to_user.name, 'User2')

    def test_friend_info(self):
        """测试 friend_info 方法"""
        info = self.friendship.friend_info()
        self.assertEqual(info['toUser'], 'User2')
        self.assertEqual(info['remark'], 'Best friends')