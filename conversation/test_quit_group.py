import json
from django.test import TestCase
from user.models import User
from conversation.models import GroupConversation, UserGroupConversation

class QuitGroupTestCase(TestCase):
    def setUp(self):
        # 创建测试用户和群组会话
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        self.group_conversation = GroupConversation.objects.create(title='TestGroup', owner=self.user1)
        self.user1_group_conversation = UserGroupConversation.objects.create(user=self.user1, group_conversation=self.group_conversation, identity=2)
        self.user2_group_conversation = UserGroupConversation.objects.create(user=self.user2, group_conversation=self.group_conversation, identity=0)
        self.group_conversation.members.add(self.user2)
        self.url = '/conversation/group/member/quit'

        self.correct_data = {
            "userName": "jane_doe",
            "groupId": str(self.group_conversation.id)
        }

    def test_quit_group_success(self):
        # 测试成功退出群组
        self.assertTrue(UserGroupConversation.objects.filter(user=self.user2, group_conversation=self.group_conversation).exists())
        response = self.client.post(self.url, data=json.dumps(self.correct_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')
        self.assertFalse(UserGroupConversation.objects.filter(user=self.user2, group_conversation=self.group_conversation).exists())

    def test_quit_group_bad_method(self):
        # 测试非POST请求
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_quit_group_missing_fields(self):
        # 测试缺少字段的请求
        data = self.correct_data.copy()
        del data['groupId']  # 删除必需字段
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Bad parameters', json.loads(response.content)['info'])

    def test_quit_group_group_not_found(self):
        # 测试找不到群组的情况
        data = self.correct_data.copy()
        data['groupId'] = -1
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Conversation not found', json.loads(response.content)['info'])

    def test_quit_group_user_not_found(self):
        # 测试找不到用户的情况
        data = self.correct_data.copy()
        data['userName'] = 'unknown_user'
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('User not found', json.loads(response.content)['info'])

    def test_quit_group_permission_denied(self):
        # 测试群主尝试退出群组的情况（通常群主不能直接退出）
        data = {
            "userName": "john_doe",
            "groupId": str(self.group_conversation.id)
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content)['code'], -12)
        self.assertEqual(json.loads(response.content)['info'], 'Permission denied')