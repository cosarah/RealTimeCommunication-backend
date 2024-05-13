import json
from django.test import TestCase
from user.models import User
from conversation.models import GroupConversation, UserGroupConversation

class AddGroupMemberTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        self.user3 = User.objects.create(name='alice_doe', password='password')
        self.group_conversation = GroupConversation.objects.create(title='TestGroup', owner=self.user1)
        self.user1_group_conversation = UserGroupConversation.objects.create(user=self.user1, group_conversation=self.group_conversation, identity=2)
        self.user2_group_conversation = UserGroupConversation.objects.create(user=self.user2, group_conversation=self.group_conversation, identity=0)
        self.group_conversation.members.add(self.user2)
        self.url = '/conversation/group/member/add'

        self.correct_data = {
            "userName": "john_doe",
            "groupId": str(self.group_conversation.id),
            "inviteeName": "alice_doe"
        }

    def test_add_group_member_success(self):
        self.assertFalse(UserGroupConversation.objects.filter(user=self.user3, group_conversation=self.group_conversation).exists())
        response = self.client.post(self.url, data=json.dumps(self.correct_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')
        self.assertTrue(UserGroupConversation.objects.filter(user=self.user3, group_conversation=self.group_conversation).exists())

class RemoveGroupMemberTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        self.group_conversation = GroupConversation.objects.create(title='TestGroup', owner=self.user1)
        self.user1_group_conversation = UserGroupConversation.objects.create(user=self.user1, group_conversation=self.group_conversation, identity=2)
        self.user2_group_conversation = UserGroupConversation.objects.create(user=self.user2, group_conversation=self.group_conversation, identity=0)
        self.group_conversation.members.add(self.user2)
        self.url = '/conversation/group/member/remove'

        self.correct_data = {
            "userName": "john_doe",
            "groupId": str(self.group_conversation.id),
            "memberName": "jane_doe"
        }

    def test_remove_group_member_success(self):
        self.assertTrue(UserGroupConversation.objects.filter(user=self.user2, group_conversation=self.group_conversation).exists())
        response = self.client.post(self.url, data=json.dumps(self.correct_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')
        self.assertTrue(UserGroupConversation.objects.filter(user=self.user2, group_conversation=self.group_conversation).exists())
        self.assertTrue(UserGroupConversation.objects.get(user=self.user2, group_conversation=self.group_conversation).is_kicked)