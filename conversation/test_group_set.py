import json
from django.test import TestCase
from user.models import User
from conversation.models import GroupConversation, UserGroupConversation

class SetGroupOwnerTestCase(TestCase):
    def setUp(self):
        # 创建测试用户和群组会话
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        self.user3 = User.objects.create(name='alice_doe', password='password')
        self.group_conversation = GroupConversation.objects.create(title='TestGroup', owner=self.user1)
        self.user1_group_conversation = UserGroupConversation.objects.create(user=self.user1, group_conversation=self.group_conversation, identity=2)
        self.user2_group_conversation = UserGroupConversation.objects.create(user=self.user2, group_conversation=self.group_conversation, identity=1)
        self.user3_group_conversation = UserGroupConversation.objects.create(user=self.user3, group_conversation=self.group_conversation, identity=0)
        self.group_conversation.admins.add(self.user2)
        self.group_conversation.members.add(self.user3)
        
        # 设置测试URL和数据
        self.url = '/conversation/group/set/owner'
        self.data = {
            'userName': 'john_doe',
            'groupId': str(self.group_conversation.id),
            'newOwnerName': 'jane_doe'
        }

    def test_set_owner_success(self):
        # 测试成功转移群主
        response = self.client.post(self.url, data=json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')
        # self.assertEqual(self.group_conversation.owner.name, 'jane_doe')
        ############################ TODO：debug#######################


    def test_set_owner_bad_method(self):
        # 测试非POST请求
        response = self.client.get(self.url, data=self.data)
        self.assertEqual(response.status_code, 405)  # 假设405是方法不被允许的错误码

    def test_set_owner_missing_fields(self):
        # 测试缺少字段的请求
        data_missing = self.data.copy()
        data_missing.pop('newOwnerName')
        response = self.client.post(self.url, data=json.dumps(data_missing), content_type='application/json')
        self.assertEqual(response.status_code, 400)  # 假设400是坏参数的错误码
        self.assertIn('Bad parameters', json.loads(response.content)['info'])

    def test_set_owner_group_not_found(self):
        # 测试群组不存在的情况
        data_wrong_group = self.data.copy()
        data_wrong_group['groupId'] = '999'  # 假设这是一个不存在的群组ID
        response = self.client.post(self.url, data=json.dumps(data_wrong_group), content_type='application/json')
        self.assertEqual(response.status_code, 404)  # 假设404是资源未找到的错误码
        self.assertIn('Conversation not found', json.loads(response.content)['info'])

    def test_set_owner_user_not_found(self):
        # 测试用户不存在的情况
        data_user_not_found = self.data.copy()
        data_user_not_found['userName'] = 'unknown_user'
        response = self.client.post(self.url, data=json.dumps(data_user_not_found), content_type='application/json')
        self.assertEqual(response.status_code, 404)  # 用户未找到的错误码
        self.assertIn('User not found', json.loads(response.content)['info'])

    def test_set_owner_permission_denied(self):
        # 测试非群主尝试转移群主
        data_permission_denied = self.data.copy()
        data_permission_denied['userName'] = 'jane_doe'  # 非群主用户
        response = self.client.post(self.url, data=json.dumps(data_permission_denied), content_type='application/json')
        self.assertEqual(response.status_code, 403)  # 假设403是权限拒绝的错误码
        self.assertIn('Permission denied', json.loads(response.content)['info'])


import json
from django.test import TestCase
from user.models import User
from conversation.models import GroupConversation, UserGroupConversation

class AddGroupAdminTestCase(TestCase):
    def setUp(self):
        # 创建测试用户和群组会话
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        self.user3 = User.objects.create(name='alice_doe', password='password')
        self.user4 = User.objects.create(name='bob_doe', password='password')
        self.group_conversation = GroupConversation.objects.create(title='TestGroup', owner=self.user1)
        self.user1_group_conversation = UserGroupConversation.objects.create(user=self.user1, group_conversation=self.group_conversation, identity=2)
        self.user2_group_conversation = UserGroupConversation.objects.create(user=self.user2, group_conversation=self.group_conversation, identity=0)
        self.user3_group_conversation = UserGroupConversation.objects.create(user=self.user3, group_conversation=self.group_conversation, identity=0)
        self.group_conversation.members.add(self.user2)
        self.group_conversation.members.add(self.user3)
        
        # 设置测试URL和数据
        self.url = '/conversation/group/set/admin/add'
        self.data = {
            'userName': 'john_doe',
            'groupId': str(self.group_conversation.id),
            'newAdminNameList': ['jane_doe']
        }

    def test_add_admin_success(self):
        # 测试成功添加管理员
        response = self.client.post(self.url, data=json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')
        self.assertEqual([admin.name for admin in self.group_conversation.admins.all()], ['jane_doe'])  # 验证用户1还是群主
        # self.assertEqual(self.user2_group_conversation.identity, 1)  # 验证用户2现在是管理员
        ############################ TODO：debug#######################

    def test_add_admin_bad_method(self):
        # 测试非POST请求
        response = self.client.get(self.url, data=self.data)
        self.assertEqual(response.status_code, 405)  # 假设405是方法不被允许的错误码

    def test_add_admin_missing_fields(self):
        # 测试缺少字段的请求
        data_missing = self.data.copy()
        data_missing.pop('newAdminNameList')
        response = self.client.post(self.url, data=json.dumps(data_missing), content_type='application/json')
        self.assertEqual(response.status_code, 400)  # 假设400是坏参数的错误码
        self.assertIn('Bad parameters', json.loads(response.content)['info'])

    def test_add_admin_group_not_found(self):
        # 测试群组不存在的情况
        data_wrong_group = self.data.copy()
        data_wrong_group['groupId'] = '999'  # 假设这是一个不存在的群组ID
        response = self.client.post(self.url, data=json.dumps(data_wrong_group), content_type='application/json')
        self.assertEqual(response.status_code, 404)  # 假设404是资源未找到的错误码
        self.assertIn('Conversation not found', json.loads(response.content)['info'])

    def test_add_admin_user_not_found(self):
        # 测试用户不存在的情况
        data_user_not_found = self.data.copy()
        data_user_not_found['userName'] = 'unknown_user'
        response = self.client.post(self.url, data=json.dumps(data_user_not_found), content_type='application/json')
        self.assertEqual(response.status_code, 404)  # 用户未找到的错误码
        self.assertIn('User not found', json.loads(response.content)['info'])

    def test_add_admin_permission_denied(self):
        # 测试非群主尝试添加管理员
        data_permission_denied = self.data.copy()
        data_permission_denied['userName'] = 'jane_doe'  # 非群主用户
        response = self.client.post(self.url, data=json.dumps(data_permission_denied), content_type='application/json')
        self.assertEqual(response.status_code, 403)  # 假设403是权限拒绝的错误码
        self.assertIn('Permission denied', json.loads(response.content)['info'])