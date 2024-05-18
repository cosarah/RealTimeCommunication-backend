import json
from django.test import TestCase
from user.models import User
from conversation.models import GroupConversation, UserGroupConversation
from utils.utils_jwt import generate_jwt_token

class GetGroupInfoTestCase(TestCase):
    def setUp(self):
        # 创建测试用户和群组会话
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        self.group_conversation = GroupConversation.objects.create(title='TestGroup', owner=self.user1)
        self.user1_group_conversation = UserGroupConversation.objects.create(user=self.user1, group_conversation=self.group_conversation, identity=2)
        self.user2_group_conversation = UserGroupConversation.objects.create(user=self.user2, group_conversation=self.group_conversation, identity=0)
        self.group_conversation.members.add(self.user1)
        self.group_conversation.members.add(self.user2)
        
        self.url = '/conversation/group/member'
        self.data = {
            'userName': 'john_doe',
            'groupId': self.group_conversation.id
        }
        self.headers = {
            "Authorization": generate_jwt_token(self.user1.name),
            "Content-Type": "application/json"
        }
        self.token=generate_jwt_token(self.user1.name)

    def test_get_group_info_success(self):
        # 测试成功获取群组信息
        response = self.client.get(self.url, data=self.data, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')
        group_info = json.loads(response.content)
        self.assertEqual(group_info['title'], 'TestGroup')
        self.assertEqual(group_info['owner']['userName'], 'john_doe')

    def test_get_group_info_bad_method(self):
        # 测试非GET请求
        response = self.client.post(self.url, data=self.data, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 405)

    def test_get_group_info_user_not_member(self):
        # 测试非群组成员尝试获取群组信息
        data_not_found = self.data.copy()
        data_not_found['userName'] = 'bob_doe' # 非群组成员
        response = self.client.get(self.url, data=self.data, HTTP_AUTHORIZATION=self.token) 
        self.assertEqual(response.status_code, 200)  


class SetGroupTitleTestCase(TestCase):
    def setUp(self):
        # 创建测试用户和群组会话
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        self.group_conversation = GroupConversation.objects.create(title='OldTitle', owner=self.user1)
        self.user1_group_conversation = UserGroupConversation.objects.create(user=self.user1, group_conversation=self.group_conversation, identity=2)
        self.user2_group_conversation = UserGroupConversation.objects.create(user=self.user2, group_conversation=self.group_conversation, identity=0)
        self.group_conversation.members.add(self.user2)
        
        # 设置测试URL和数据
        self.url = '/conversation/group/set/title'
        self.data = {
            'userName': 'john_doe',
            'groupId': str(self.group_conversation.id),  # 确保ID是字符串格式
            'groupTitle': 'NewTitle'
        }
        self.headers = {
            "Authorization": generate_jwt_token(self.user1.name),
            "Content-Type": "application/json"
        }
        self.token=generate_jwt_token(self.user1.name)

    def test_set_group_title_success(self):
        # 测试成功设置群组标题
        response = self.client.post(self.url, data=self.data, content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')
        self.assertEqual(GroupConversation.objects.get(id=self.group_conversation.id).title, 'NewTitle')

    def test_set_group_title_bad_method(self):
        # 测试非POST请求
        response = self.client.get(self.url, data=self.data, HTTP_AUTHORIZATION=self.token)
        expected_status_code = 405  # 根据实际的HTTP方法错误处理状态码进行调整
        self.assertEqual(response.status_code, expected_status_code)

    def test_set_group_title_missing_fields(self):
        # 测试缺少字段的请求
        data_missing = self.data.copy()
        data_missing.pop('groupTitle')
        response = self.client.post(self.url, data=data_missing, content_type='application/json', HTTP_AUTHORIZATION=self.token)
        expected_status_code = 400  # 根据实际的缺失参数错误处理状态码进行调整
        self.assertEqual(response.status_code, expected_status_code)

    def test_set_group_title_group_not_found(self):
        # 测试群组不存在的情况
        data_wrong_group = self.data.copy()
        data_wrong_group['groupId'] = '999'  # 假设这是一个不存在的群组ID
        response = self.client.post(self.url, data=data_wrong_group, content_type='application/json', HTTP_AUTHORIZATION=self.token)
        expected_status_code = 404  # 根据实际的资源未找到错误处理状态码进行调整
        self.assertEqual(response.status_code, expected_status_code)

class SetGroupAnnouncementTestCase(TestCase):
    def setUp(self):
        # 创建测试用户和群组会话
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        self.group_conversation = GroupConversation.objects.create(title='TestGroup', owner=self.user1)
        self.user1_group_conversation = UserGroupConversation.objects.create(user=self.user1, group_conversation=self.group_conversation, identity=2)
        self.user2_group_conversation = UserGroupConversation.objects.create(user=self.user2, group_conversation=self.group_conversation, identity=0)
        self.group_conversation.members.add(self.user1)
        self.group_conversation.members.add(self.user2)
        
        # 设置测试URL和数据
        self.url = '/conversation/group/set/announce'
        self.data = {
            'userName': 'john_doe',
            'groupId': str(self.group_conversation.id),  # 确保ID是字符串格式
            'announcement': 'This is a new announcement.'
        }
        self.headers = {
            "Authorization": generate_jwt_token(self.user1.name),
            "Content-Type": "application/json"
        }
        self.token=generate_jwt_token(self.user1.name)

    def test_set_announcement_success(self):
        # 测试成功设置群组公告
        response = self.client.post(self.url, data=json.dumps(self.data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')
        self.assertEqual(self.group_conversation.get_announcements()[0]['text'], 'This is a new announcement.')

    def test_set_announcement_bad_method(self):
        # 测试非POST请求
        response = self.client.get(self.url, data=self.data, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 405)  # 假设405是方法不被允许的错误码

    def test_set_announcement_missing_fields(self):
        # 测试缺少字段的请求
        data_missing = self.data.copy()
        data_missing.pop('announcement')
        response = self.client.post(self.url, data=json.dumps(data_missing), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 400)  # 假设400是坏参数的错误码
        self.assertIn('Bad parameters', json.loads(response.content)['info'])

    def test_set_announcement_group_not_found(self):
        # 测试群组不存在的情况
        data_wrong_group = self.data.copy()
        data_wrong_group['groupId'] = '999'  # 假设这是一个不存在的群组ID
        response = self.client.post(self.url, data=json.dumps(data_wrong_group), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 404)  # 假设404是资源未找到的错误码
        self.assertIn('Conversation not found', json.loads(response.content)['info'])

    def test_set_announcement_user_not_found(self):
        # 测试用户不存在的情况
        data_user_not_found = self.data.copy()
        data_user_not_found['userName'] = 'unknown_user'
        response = self.client.post(self.url, data=json.dumps(data_user_not_found), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 403)  # 用户未找到的错误码
        self.assertIn('Permission denied', json.loads(response.content)['info'])

    def test_set_announcement_permission_denied(self):
        # 测试非群主尝试设置群组公告
        data_permission_denied = self.data.copy()
        data_permission_denied['userName'] = 'jane_doe'  # 非群主用户
        response = self.client.post(self.url, data=json.dumps(data_permission_denied), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 403)  # 假设403是权限拒绝的错误码
        self.assertIn('Permission denied', json.loads(response.content)['info'])


class GetGroupConversationListTestCase(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        
        # 创建群组会话并添加用户1和用户2
        self.group_conversation1 = GroupConversation.objects.create(title='TestGroup1', owner=self.user1)
        self.user1_group_conversation1 = UserGroupConversation.objects.create(user=self.user1, group_conversation=self.group_conversation1, identity=2)
        self.user2_group_conversation1 = UserGroupConversation.objects.create(user=self.user2, group_conversation=self.group_conversation1, identity=0)
        
        self.group_conversation2 = GroupConversation.objects.create(title='TestGroup2', owner=self.user1)
        self.user1_group_conversation2 = UserGroupConversation.objects.create(user=self.user1, group_conversation=self.group_conversation2, identity=2)
        
        # 设置测试URL和数据
        self.url = '/conversation/group'
        self.data = {
            'userName': 'john_doe'
        }

        self.headers = {
            "Authorization": generate_jwt_token(self.user1.name),
            "Content-Type": "application/json"
        }

        self.token=generate_jwt_token(self.user1.name)

    def test_get_group_conversation_list_success(self):
        # 测试成功获取群组会话列表
        response = self.client.get(self.url, data=self.data, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')
        
        # 确保返回了群组会话列表
        group_conversations = json.loads(response.content)['groupConversationList']
        self.assertEqual(len(group_conversations), 2)
        self.assertEqual(group_conversations[0]['groupConversation']['title'], 'TestGroup1')
        self.assertEqual(group_conversations[1]['groupConversation']['title'], 'TestGroup2')

    def test_get_group_conversation_list_bad_method(self):
        # 测试非GET请求
        response = self.client.post(self.url, data=self.data, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 405)  # 假设405是方法不被允许的错误码

    def test_get_group_conversation_list_missing_fields(self):
        # 测试缺少字段的请求
        response = self.client.get(self.url, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 403) 
        self.assertIn('Permission denied', json.loads(response.content)['info'])

    def test_get_group_conversation_list_user_not_found(self):
        # 测试用户不存在的情况
        data_user_not_found = self.data.copy()
        data_user_not_found['userName'] = 'unknown_user'
        response = self.client.get(self.url, data=data_user_not_found, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 403)  # 用户未找到的错误码
        self.assertIn('Permission denied', json.loads(response.content)['info'])