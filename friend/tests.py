from django.test import TestCase
from user.models import User
from friend.models import Friendship, FriendRequest, FriendRequestMessage, UserTag
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

class FriendRequestMessageTestCase(TestCase):
    def setUp(self):
        # Create two users
        self.user1 = User.objects.create(name='user1', password='12345')
        self.user2 = User.objects.create(name='user2', password='12345')
        # Create a friend request from user1 to user2
        self.friend_request = FriendRequest.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            updated_message="Let's be friends!",
        )
        # Create a friend request message from user1 to user2
        self.friend_request_message = FriendRequestMessage.objects.create(
            request=self.friend_request,
            message="Hey, let's be friends!"
        )

    def test_create_friend_request_message(self):
        # Test if the friend request message was created successfully
        self.assertTrue(FriendRequest.objects.filter(from_user=self.user1, to_user=self.user2).exists())
        self.assertTrue(FriendRequestMessage.objects.filter(request=self.friend_request).exists())
        self.assertEqual(self.friend_request_message.message, "Hey, let's be friends!")

class UserTagTestCase(TestCase):
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
        # Create a user tag for user1
        self.user_tag = UserTag.objects.create(
            user=self.user1,
            name='friend',
        )
        self.user_tag.friendships.set([self.friendship])

    def test_create_user_tag(self):
        # Test if the user tag was created successfully
        self.assertTrue(UserTag.objects.filter(user=self.user1, name='friend').exists())
        self.assertEqual(self.user_tag.user, self.user1)
        self.assertEqual(self.user_tag.name, 'friend')
        self.assertEqual(list(self.user_tag.friendships.all()), [self.friendship])


    def test_delete_user_tag(self):
        # Delete the user tag
        self.user_tag.delete()
        # Test if the user tag was deleted successfully
        self.assertFalse(UserTag.objects.filter(user=self.user1, name='friend').exists())
        self.assertTrue(Friendship.objects.filter(from_user=self.user1, to_user=self.user2).exists())
        self.assertEqual(Friendship.objects.get(from_user=self.user1, to_user=self.user2).tags.all().count(), 0)
