import json
from django.test import TestCase
from user.models import User
from friend.models import Friendship, FriendRequest, FriendRequestMessage
from utils.utils_jwt import generate_jwt_token

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
        self.headers = {
            "Authorization": generate_jwt_token(self.user1.name),
            "Content-Type": "application/json"
        }
    def test_get_friend_request_list(self):
        response = self.client.get('/friend/request/',{'userName': self.user1.name}, headers=self.headers)
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
        response = self.client.post('/friend/request/',{'userName': self.user1.name}, headers=self.headers)
        self.assertEqual(response.status_code, 405)
        
    def test_get_friend_request_list_with_no_user(self):
        response = self.client.get('/friend/request/',{'userName': 'no_user'}, headers=self.headers)
        self.assertEqual(response.status_code, 403)
    
class FriendRequestCreateTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(name='user1', password='password')
        self.user2 = User.objects.create(name='user2', password='password')
        self.data = {'userName':self.user1.name,'friendName': self.user2.name, 'message':'message1' }
        self.headers = {
            "Authorization": generate_jwt_token(self.user1.name),
            "Content-Type": "application/json"
        }
    def test_create_friend_request(self):
        response = self.client.post('/friend/add/',data=self.data, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FriendRequest.objects.filter(from_user=self.user1, to_user=self.user2).count(), 1)
        self.assertEqual(FriendRequest.objects.filter(from_user=self.user2, to_user=self.user1).count(), 0)
        self.assertEqual(FriendRequest.objects.get(from_user=self.user1, to_user=self.user2).updated_message, 'message1')
        self.assertEqual(FriendRequest.objects.get(from_user=self.user1, to_user=self.user2).status, 0)

        new_data = self.data.copy()
        new_data['message'] = 'new message'
        response = self.client.post('/friend/add/',data=new_data, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FriendRequest.objects.filter(from_user=self.user1, to_user=self.user2).count(), 1)
        self.assertEqual(FriendRequest.objects.filter(from_user=self.user2, to_user=self.user1).count(), 0)
        friend_request = FriendRequest.objects.get(from_user=self.user1, to_user=self.user2)
        self.assertEqual(FriendRequestMessage.objects.filter(request=friend_request).count(), 2)
        self.assertEqual(FriendRequest.objects.get(from_user=self.user1, to_user=self.user2).updated_message, 'new message')
        self.assertEqual(FriendRequest.objects.get(from_user=self.user1, to_user=self.user2).status, 0)
        
    def test_create_friend_request_with_bad_method(self):
        response = self.client.get('/friend/add/', data=self.data, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 405)
        
    def test_create_friend_request_with_no_user(self):
        data = self.data.copy()
        data['userName'] = 'no_user'
        response = self.client.post('/friend/add/', data=data, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 403)
        
    def test_create_friend_request_with_already_friend(self):
        new_data = self.data.copy()
        new_user = User.objects.create(name='new_user', password='password')
        Friendship.objects.create(from_user=self.user1, to_user=new_user)
        Friendship.objects.create(from_user=new_user, to_user=self.user1)
        new_data['friendName'] = 'new_user'
        response = self.client.post('/friend/add/', data=new_data, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content)['info'], 'Already exist')
        self.assertEqual(json.loads(response.content)['code'], -7)
        
    def test_create_friend_request_with_already_get_request(self):
        FriendRequest.objects.create(from_user=self.user2, to_user=self.user1)
        response = self.client.post('/friend/add/', data=self.data, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 403)

        self.assertEqual(json.loads(response.content)['info'], 'Please go to accept friend request')
        self.assertEqual(json.loads(response.content)['code'], 1)
        
class FriendRequestAcceptTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(name='user1', password='password')
        self.user2 = User.objects.create(name='user2', password='password')
        self.request = FriendRequest.objects.create(from_user=self.user1, to_user=self.user2)
        self.data = {'userName':self.user2.name,'friendName': self.user1.name }
        self.headers = {
            "Authorization": generate_jwt_token(self.user2.name),
            "Content-Type": "application/json"
        }
    def test_accept_friend_request(self):
        response = self.client.post('/friend/accept/', data=self.data, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FriendRequest.objects.filter(from_user=self.user1, to_user=self.user2).count(), 1)
        self.assertEqual(Friendship.objects.filter(from_user=self.user1, to_user=self.user2).count(), 1)
        self.assertEqual(Friendship.objects.filter(from_user=self.user2, to_user=self.user1).count(), 1)
        self.assertEqual(FriendRequest.objects.get(from_user=self.user1, to_user=self.user2).status, 1)
        
    def test_accept_friend_request_with_bad_method(self):
        response = self.client.get('/friend/accept/', data=self.data, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 405)
        
    def test_accept_friend_request_with_no_user(self):
        data = self.data.copy()
        data['userName'] = 'no_user'
        response = self.client.post('/friend/accept/', data=data, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 403)

    def test_accept_friend_request_with_no_request(self):
        User.objects.create(name='no_request', password='password')
        new_data = self.data.copy()
        new_data['friendName'] = 'no_request'
        response = self.client.post('/friend/accept/', data=new_data, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content)['info'], 'Friend request not found')
        self.assertEqual(json.loads(response.content)['code'], 2)

    def test_accept_friend_request_with_already_accepted(self):
        self.request.status = 1
        response = self.client.post('/friend/accept/', data=self.data, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FriendRequest.objects.filter(from_user=self.user1, to_user=self.user2).count(), 1)
        self.assertEqual(Friendship.objects.filter(from_user=self.user1, to_user=self.user2).count(), 1)
        self.assertEqual(Friendship.objects.filter(from_user=self.user2, to_user=self.user1).count(), 1)
        self.assertEqual(FriendRequest.objects.get(from_user=self.user1, to_user=self.user2).status, 1)

    def test_accept_friend_request_with_denied_request(self):
        self.request.status = 2
        response = self.client.post('/friend/accept/', data=self.data, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FriendRequest.objects.filter(from_user=self.user1, to_user=self.user2).count(), 1)
        self.assertEqual(Friendship.objects.filter(from_user=self.user1, to_user=self.user2).count(), 1)
        self.assertEqual(Friendship.objects.filter(from_user=self.user2, to_user=self.user1).count(), 1)
        self.assertEqual(FriendRequest.objects.get(from_user=self.user1, to_user=self.user2).status, 1)

class FriendRequestRejectTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(name='user1', password='password')
        self.user2 = User.objects.create(name='user2', password='password')
        self.request = FriendRequest.objects.create(from_user=self.user1, to_user=self.user2)
        self.data = {'userName':self.user2.name,'friendName': self.user1.name }
        self.headers = {
            "Authorization": generate_jwt_token(self.user2.name),
            "Content-Type": "application/json"
        }
    def test_reject_friend_request(self):
        response = self.client.post('/friend/reject/', data=self.data, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FriendRequest.objects.get(from_user=self.user1, to_user=self.user2).status, 2)

    def test_reject_friend_request_with_bad_method(self):
        response = self.client.get('/friend/reject/', data=self.data, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 405)

    def test_reject_friend_request_with_no_user(self):
        data = self.data.copy()
        data['userName'] = 'no_user'
        response = self.client.post('/friend/reject/', data=data, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content)['info'], 'Permission denied')
        self.assertEqual(json.loads(response.content)['code'], -12)

    def test_reject_friend_request_with_no_request(self):
        User.objects.create(name='no_request', password='password')
        new_data = self.data.copy()
        new_data['friendName'] = 'no_request'
        response = self.client.post('/friend/reject/', data=new_data, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content)['info'], 'Friend request not found')
        self.assertEqual(json.loads(response.content)['code'], 2)
    
    def test_reject_friend_request_with_already_accepted(self):
        self.request.status = 1
        self.request.save()
        response = self.client.post('/friend/reject/', data=self.data, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(FriendRequest.objects.get(from_user=self.user1, to_user=self.user2).status, 1)
        self.assertEqual(json.loads(response.content)['info'], 'Friend request already accepted or rejected')
        self.assertEqual(json.loads(response.content)['code'], 1)

        self.request.status = 0
        self.request.save()

    def test_reject_friend_request_with_already_rejected(self):
        self.request.status = 2
        self.request.save()
        response = self.client.post('/friend/reject/', data=self.data, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(FriendRequest.objects.get(from_user=self.user1, to_user=self.user2).status, 2)
        self.assertEqual(json.loads(response.content)['info'], 'Friend request already accepted or rejected')
        self.assertEqual(json.loads(response.content)['code'], 1)

        self.request.status = 0
        self.request.save()