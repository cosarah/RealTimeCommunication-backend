import json
from django.test import TestCase
from user.models import User
from friend.models import Friendship
from conversation.models import PrivateConversation, PrivateMessage, UserPrivateConversation
from utils.utils_jwt import generate_jwt_token

class PrivateConversationCreateTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(name='user1', password='password')
        self.user2 = User.objects.create(name='user2', password='password')
        self.friendship1 = Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        self.friendship2 = Friendship.objects.create(from_user=self.user2, to_user=self.user1)
        self.headers = {
            "Authorization": generate_jwt_token(self.user1.name),
            "Content-Type": "application/json"
        }


    def test_create_private_conversation(self):
        private_conversation = PrivateConversation.objects.create(
            user1=self.user1,
            user2=self.user2
        )
        self.assertIsInstance(private_conversation, PrivateConversation)
        self.assertEqual(private_conversation.user1, self.user1)
        self.assertEqual(private_conversation.user2, self.user2)
        self.assertEqual(private_conversation.messages.count(), 0)
        
        user1_private_conversation = UserPrivateConversation.objects.create(user=self.user1, friendship=self.friendship1, conversation=private_conversation)

        user2_private_conversation = UserPrivateConversation.objects.create(user=self.user2, friendship=self.friendship2, conversation=private_conversation)

        self.assertIsInstance(user1_private_conversation, UserPrivateConversation)
        self.assertIsInstance(user2_private_conversation, UserPrivateConversation)
        self.assertEqual(user1_private_conversation.user, self.user1)
        self.assertEqual(user2_private_conversation.user, self.user2)
        self.assertEqual(user1_private_conversation.conversation, private_conversation)
        self.assertEqual(user2_private_conversation.conversation, private_conversation)

        message = PrivateMessage.objects.create(
            sender=self.user1,
            conversation=private_conversation,
            text='Hello, how are you?'
        )
        self.assertIsInstance(message, PrivateMessage)
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.conversation, private_conversation)
        self.assertEqual(message.text, 'Hello, how are you?')
        self.assertEqual(private_conversation.messages.count(), 1)


class PrivateConversationSendMessageTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(name='user1', password='password')
        self.user2 = User.objects.create(name='user2', password='password')
        self.friendship1 = Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        self.friendship2 = Friendship.objects.create(from_user=self.user2, to_user=self.user1)
        self.data = {
            'userName': self.user1.name,
            'friendName': self.user2.name,
            'message': 'Hello, how are you?',
            'quote': ''
        }
        self.url = '/conversation/private/message/send'
        self.private_conversation = PrivateConversation.objects.create(
            id=1,
            user1=self.user1,
            user2=self.user2
        )
        self.headers = {
            "Authorization": generate_jwt_token(self.user1.name),
            "Content-Type": "application/json"
        }


    def test_send_message(self):
        response = self.client.post(self.url, data=self.data, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')
        self.assertEqual(json.loads(response.content)['messageId'], 1)

    def check_message(self):
        response = self.client.post(self.url, data=self.data, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')
        self.assertEqual(json.loads(response.content)['messageId'], 1)
        
        response = self.client.get('/conversation/private/message')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)