import json
from django.test import TestCase
from user.models import User
from friend.models import Friendship, FriendRequest, UserTag
from django.utils import timezone

class TestGetFriendList(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(name='test1', password='123456')
        self.user2 = User.objects.create(name='test2', password='123456')
        self.user3 = User.objects.create(name='test3', password='123456')
        self.user4 = User.objects.create(name='test4', password='123456')
        self.friendship1 = Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        Friendship.objects.create(from_user=self.user2, to_user=self.user1)
        self.friendship2 = Friendship.objects.create(from_user=self.user1, to_user=self.user3)
        Friendship.objects.create(from_user=self.user3, to_user=self.user1)
        Friendship.objects.create(from_user=self.user2, to_user=self.user3)
        Friendship.objects.create(from_user=self.user3, to_user=self.user2)
        self.tag1 = UserTag.objects.create(user=self.user1, name='tag1')
        self.tag2 = UserTag.objects.create(user=self.user1, name='tag2')
    def test_get_friend_list(self):
        response = self.client.get('/friend/', {'userName': self.user1.name})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['friends']), 2)
        name_list = [friend_info['userName'] for friend_info in data['friends']]
        self.assertIn(self.user2.name, name_list)
        self.assertIn(self.user3.name, name_list)
        self.assertNotIn(self.user4.name, name_list)

    def test_get_friend_list_with_tag(self):
        
        self.friendship1.tags.set([self.tag1,self.tag2])
        self.friendship2.tags.set([self.tag1])
        response = self.client.get('/friend/tags/', {'userName': self.user1.name})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['tag1']), 2)
        self.assertEqual(len(data['tag2']), 1)
        name_list = [friend_info['userName'] for friend_info in data['tag1']]
        self.assertIn(self.user2.name, name_list)
        self.assertIn(self.user3.name, name_list)
        self.assertNotIn(self.user4.name, name_list)

