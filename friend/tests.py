from django.test import TestCase
from user.models import User
from friend.models import Friendship

# Create your tests here.
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
        info = self.friendship.friend_profile()
        self.assertEqual(info['toUser'], 'User2')
        self.assertEqual(info['remark'], 'Best friends')