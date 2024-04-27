import json
from django.test import TestCase
from user.models import User
from friend.models import Friendship, FriendRequest, UserTag
from django.utils import timezone

class FriendProfileFixTestCase(TestCase):
    def setUp(self):
        # 设置测试用户和朋友
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        self.friendship = Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        self.user_tag = UserTag.objects.create(user=self.user1,  name='CollegeBuddy')
        self.user_tag.friendships.set([self.friendship])
        self.friendship.tags.set([self.user_tag])
        self.url = '/friend/fix/'
        self.correct_data = {
            "userName": "john_doe",
            "friendName": "jane_doe",
            "alias": "Jane",
            "description": "Best friend from college",
            "tag": "CollegeBuddy"
        }

    def test_fix_friend_profile_success(self):
        response = self.client.post(self.url, data=json.dumps(self.correct_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')

        self.assertEqual(Friendship.objects.get(from_user=self.user1, to_user=self.user2).alias, 'Jane')
        self.assertEqual(Friendship.objects.get(from_user=self.user1, to_user=self.user2).description, 'Best friend from college')
        self.assertEqual(UserTag.objects.filter(user=self.user1, name='CollegeBuddy').count(), 1)
        self.assertEqual([tag.name for tag in Friendship.objects.get(from_user=self.user1, to_user=self.user2).tags.all()], ['CollegeBuddy'])

    def test_fix_friend_profile_bad_method(self):
        # 测试非POST请求
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_fix_friend_profile_missing_fields(self):
        # 测试缺少字段的请求
        data = self.correct_data.copy()
        del data['alias']  # 删除一个必需字段
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Bad parameters', json.loads(response.content)['info'])

    def test_fix_friend_profile_friend_not_found(self):
        # 测试找不到朋友的情况
        data = self.correct_data.copy()
        data['friendName'] = 'unknown_person'
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('User not found', json.loads(response.content)['info'])

    def test_fix_friend_profile_new_tag(self):
        # 测试新增标签的情况
        data = self.correct_data.copy()
        data['tag'] = 'NewTag'
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')

        self.assertEqual(UserTag.objects.filter(user=self.user1, name='NewTag').count(), 1)

class FriendProfileFixAliasTestCase(TestCase):
    def setUp(self):
        # 设置测试用户和朋友
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        self.friendship = Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        self.user_tag = UserTag.objects.create(user=self.user1,  name='CollegeBuddy')
        self.user_tag.friendships.set([self.friendship])
        self.friendship.tags.set([self.user_tag])
        self.url = '/friend/fix/alias/'
        self.correct_data = {
            "userName": "john_doe",
            "friendName": "jane_doe",
            "alias": "Jane"
        }

    def test_fix_friend_profile_success(self):
        response = self.client.post(self.url, data=json.dumps(self.correct_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Alias not changed')

        self.assertEqual(Friendship.objects.get(from_user=self.user1, to_user=self.user2).alias, 'Jane')
        self.assertEqual(Friendship.objects.get(from_user=self.user1, to_user=self.user2).description, '')
        self.assertEqual(UserTag.objects.filter(user=self.user1, name='CollegeBuddy').count(), 1)
        self.assertEqual([tag.name for tag in Friendship.objects.get(from_user=self.user1, to_user=self.user2).tags.all()], ['CollegeBuddy'])

    def test_fix_friend_profile_bad_method(self):
        # 测试非POST请求
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_fix_friend_profile_missing_fields(self):
        # 测试缺少字段的请求
        data = self.correct_data.copy()
        del data['alias']  # 删除一个必需字段
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Bad parameters', json.loads(response.content)['info'])

    def test_fix_friend_profile_friend_not_found(self):
        # 测试找不到朋友的情况
        data = self.correct_data.copy()
        data['friendName'] = 'unknown_person'
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('User not found', json.loads(response.content)['info'])


class FriendProfileFixTagAddTestCase(TestCase):
    def setUp(self):
        # 设置测试用户和朋友
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        self.friendship = Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        self.user_tag = UserTag.objects.create(user=self.user1,  name='CollegeBuddy')
        self.user_tag.friendships.set([self.friendship])
        self.friendship.tags.set([self.user_tag])
        self.url = '/friend/fix/tag/add/'
        self.correct_data = {
            "userName": "john_doe",
            "friendName": "jane_doe",
            "tag": "classmate"
        }

    def test_add_friend_tag_success(self):
        response = self.client.post(self.url, data=json.dumps(self.correct_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(UserTag.objects.filter(user=self.user1, name='CollegeBuddy').count(), 1)
        self.assertEqual(UserTag.objects.filter(user=self.user1, name='classmate').count(), 1)
        self.assertEqual([tag.name for tag in Friendship.objects.get(from_user=self.user1, to_user=self.user2).tags.all()], ['CollegeBuddy', 'classmate'])

    def test_add_friend_tag_bad_method(self):
        # 测试非POST请求
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_add_friend_tag_missing_fields(self):
        # 测试缺少字段的请求
        data = self.correct_data.copy()
        del data['tag']  # 删除一个必需字段
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Bad parameters', json.loads(response.content)['info'])

    def test_add_friend_tag_friend_not_found(self):
        # 测试找不到朋友的情况
        data = self.correct_data.copy()
        data['friendName'] = 'unknown_person'
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('User not found', json.loads(response.content)['info'])

    def test_add_friend_tag_new_tag(self):
        # 测试新增重复标签的情况
        data = self.correct_data.copy()
        data['tag'] = 'CollegeBuddy'
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content)['code'], 2)
        self.assertEqual(json.loads(response.content)['info'], 'Tag already exists')

        self.assertEqual(UserTag.objects.filter(user=self.user1, name='CollegeBuddy').count(), 1)
        self.assertEqual(UserTag.objects.filter(user=self.user1, name='classmate').count(), 0)
        self.assertEqual([tag.name for tag in Friendship.objects.get(from_user=self.user1, to_user=self.user2).tags.all()], ['CollegeBuddy'])

    def test_add_friend_tag_empty_tag(self):
        # 测试新增空标签的情况
        data = self.correct_data.copy()
        data['tag'] = ''
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content)['code'], 3)
        self.assertEqual(json.loads(response.content)['info'], 'Tag empty')

        self.assertEqual(UserTag.objects.filter(user=self.user1, name='CollegeBuddy').count(), 1)
        self.assertEqual([tag.name for tag in Friendship.objects.get(from_user=self.user1, to_user=self.user2).tags.all()], ['CollegeBuddy'])

