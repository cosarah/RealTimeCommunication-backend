import json
from django.test import TestCase
from user.models import User
from friend.models import Friendship
from conversation.models import GroupConversation, UserGroupConversation, GroupConversationRequest
from utils.utils_jwt import generate_jwt_token

class InviteGroupMemberTestCase(TestCase):
    def setUp(self):
        # 创建测试用户和群组会话
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        self.user3 = User.objects.create(name='alice_doe', password='password')
        self.group_conversation = GroupConversation.objects.create(title='TestGroup', owner=self.user1)
        self.user1_group_conversation = UserGroupConversation.objects.create(user=self.user1, group_conversation=self.group_conversation, identity=2)
        self.user2_group_conversation = UserGroupConversation.objects.create(user=self.user2, group_conversation=self.group_conversation, identity=0)
        self.group_conversation.members.add(self.user1)
        self.group_conversation.members.add(self.user2)
        self.url = '/conversation/group/member/request/invite'

        # 创建友谊关系
        self.friendship1 = Friendship.objects.create(from_user=self.user2, to_user=self.user3)
        self.friendship2 = Friendship.objects.create(from_user=self.user3, to_user=self.user2)

        self.correct_data = {
            "userName": "jane_doe",
            "groupId": str(self.group_conversation.id),
            "friendName": "alice_doe",
            "message": "Please join our group!"
        }
        self.headers = {
            "Authorization": generate_jwt_token(self.user2.name),
            "Content-Type": "application/json"
        }

    def test_invite_group_member_success(self):
        # 测试成功邀请群组成员
        response = self.client.post(self.url, data=json.dumps(self.correct_data), content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')

    def test_invite_group_member_bad_method(self):
        # 测试非POST请求
        response = self.client.get(self.url, headers=self.headers)
        self.assertEqual(response.status_code, 405)

    def test_invite_group_member_missing_fields(self):
        # 测试缺少字段的请求
        data = self.correct_data.copy()
        del data['friendName']
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Bad parameters', json.loads(response.content)['info'])

    def test_invite_group_member_group_not_found(self):
        # 测试群组不存在的情况
        data = self.correct_data.copy()
        data['groupId'] = -1
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Conversation not found', json.loads(response.content)['info'])

    def test_invite_group_member_user_not_found(self):
        # 测试用户不存在的情况
        data = self.correct_data.copy()
        data['friendName'] = 'unknown_user'
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('User not found', json.loads(response.content)['info'])

    def test_invite_group_member_no_friendship(self):
        # 测试邀请者和被邀请者之间不存在好友关系
        self.friendship1.delete()
        response = self.client.post(self.url, data=json.dumps(self.correct_data), content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 404)  # 没有好友关系
        self.assertEqual(json.loads(response.content)['code'], -6)  # 没有好友关系
        self.assertIn('Friendship not found', json.loads(response.content)['info'])

    def test_invite_group_member_already_invited(self):
        # 测试被邀请者已经被邀请，成功
        GroupConversationRequest.objects.create(from_user=self.user2, to_user=self.user3, group_conversation=self.group_conversation, message="Initial invitation")
        response = self.client.post(self.url, data=json.dumps(self.correct_data), content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 200)  
        self.assertEqual(json.loads(response.content)['code'], 0)  
        self.assertEqual(GroupConversationRequest.objects.count(), 1)  # 邀请记录未删除
        self.assertEqual(GroupConversationRequest.objects.get(from_user=self.user2, to_user=self.user3, group_conversation=self.group_conversation).message, self.correct_data['message'])  # 邀请记录修改

    def test_invite_group_member_member_already_in_group(self):
        # 测试被邀请者已经是群组成员
        UserGroupConversation.objects.create(user=self.user3, group_conversation=self.group_conversation, identity=0)
        response = self.client.post(self.url, data=json.dumps(self.correct_data), content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 403)  # 403表示已是群组成员
        self.assertEqual(json.loads(response.content)['code'], -7)  
        self.assertIn('Already exist', json.loads(response.content)['info'])


class AcceptGroupInvitationTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        self.user3 = User.objects.create(name='alice_doe', password='password')
        self.group_conversation = GroupConversation.objects.create(title='TestGroup', owner=self.user1)
        self.user1_group_conversation = UserGroupConversation.objects.create(user=self.user1, group_conversation=self.group_conversation, identity=2)
        self.user2_group_conversation = UserGroupConversation.objects.create(user=self.user2, group_conversation=self.group_conversation, identity=0)
        self.group_conversation.members.add(self.user1)
        self.group_conversation.members.add(self.user2)
        self.url = '/conversation/group/member/request/invite'

        # 创建友谊关系
        self.friendship1 = Friendship.objects.create(from_user=self.user2, to_user=self.user3)
        self.friendship2 = Friendship.objects.create(from_user=self.user3, to_user=self.user2)

        # 创建群组邀请
        self.group_conversation_request = GroupConversationRequest.objects.create(
            from_user=self.user2,
            to_user=self.user3,
            group_conversation=self.group_conversation,
            message="Please join our group!",
            status=0  # Pending status
        )
        
        self.url = '/conversation/group/member/request/accept'

        self.correct_data = {
            "userName": "jane_doe",
            "groupId": str(self.group_conversation.id),
            "inviteeName": "alice_doe"
        }

        self.headers = {
            "Authorization": generate_jwt_token(self.user2.name),
            "Content-Type": "application/json"
        }

    def test_accept_group_invitation_success(self):
        # 测试成功接受群组邀请
        self.assertFalse(UserGroupConversation.objects.filter(user=self.user3, group_conversation=self.group_conversation).exists())
        response = self.client.post(self.url, data=json.dumps(self.correct_data), content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')
        self.assertTrue(UserGroupConversation.objects.filter(user=self.user2, group_conversation=self.group_conversation).exists())
        self.group_conversation_request.refresh_from_db()
        self.assertEqual(self.group_conversation_request.status, 1)  # Accepted status

    def test_accept_group_invitation_bad_method(self):
        # 测试非POST请求
        response = self.client.get(self.url, headers=self.headers)
        self.assertEqual(response.status_code, 405)

    def test_accept_group_invitation_missing_fields(self):
        # 测试缺少字段的请求
        data = self.correct_data.copy()
        del data['inviteeName']
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Bad parameters', json.loads(response.content)['info'])

    def test_accept_group_invitation_group_not_found(self):
        # 测试群组不存在的情况
        data = self.correct_data.copy()
        data['groupId'] = -1
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Conversation not found', json.loads(response.content)['info'])

    def test_accept_group_invitation_user_not_found(self):
        # 测试用户不存在的情况
        data = self.correct_data.copy()
        data['userName'] = 'unknown_user'
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 403)
        self.assertIn('Permission denied', json.loads(response.content)['info'])

    def test_accept_group_invitation_no_invitation(self):
        # 测试没有对应的群组邀请
        self.group_conversation_request.delete()
        response = self.client.post(self.url, data=json.dumps(self.correct_data), content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Request not found', json.loads(response.content)['info'])

    def test_accept_group_invitation_already_member(self):
        # 测试被邀请者已经是群组成员
        UserGroupConversation.objects.create(user=self.user3, group_conversation=self.group_conversation, identity=0)
        GroupConversation.objects.get(id=self.group_conversation.id).members.add(self.user3)

        response = self.client.post(self.url, data=json.dumps(self.correct_data), content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 403)
        self.assertIn('Already exist', json.loads(response.content)['info'])

    def test_accept_group_invitation_invitation_already_accepted(self):
        # 测试邀请已被接受
        self.group_conversation_request.status = 1  # Accepted status
        self.group_conversation_request.save()
        response = self.client.post(self.url, data=json.dumps(self.correct_data), content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 403)
        self.assertIn('Already exist', json.loads(response.content)['info'])

class RejectGroupInvitationTestCase(TestCase):
    def setUp(self):
        # 创建测试用户和群组会话
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        self.user3 = User.objects.create(name='alice_doe', password='password')
        self.group_conversation = GroupConversation.objects.create(title='TestGroup', owner=self.user1)
        self.user1_group_conversation = UserGroupConversation.objects.create(user=self.user1, group_conversation=self.group_conversation, identity=2)
        self.user2_group_conversation = UserGroupConversation.objects.create(user=self.user2, group_conversation=self.group_conversation, identity=0)
        self.group_conversation.members.add(self.user2)
        
        # 创建群组邀请
        self.group_conversation_request = GroupConversationRequest.objects.create(
            from_user=self.user2,
            to_user=self.user3,
            group_conversation=self.group_conversation,
            message="Please join our group!",
            status=0  # Pending status
        )
        
        self.url = '/conversation/group/member/request/reject'

        self.correct_data = {
            "userName": "john_doe",
            "groupId": str(self.group_conversation.id),
            "inviteeName": "alice_doe"
        }

        self.headers = {
            "Authorization": generate_jwt_token(self.user1.name),
            "Content-Type": "application/json"
        }

    def test_reject_group_invitation_success(self):
        # 测试成功拒绝群组邀请
        response = self.client.post(self.url, data=json.dumps(self.correct_data), content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')
        self.group_conversation_request.refresh_from_db()
        self.assertEqual(self.group_conversation_request.status, 2)  # Rejected status

    def test_reject_group_invitation_bad_method(self):
        # 测试非POST请求
        response = self.client.get(self.url, headers=self.headers)
        self.assertEqual(response.status_code, 405)

    def test_reject_group_invitation_missing_fields(self):
        # 测试缺少字段的请求
        data = self.correct_data.copy()
        del data['inviteeName']
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Bad parameters', json.loads(response.content)['info'])

    def test_reject_group_invitation_group_not_found(self):
        # 测试群组不存在的情况
        data = self.correct_data.copy()
        data['groupId'] = -1
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Conversation not found', json.loads(response.content)['info'])

    def test_reject_group_invitation_user_not_found(self):
        # 测试用户不存在的情况
        data = self.correct_data.copy()
        data['userName'] = 'unknown_user'
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 403)
        self.assertIn('Permission denied', json.loads(response.content)['info'])

    def test_reject_group_invitation_no_invitation(self):
        # 测试没有对应的群组邀请
        self.group_conversation_request.delete()
        response = self.client.post(self.url, data=json.dumps(self.correct_data), content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Request not found', json.loads(response.content)['info'])

    def test_reject_group_invitation_invitation_already_rejected(self):
        # 测试邀请已被拒绝
        self.group_conversation_request.status = 2  # Rejected status
        self.group_conversation_request.save()
        response = self.client.post(self.url, data=json.dumps(self.correct_data), content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, 403)
        self.assertIn('Permission denied', json.loads(response.content)['info'])

class GetGroupInvitationListTestCase(TestCase):
    def setUp(self):
        # 创建测试用户和群组会话
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        self.user3 = User.objects.create(name='alice_doe', password='password')
        self.group_conversation = GroupConversation.objects.create(title='TestGroup', owner=self.user1)
        self.user1_group_conversation = UserGroupConversation.objects.create(user=self.user1, group_conversation=self.group_conversation, identity=2)
        
        # 创建群组邀请
        self.group_conversation_request = GroupConversationRequest.objects.create(
            from_user=self.user1,
            to_user=self.user3,
            group_conversation=self.group_conversation,
            message="Please join our group!",
            status=0  # Pending status
        )
        
        self.url = '/conversation/group/member/request'
        self.data = {
            'userName': 'john_doe',
            'groupId': self.group_conversation.id
        }

        self.headers = {
            "Authorization": generate_jwt_token(self.user1.name),
            "Content-Type": "application/json"
        }

    def test_get_group_invitation_list_success(self):
        # 测试成功获取群组邀请列表
        response = self.client.get(self.url, data=self.data, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')
        invitations = json.loads(response.content)['requests']
        self.assertEqual(len(invitations), 1)
        self.assertEqual(invitations[0]['fromUserName'], 'john_doe')

    def test_get_group_invitation_list_unauthenticated(self):
        # 测试未认证用户尝试获取群组邀请列表
        self.data['userName'] = 'jane_doe'
        response = self.client.get(self.url, data=self.data, headers=self.headers)
        self.assertEqual(response.status_code, 403)  # 或者应用中定义的其他适用状态码
