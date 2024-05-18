import json
from django.test import TestCase
from user.models import User
from friend.models import Friendship
from utils.utils_jwt import generate_jwt_token

class FriendDeleteTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create(name='test1', password='password')
        self.user2 = User.objects.create(name='test2', password='password')
        self.friendship1 = Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        self.friendship2 = Friendship.objects.create(from_user=self.user2, to_user=self.user1)
        self.data = {'userName':self.user1.name,'friendName': self.user2.name, 'message':'message1' }
        self.headers = {
            "Authorization": generate_jwt_token(self.user1.name),
            "Content-Type": "application/json"
        }
        self.token=generate_jwt_token(self.user1.name)

    def test_delete_friend(self):
        response = self.client.post('/friend/delete/',data=self.data, content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Friendship.objects.filter(from_user=self.user1, to_user=self.user2).count(), 0)
        self.assertEqual(Friendship.objects.filter(from_user=self.user2, to_user=self.user1).count(), 0)
        
class UserSearchTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create(name='test1', password='password',phone='1234567890',email='xcuin@gmail.com')
        self.user2 = User.objects.create(name='test2', password='password',phone='428967890',email='xvefsin@gmail.com')
        self.user3 = User.objects.create(name='test3', password='password',phone='4264537890',email='xhtr42in@gmail.com')
        friendship1 = Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        friendship2 = Friendship.objects.create(from_user=self.user2, to_user=self.user1)
        self.data1 = {'userName':self.user1.name, 'keyword': 'test2', 'info':'name'}
        self.data2 = {'userName':self.user1.name, 'keyword': 'test3', 'info':'name'}
        self.headers = {
            "Authorization": generate_jwt_token(self.user1.name),
            "Content-Type": "application/json"
        }
        self.token=generate_jwt_token(self.user1.name)

    def test_search_user(self):
        response1 = self.client.get('/friend/search/',data=self.data1, content_type='application/json', HTTP_AUTHORIZATION=self.token)
        response2 = self.client.get('/friend/search/',data=self.data2, content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(json.loads(response1.content)['isFriend'], 1)
        self.assertEqual(json.loads(response2.content)['isFriend'], 0)

    def test_search_user_not_exist(self):
        data = {'userName':self.user1.name, 'keyword': 'test4', 'info':'name'}
        response = self.client.get('/friend/search/',data=data, content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content)['info'], 'User not found')
        self.assertEqual(json.loads(response.content)['code'], -5)

    def test_search_user_unknown_info(self):
        data = {'userName':self.user1.name, 'keyword': 'test2', 'info':'phoneing'}

        response = self.client.get('/friend/search/',data=data, content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 403)

        self.assertEqual(json.loads(response.content)['info'], 'Unknown info type')
        self.assertEqual(json.loads(response.content)['code'], 1)