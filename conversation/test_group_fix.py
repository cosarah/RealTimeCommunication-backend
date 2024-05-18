import json
from django.test import TestCase
from user.models import User
from conversation.models import GroupConversation, UserGroupConversation
from utils.utils_jwt import generate_jwt_token

class UserGroupConversationFixTestCase(TestCase):
    def setUp(self):
        # 设置测试用户和群组会话
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        self.group_conversation = GroupConversation.objects.create(title='TestGroup', owner=self.user1)

        self.user_group_conversation = UserGroupConversation.objects.create(user=self.user1, group_conversation=self.group_conversation, identity=2)
        self.user2_group_conversation = UserGroupConversation.objects.create(user=self.user2, group_conversation=self.group_conversation, identity=0)
        self.group_conversation.members.add(self.user2)
        self.url = '/conversation/group/member/fix'

        self.correct_data = {
            "userName": "john_doe",
            "groupId": str(self.group_conversation.id),
            "groupAlias": "John's Group",
        }

        self.headers = {
            "Authorization": generate_jwt_token(self.user1.name),
            "Content-Type": "application/json"
        }
        self.token=generate_jwt_token(self.user1.name)

    def test_fix_group_conversation_success(self):
        # 测试成功修复群组会话信息
        response = self.client.post(self.url, data=json.dumps(self.correct_data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')

        self.assertEqual(UserGroupConversation.objects.get(user=self.user1, group_conversation=self.group_conversation).alias, 'John\'s Group')

    def test_fix_group_conversation_bad_method(self):
        # 测试非POST请求
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_fix_group_conversation_missing_fields(self):
        # 测试缺少字段的请求
        data = self.correct_data.copy()
        del data['groupAlias']  # 删除一个必需字段
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Bad parameters', json.loads(response.content)['info'])

    def test_fix_group_conversation_group_not_found(self):
        # 测试找不到群组的情况
        data = self.correct_data.copy()
        data['groupId'] = '-1'
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Conversation not found', json.loads(response.content)['info'])

    def test_fix_group_conversation_user_not_found(self):
        # 测试找不到用户的情况
        data = self.correct_data.copy()
        data['userName'] = 'unknown_user'
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 403)
        self.assertIn('Permission denied', json.loads(response.content)['info'])