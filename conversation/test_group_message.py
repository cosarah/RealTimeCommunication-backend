import json
from django.test import TestCase
from user.models import User
from conversation.models import GroupConversation, UserGroupConversation, GroupMessage
from utils.utils_jwt import generate_jwt_token

class GetGroupMessageListTestCase(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        self.group_conversation = GroupConversation.objects.create(title='TestGroup', owner=self.user1)
        self.user1_group_conversation = UserGroupConversation.objects.create(user=self.user1, group_conversation=self.group_conversation, identity=2)
        self.user2_group_conversation = UserGroupConversation.objects.create(user=self.user2, group_conversation=self.group_conversation, identity=0)
        self.group_conversation.members.add(self.user2)
        
        # 创建群组消息
        self.group_message1 = GroupMessage.objects.create(
            sender=self.user1,
            text='Hello Group!',
            conversation=self.group_conversation
        )
        self.group_message2 = GroupMessage.objects.create(
            sender=self.user2,
            text='Hi everyone!',
            conversation=self.group_conversation
        )

        self.user1_group_conversation.messages.add(self.group_message1)
        self.user1_group_conversation.messages.add(self.group_message2)

        
        # 设置URL，这里需要根据实际的URL配置调整
        self.list_url = '/conversation/group/message'
    
        self.token = generate_jwt_token(self.user1.name)
    
    def test_get_group_message_list_success(self):
        # 测试获取群组消息列表成功
        response = self.client.get(self.list_url, data={'userName': self.user1.name,'groupId': self.group_conversation.id}, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['messageList']), 2)
        self.assertIn('doe', json.loads(response.content)['messageList'][0]['senderName'])
        self.assertIn('doe', json.loads(response.content)['messageList'][1]['senderName'])
    
    def test_get_group_message_list_unauthorized(self):
        # 测试未授权用户尝试获取群组消息列表
        invalid_headers = {
            'Authorization': 'JWT invalid_token',
            'Content-Type': 'application/json'
        }
        response = self.client.get(self.list_url, **invalid_headers)
        self.assertEqual(response.status_code, 401)  # 假设未授权状态码为401
    
    def test_get_group_message_list_group_not_found(self):
        # 测试群组不存在的情况
        response = self.client.get(self.list_url, data={'userName': self.user1.name,'groupId': -1}, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 404)  # 假设群组不存在状态码为404


class SendGroupMessageTestCase(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        
        # 创建群组会话
        self.group_conversation = GroupConversation.objects.create(title='TestGroup', owner=self.user1)
        
        # 将用户添加到群组中
        self.group_conversation.members.add(self.user1, self.user2)
        
        # 创建群组会话与用户的关联
        UserGroupConversation.objects.create(user=self.user1, group_conversation=self.group_conversation, identity=2)
        UserGroupConversation.objects.create(user=self.user2, group_conversation=self.group_conversation, identity=0)
        
        # 设置发送群组消息的URL
        self.send_message_url = '/conversation/group/message/send'
        
        # 生成JWT token
        self.token = generate_jwt_token(self.user1.name)
    
    def test_send_group_message_success(self):
        # 测试发送群组消息成功
        data = {
            "userName": "john_doe",
            "groupId": self.group_conversation.id,
            "message": "Hello, group!",
            "quote": ""
        }
        response = self.client.post(
            self.send_message_url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)  # 假设成功响应的code为0
        
        # 验证消息是否已发送
        messages = GroupMessage.objects.filter(conversation=self.group_conversation)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].text, "Hello, group!")
    
    def test_send_group_message_unauthorized(self):
        # 测试未授权用户尝试发送群组消息
        invalid_token = generate_jwt_token('invalid_user')
        data = {
            "userName": "john_doe",
            "groupId": self.group_conversation.id,
            "message": "Hello, group!",
            "quote": ""
        }
        response = self.client.post(
            self.send_message_url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=invalid_token
        )
        self.assertEqual(response.status_code, 403)  
    
    def test_send_group_message_missing_fields(self):
        # 测试缺少字段的请求
        data = {
            "userName": "john_doe",  # 缺少message字段
            "groupId": self.group_conversation.id
        }
        response = self.client.post(
            self.send_message_url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        self.assertEqual(response.status_code, 400)  # 假设缺少参数的状态码为400
    
    def test_send_group_message_group_not_found(self):
        # 测试群组不存在的情况
        data = {
            "userName": "john_doe",
            "groupId": -1,
            "message": "Hello, group!",
            "quote": ""
        }
        response = self.client.post(
            self.send_message_url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        self.assertEqual(response.status_code, 404)  # 假设群组不存在状态码为404

class DeleteGroupMessageTestCase(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        
        # 创建群组会话
        self.group_conversation = GroupConversation.objects.create(title='TestGroup', owner=self.user1)
        
        # 将用户添加到群组中
        self.group_conversation.members.add(self.user1, self.user2)
        
        # 创建群组消息
        self.group_message1 = GroupMessage.objects.create(
            sender=self.user1,
            text='Hello Group!',
            conversation=self.group_conversation
        )
        self.group_message2 = GroupMessage.objects.create(
            sender=self.user2,
            text='Hi everyone!',
            conversation=self.group_conversation
        )
        
        # 创建群组会话与用户的关联
        UserGroupConversation.objects.create(user=self.user1, group_conversation=self.group_conversation, identity=2)
        UserGroupConversation.objects.create(user=self.user2, group_conversation=self.group_conversation, identity=0)
        
        # 设置删除群组消息的URL，并生成JWT token
        self.delete_message_url = '/conversation/group/message/delete'
        self.token = generate_jwt_token(self.user1.name)
        self.data = {
            "userName": self.user1.name,
            "groupId": self.group_conversation.id,
            "messageId": self.group_message1.id
        }

    def test_delete_group_message_success(self):
        # 测试成功删除群组消息
        response = self.client.post(
            self.delete_message_url,
            data=self.data,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)  # 假设成功响应的code为0
        
        # 验证消息是否已被删除
        self.assertTrue(GroupMessage.objects.filter(id=self.group_message1.id).exists())

    def test_delete_group_message_unauthorized(self):
        # 测试未授权用户尝试删除群组消息
        invalid_token = generate_jwt_token('invalid_user')
        response = self.client.post(
            self.delete_message_url,
            data=self.data,
            content_type='application/json',
            HTTP_AUTHORIZATION=invalid_token
        )
        self.assertEqual(response.status_code, 403)  # 假设未授权状态码为403

    def test_delete_group_message_message_not_found(self):
        # 测试删除不存在的群组消息
        response = self.client.post(
            self.delete_message_url,
            data={
                "userName": self.user1.name,
                "groupId": self.group_conversation.id,
                "messageId": 999999999  # 不存在的消息ID
            },
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        self.assertEqual(response.status_code, 404)  # 假设消息不存在状态码为404

    def test_delete_group_message_group_not_found(self):
        # 测试群组不存在的情况
        response = self.client.post(
            self.delete_message_url,
            data={
                "userName": self.user1.name,
                "groupId": 999999999,  # 不存在的群组ID
                "messageId": self.group_message1.id
            },
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        self.assertEqual(response.status_code, 404)  # 假设群组不存在状态码为404

class WithdrawGroupMessageTestCase(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        
        # 创建群组会话
        self.group_conversation = GroupConversation.objects.create(title='TestGroup', owner=self.user1)
        # 创建群组会话与用户的关联
        UserGroupConversation.objects.create(user=self.user1, group_conversation=self.group_conversation, identity=2)
        UserGroupConversation.objects.create(user=self.user2, group_conversation=self.group_conversation, identity=0)
        # 将用户添加到群组中
        self.group_conversation.members.add(self.user1, self.user2)
        
        # 创建群组消息
        self.group_message1 = GroupMessage.objects.create(
            sender=self.user1,
            text='Hello Group!',
            conversation=self.group_conversation
        )
        self.group_message2 = GroupMessage.objects.create(
            sender=self.user2,
            text='Hi everyone!',
            conversation=self.group_conversation
        )
        
        # 创建群组会话与用户的关联
        # 这里假设已经存在了相应的UserGroupConversation对象
        # 如果需要，可以取消注释下面的代码
        # UserGroupConversation.objects.create(user=self.user1, group_conversation=self.group_conversation, identity=2)
        # UserGroupConversation.objects.create(user=self.user2, group_conversation=self.group_conversation, identity=0)
        
        # 设置URL，并生成JWT token
        self.withdraw_message_url = '/conversation/group/message/withdraw'
        self.token = generate_jwt_token(self.user1.name)
    
    def test_withdraw_group_message_success(self):
        # 测试成功撤回群组消息
        data = {
            "userName": "john_doe",
            "groupId": self.group_conversation.id,
            "messageId": self.group_message1.id
        }
        response = self.client.post(
            self.withdraw_message_url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)  # 假设成功响应的code为0
        
        # 验证消息是否已被撤回（这里假设撤回消息会从数据库中删除）
        self.assertFalse(GroupMessage.objects.filter(id=self.group_message1.id).exists())
    
    def test_withdraw_group_message_unauthorized(self):
        # 测试未授权用户尝试撤回群组消息
        invalid_token = generate_jwt_token('invalid_user')
        data = {
            "userName": "john_doe",
            "groupId": self.group_conversation.id,
            "messageId": self.group_message1.id
        }
        response = self.client.post(
            self.withdraw_message_url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=invalid_token
        )
        self.assertEqual(response.status_code, 403)  # 假设未授权状态码为403
    
    def test_withdraw_group_message_message_not_found(self):
        # 测试撤回不存在的群组消息
        data = {
            "userName": "john_doe",
            "groupId": self.group_conversation.id,
            "messageId": -1  # 不存在的消息ID
        }
        response = self.client.post(
            self.withdraw_message_url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        self.assertEqual(response.status_code, 404)  # 假设消息不存在状态码为404
    
    def test_withdraw_group_message_group_not_found(self):
        # 测试在不存在的群组中撤回消息
        data = {
            "userName": "john_doe",
            "groupId": -1,  # 不存在的群组ID
            "messageId": self.group_message1.id
        }
        response = self.client.post(
            self.withdraw_message_url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.token
        )
        self.assertEqual(response.status_code, 404)  # 假设群组不存在状态码为404