import json
from django.test import TestCase
from user.models import User
from friend.models import Friendship
from conversation.models import PrivateConversation, PrivateMessage, UserPrivateConversation
from utils.utils_jwt import generate_jwt_token

class GetPrivateConversationListTestCase(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        
        # 创建好友关系
        self.friendship = Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        
        # 创建私聊会话
        self.private_conversation = PrivateConversation.objects.create(user1=self.user1, user2=self.user2)
        
        # 创建用户与私聊会话的关联
        UserPrivateConversation.objects.create(user=self.user1, friendship=self.friendship, conversation=self.private_conversation)
        
        # 设置获取私聊会话列表的URL
        self.list_url = '/conversation/private'
        
        # 生成JWT token
        self.token = generate_jwt_token(self.user1.name)

    def test_get_private_conversation_list_success(self):
        # 测试成功获取私聊会话列表
        response = self.client.get(
            self.list_url,
            data={'userName': self.user1.name},
            HTTP_AUTHORIZATION=self.token
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['privateConversationList']), 1)
        self.assertEqual(json.loads(response.content)['privateConversationList'][0]['friendName'], 'jane_doe')

    def test_get_private_conversation_list_unauthorized(self):
        # 测试未授权用户尝试获取私聊会话列表
        invalid_token = generate_jwt_token('invalid_user')
        response = self.client.get(
            self.list_url,
            data={'userName': self.user1.name},
            HTTP_AUTHORIZATION=invalid_token
        )
        self.assertEqual(response.status_code, 403)  # 假设未授权状态码为403

    def test_get_private_conversation_list_user_not_found(self):
        # 测试不存在的用户尝试获取私聊会话列表
        response = self.client.get(
            self.list_url,
            data={'userName': 'unknown_user'},
            HTTP_AUTHORIZATION=self.token
        )
        self.assertEqual(response.status_code, 403)  # 假设用户不存在状态码为404

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
        self.token=generate_jwt_token(self.user1.name)


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
        self.token=generate_jwt_token(self.user1.name)


    def test_send_message(self):
        response = self.client.post(self.url, data=self.data, content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')
        self.assertEqual(json.loads(response.content)['messageId'], 1)

    def check_message(self):
        response = self.client.post(self.url, data=self.data, content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')
        self.assertEqual(json.loads(response.content)['messageId'], 1)
        
        response = self.client.get('/conversation/private/message')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)

class GetPrivateMessageListTestCase(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        
        # 创建好友关系
        self.friendship = Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        self.friendship2 = Friendship.objects.create(from_user=self.user2, to_user=self.user1)
        
        # 创建私聊会话
        self.private_conversation = PrivateConversation.objects.create(user1=self.user1, user2=self.user2)
        self.private_conversation2 = PrivateConversation.objects.create(user1=self.user2, user2=self.user1)
        
        # 创建用户与私聊会话的关联
        UserPrivateConversation.objects.create(
            user=self.user1, 
            friendship=self.friendship, 
            conversation=self.private_conversation
        )
        
        # 创建私聊消息
        self.message1 = PrivateMessage.objects.create(
            sender=self.user1,
            text='Hello, Jane!',
            conversation=self.private_conversation
        )
        self.message2 = PrivateMessage.objects.create(
            sender=self.user2,
            text='Hi, John!',
            conversation=self.private_conversation
        )
        
        # 设置获取私聊消息列表的URL
        self.list_url = '/conversation/private/message'
        
        # 生成JWT token
        self.token = generate_jwt_token(self.user1.name)

    def test_get_private_message_list_success(self):
        # 测试成功获取私聊消息列表
        data = {
            "userName": "john_doe",
            "friendName": "jane_doe"
        }
        response = self.client.get(
            self.list_url,
            data=data,
            HTTP_AUTHORIZATION=self.token
        )
        self.assertEqual(response.status_code, 200)

    def test_get_private_message_list_unauthorized(self):
        # 测试未授权用户尝试获取私聊消息列表
        invalid_token = generate_jwt_token('invalid_user')
        data = {
            "userName": "john_doe",
            "friendName": "jane_doe"
        }
        response = self.client.get(
            self.list_url,
            data=data,
            HTTP_AUTHORIZATION=invalid_token
        )
        self.assertEqual(response.status_code, 403)  # 假设未授权状态码为403

    def test_get_private_message_list_friendship_not_found(self):
        # 测试不存在的好友关系尝试获取私聊消息列表
        data = {
            "userName": "john_doe",
            "friendName": "unknown_user"
        }
        response = self.client.get(
            self.list_url,
            data=data,
            HTTP_AUTHORIZATION=self.token
        )
        self.assertEqual(response.status_code, 404)  # 假设好友关系不存在状态码为404


class DeletePrivateMessageTestCase(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        
        # 创建好友关系
        self.friendship = Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        self.friendship2 = Friendship.objects.create(from_user=self.user2, to_user=self.user1)
        
        # 创建私聊会话
        self.private_conversation = PrivateConversation.objects.create(user1=self.user1, user2=self.user2)
        self.private_conversation2 = PrivateConversation.objects.create(user1=self.user2, user2=self.user1)
        
        # 创建用户与私聊会话的关联
        UserPrivateConversation.objects.create(
            user=self.user1, 
            friendship=self.friendship, 
            conversation=self.private_conversation
        )
        
        # 创建私聊消息
        self.message1 = PrivateMessage.objects.create(
            sender=self.user1,
            text='Hello, Jane!',
            conversation=self.private_conversation
        )
        self.message2 = PrivateMessage.objects.create(
            sender=self.user2,
            text='Hi, John!',
            conversation=self.private_conversation
        )
        
        # 设置删除私聊消息的URL
        self.delete_url = '/conversation/private/message/delete'
        self.token = generate_jwt_token(self.user1.name)

    def test_delete_private_message_success(self):
        # 测试成功删除私聊消息
        data = {
            "userName": "john_doe",
            "friendName": "jane_doe",
            "messageId": self.message1.id
        }
        response = self.client.post(
            self.delete_url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)  # 假设成功响应的code为0
        
        # 验证消息是否已被删除
        self.assertTrue(PrivateMessage.objects.filter(id=self.message1.id).exists())

    def test_delete_private_message_unauthorized(self):
        # 测试未授权用户尝试删除私聊消息
        invalid_token = generate_jwt_token('invalid_user')
        data = {
            "userName": "john_doe",
            "friendName": "jane_doe",
            "messageId": self.message1.id
        }
        response = self.client.post(
            self.delete_url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=invalid_token
        )
        self.assertEqual(response.status_code, 403)  # 假设未授权状态码为403

    def test_delete_private_message_message_not_found(self):
        # 测试删除不存在的私聊消息
        data = {
            "userName": "john_doe",
            "friendName": "jane_doe",
            "messageId": -1  # 不存在的消息ID
        }
        response = self.client.post(
            self.delete_url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        self.assertEqual(response.status_code, 404)  # 假设消息不存在状态码为404

    def test_delete_private_message_friendship_not_found(self):
        # 测试不存在的好友关系尝试删除私聊消息
        data = {
            "userName": "john_doe",
            "friendName": "unknown_user",
            "messageId": self.message1.id
        }
        response = self.client.post(
            self.delete_url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        self.assertEqual(response.status_code, 404)  # 假设好友关系不存在状态码为404

import json
from django.test import TestCase
from user.models import User
from friend.models import Friendship
from conversation.models import PrivateConversation, UserPrivateConversation, GroupConversation, UserGroupConversation
from utils.utils_jwt import generate_jwt_token

class GetNewConversationListTestCase(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        
        # 创建好友关系
        self.friendship = Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        
        # 创建私聊会话
        self.private_conversation = PrivateConversation.objects.create(user1=self.user1, user2=self.user2)
        
        # 创建用户与私聊会话的关联
        UserPrivateConversation.objects.create(
            user=self.user1, 
            friendship=self.friendship, 
            conversation=self.private_conversation,
            unread_messages_count=1
        )
        
        # 创建群组会话
        self.group_conversation = GroupConversation.objects.create(title='TestGroup', owner=self.user1)
        
        # 将用户添加到群组中
        self.group_conversation.members.add(self.user1, self.user2)
        
        # 创建用户与群组会话的关联
        UserGroupConversation.objects.create(user=self.user1, group_conversation=self.group_conversation)
        
        # 设置获取新会话列表的URL
        self.list_url = '/conversation/'
        
        # 生成JWT token
        self.token = generate_jwt_token(self.user1.name)

    def test_get_new_conversation_list_success(self):
        # 测试成功获取新会话列表
        response = self.client.get(
            self.list_url,
            data={'userName': self.user1.name},
            HTTP_AUTHORIZATION=self.token
        )
        self.assertEqual(response.status_code, 200)


    def test_get_new_conversation_list_unauthorized(self):
        # 测试未授权用户尝试获取新会话列表
        invalid_token = generate_jwt_token('invalid_user')
        response = self.client.get(
            self.list_url,
            data={'userName': self.user1.name},
            HTTP_AUTHORIZATION=invalid_token
        )
        self.assertEqual(response.status_code, 403)  # 假设未授权状态码为403

    def test_get_new_conversation_list_user_not_found(self):
        # 测试不存在的用户尝试获取新会话列表
        response = self.client.get(
            self.list_url,
            data={'userName': 'unknown_user'},
            HTTP_AUTHORIZATION=self.token
        )
        self.assertEqual(response.status_code, 403) 