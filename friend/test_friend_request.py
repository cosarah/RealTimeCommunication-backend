import json
from django.test import TestCase
from user.models import User
from friend.models import Friendship, FriendRequest, UserTag
from django.utils import timezone

class FriendRequestListTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(name='user1', password='password')
        self.user2 = User.objects.create(name='user2', password='password')
        self.user3 = User.objects.create(name='user3', password='password')
        self.user4 = User.objects.create(name='user4', password='password')
        self.request1 = FriendRequest.objects.create(from_user=self.user1, to_user=self.user2)
        self.request2 = FriendRequest.objects.create(from_user=self.user2, to_user=self.user1)
        self.request3 = FriendRequest.objects.create(from_user=self.user1, to_user=self.user3)
        self.request4 = FriendRequest.objects.create(from_user=self.user4, to_user=self.user1)
    def test_get_friend_request_list(self):
        response = self.client.get('/friend/request/',{'userName': self.user1.name})
        return_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        applys = [name['userName'] for name in return_data['applys']]
        requests = [name['userName'] for name in return_data['requests']]
        self.assertEqual(len(applys), 2)
        self.assertEqual(len(requests), 2)
        self.assertIn(self.user2.name, applys)
        self.assertIn(self.user2.name, requests)
        self.assertIn(self.user3.name, applys)
        self.assertIn(self.user4.name, requests)
        
    def test_get_friend_request_list_with_bad_method(self):
        response = self.client.post('/friend/request/',{'userName': self.user1.name})
        self.assertEqual(response.status_code, 405)
        
    def test_get_friend_request_list_with_no_user(self):
        response = self.client.get('/friend/request/',{'userName': 'no_user'})
        self.assertEqual(response.status_code, 404)
        self.assertIn('User not found', json.loads(response.content)['info'])
    
