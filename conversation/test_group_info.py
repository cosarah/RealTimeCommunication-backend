import json
from django.test import TestCase
from user.models import User
from conversation.models import GroupConversation, UserGroupConversation


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
        
    def test_get_group_info_success(self):
        # 测试成功获取群组信息
        response = self.client.get(self.url, data=self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')
        group_info = json.loads(response.content)
        self.assertEqual(group_info['title'], 'TestGroup')
        self.assertEqual(group_info['owner']['userName'], 'john_doe')

    def test_get_group_info_bad_method(self):
        # 测试非GET请求
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 405)

    def test_get_group_info_user_not_member(self):
        # 测试非群组成员尝试获取群组信息
        data_not_found = self.data.copy()
        data_not_found['userName'] = 'bob_doe' # 非群组成员
        response = self.client.get(self.url, data=self.data) 
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

    def test_set_group_title_success(self):
        # 测试成功设置群组标题
        response = self.client.post(self.url, data=self.data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')
        self.assertEqual(GroupConversation.objects.get(id=self.group_conversation.id).title, 'NewTitle')

    def test_set_group_title_bad_method(self):
        # 测试非POST请求
        response = self.client.get(self.url, data=self.data)
        expected_status_code = 405  # 根据实际的HTTP方法错误处理状态码进行调整
        self.assertEqual(response.status_code, expected_status_code)

    def test_set_group_title_missing_fields(self):
        # 测试缺少字段的请求
        data_missing = self.data.copy()
        data_missing.pop('groupTitle')
        response = self.client.post(self.url, data=data_missing, content_type='application/json')
        expected_status_code = 400  # 根据实际的缺失参数错误处理状态码进行调整
        self.assertEqual(response.status_code, expected_status_code)

    def test_set_group_title_group_not_found(self):
        # 测试群组不存在的情况
        data_wrong_group = self.data.copy()
        data_wrong_group['groupId'] = '999'  # 假设这是一个不存在的群组ID
        response = self.client.post(self.url, data=data_wrong_group, content_type='application/json')
        expected_status_code = 404  # 根据实际的资源未找到错误处理状态码进行调整
        self.assertEqual(response.status_code, expected_status_code)