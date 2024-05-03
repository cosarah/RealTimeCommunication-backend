from django.test import TestCase
from user.models import User
from friend.models import Friendship, FriendRequest
from django.utils import timezone


class FriendRequestTestCase(TestCase):
    def setUp(self):
        # Create two users
        self.user1 = User.objects.create(name='user1', password='12345')
        self.user2 = User.objects.create(name='user2', password='12345')
        # Create a friend request from user1 to user2
        self.friend_request = FriendRequest.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            updated_time=timezone.now(),
            updated_message="Let's be friends!",
        )


    def test_create_friend_request(self):
        # Test if the friend request was created successfully
        self.assertTrue(FriendRequest.objects.filter(from_user=self.user1, to_user=self.user2).exists())
        self.assertEqual(self.friend_request.status, 0)
        self.assertEqual(self.friend_request.updated_message, "Let's be friends!")

    def test_accept_friend_request(self):
        # Accept the friend request
        self.assertTrue(self.friend_request.accept())
        # Test if the friendship has been created
        self.assertTrue(Friendship.objects.filter(from_user=self.user1, to_user=self.user2).exists())
        self.assertTrue(Friendship.objects.filter(from_user=self.user2, to_user=self.user1).exists())
        # Test if the friend request status is now 'Accepted'
        self.assertEqual(self.friend_request.status, 1)

    def test_reject_friend_request(self):
        # Reject the friend request
        self.assertTrue(self.friend_request.reject())
        # Test if the friend request status is now 'Declined'
        self.assertEqual(self.friend_request.status, 2)

    def test_double_accept_friend_request(self):
        # Accept the friend request
        self.friend_request.accept()
        # Try to accept it again
        self.assertFalse(self.friend_request.accept())

    def test_double_reject_friend_request(self):
        # Reject the friend request
        self.friend_request.reject()
        # Try to reject it again
        self.assertFalse(self.friend_request.reject())

    def test_accept_friend_request_after_reject(self):
        # Reject the friend request
        self.assertTrue(self.friend_request.reject())
        # Try to accept it again
        self.assertTrue(self.friend_request.accept())

class FriendshipTestCase(TestCase):
    def setUp(self):
        # Create two users
        self.user1 = User.objects.create(name='user1', password='12345')
        self.user2 = User.objects.create(name='user2', password='12345')
        # Create a friendship between user1 and user2
        self.friendship = Friendship.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            created_time=timezone.now(),
        )

    def test_create_friendship(self):
        # Test if the friendship was created successfully
        self.assertTrue(Friendship.objects.filter(from_user=self.user1, to_user=self.user2).exists())
        self.assertFalse(Friendship.objects.filter(from_user=self.user2, to_user=self.user1).exists())
        time = timezone.now()
        self.assertAlmostEqual(self.friendship.created_time, time, delta=timezone.timedelta(seconds=1))
        self.assertIsNone(self.friendship.alias)
