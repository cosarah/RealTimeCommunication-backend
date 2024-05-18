import json
from django.test import TestCase
from user.models import User
from friend.models import Friendship, FriendRequest, UserTag
from utils.utils_jwt import generate_jwt_token

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
        self.headers = {
            "Authorization": generate_jwt_token(self.user1.name),
            "Content-Type": "application/json"
        }
        self.token=generate_jwt_token(self.user1.name)

    def test_fix_friend_profile_success_new_tag(self):
        # 测试新增标签的情况
        data = self.correct_data.copy()
        data['tag'] = 'NewTag'
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')

        self.assertEqual(Friendship.objects.get(from_user=self.user1, to_user=self.user2).alias, 'Jane')
        self.assertEqual(Friendship.objects.get(from_user=self.user1, to_user=self.user2).description, 'Best friend from college')
        self.assertEqual([tag.name for tag in Friendship.objects.get(from_user=self.user1, to_user=self.user2).tags.all()], ['CollegeBuddy', 'NewTag'])
        self.assertEqual(UserTag.objects.filter(user=self.user1, name='NewTag').count(), 1)
        self.assertEqual(UserTag.objects.get(user=self.user1, name='NewTag').friendships.count(), 1)
        self.assertEqual(UserTag.objects.get(user=self.user1, name='NewTag').friendships.first(), self.friendship)

    def test_fix_friend_profile_success_delete_tag(self):
        # 测试删除标签的情况
        response = self.client.post(self.url, data=json.dumps(self.correct_data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')

        self.assertEqual(Friendship.objects.get(from_user=self.user1, to_user=self.user2).alias, 'Jane')
        self.assertEqual(Friendship.objects.get(from_user=self.user1, to_user=self.user2).description, 'Best friend from college')
        self.assertEqual(UserTag.objects.filter(user=self.user1, name='CollegeBuddy').count(), 1)
        self.assertEqual([friendship.from_user.name for friendship in UserTag.objects.get(user=self.user1, name='CollegeBuddy').friendships.all()], [])

        self.assertEqual([tag.name for tag in Friendship.objects.get(from_user=self.user1, to_user=self.user2).tags.all()], [])
        self.assertEqual(UserTag.objects.filter(user=self.user1, name='CollegeBuddy').exists(), True)
        self.assertEqual(UserTag.objects.get(user=self.user1, name='CollegeBuddy').friendships.count(), 0)

    def test_fix_friend_profile_bad_method(self):
        # 测试非POST请求
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_fix_friend_profile_missing_fields(self):
        # 测试缺少字段的请求
        data = self.correct_data.copy()
        del data['alias']  # 删除一个必需字段
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Bad parameters', json.loads(response.content)['info'])

    def test_fix_friend_profile_friend_not_found(self):
        # 测试找不到朋友的情况
        data = self.correct_data.copy()
        data['friendName'] = 'unknown_person'
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 404)
        self.assertIn('User not found', json.loads(response.content)['info'])

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
        self.headers = {
            "Authorization": generate_jwt_token(self.user1.name),
            "Content-Type": "application/json"
        }
        self.token=generate_jwt_token(self.user1.name)


    def test_fix_friend_profile_success(self):
        response = self.client.post(self.url, data=json.dumps(self.correct_data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')

        self.assertEqual(Friendship.objects.get(from_user=self.user1, to_user=self.user2).alias, 'Jane')
        self.assertEqual(Friendship.objects.get(from_user=self.user1, to_user=self.user2).description, None)
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
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Bad parameters', json.loads(response.content)['info'])

    def test_fix_friend_profile_friend_not_found(self):
        # 测试找不到朋友的情况
        data = self.correct_data.copy()
        data['friendName'] = 'unknown_person'
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 404)
        self.assertIn('User not found', json.loads(response.content)['info'])

class FriendProfileFixDescriptionTestCase(TestCase):
    def setUp(self):
        # 设置测试用户和朋友
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        self.friendship = Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        self.user_tag = UserTag.objects.create(user=self.user1,  name='CollegeBuddy')
        self.user_tag.friendships.set([self.friendship])
        self.friendship.tags.set([self.user_tag])
        self.url = '/friend/fix/description/'
        self.correct_data = {
            "userName": "john_doe",
            "friendName": "jane_doe",
            "description": "Best friend from college"
        }
        self.headers = {
            "Authorization": generate_jwt_token(self.user1.name),
            "Content-Type": "application/json"
        }
        self.token=generate_jwt_token(self.user1.name)


    def test_fix_friend_profile_success(self):
        response = self.client.post(self.url, data=json.dumps(self.correct_data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['code'], 0)
        self.assertEqual(json.loads(response.content)['info'], 'Succeed')

        self.assertEqual(Friendship.objects.get(from_user=self.user1, to_user=self.user2).alias, None)
        self.assertEqual(Friendship.objects.get(from_user=self.user1, to_user=self.user2).description, 'Best friend from college')
        self.assertEqual(UserTag.objects.filter(user=self.user1, name='CollegeBuddy').count(), 1)
        self.assertEqual([tag.name for tag in Friendship.objects.get(from_user=self.user1, to_user=self.user2).tags.all()], ['CollegeBuddy'])

    def test_fix_friend_profile_bad_method(self):
        # 测试非POST请求
        response = self.client.get(self.url, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 405)

    def test_fix_friend_profile_missing_fields(self):
        # 测试缺少字段的请求
        data = self.correct_data.copy()
        del data['description']  # 删除一个必需字段
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Bad parameters', json.loads(response.content)['info'])

    def test_fix_friend_profile_friend_not_found(self):
        # 测试找不到朋友的情况
        data = self.correct_data.copy()
        data['friendName'] = 'unknown_person'
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
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
        self.headers = {
            "Authorization": generate_jwt_token(self.user1.name),
            "Content-Type": "application/json"
        }
        self.token=generate_jwt_token(self.user1.name)

    def test_add_friend_tag_success(self):
        response = self.client.post(self.url, data=json.dumps(self.correct_data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
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
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Bad parameters', json.loads(response.content)['info'])

    def test_add_friend_tag_friend_not_found(self):
        # 测试找不到朋友的情况
        data = self.correct_data.copy()
        data['friendName'] = 'unknown_person'
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 404)
        self.assertIn('User not found', json.loads(response.content)['info'])

    def test_add_friend_tag_new_tag(self):
        # 测试新增重复标签的情况
        data = self.correct_data.copy()
        data['tag'] = 'CollegeBuddy'
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content)['code'], 2)
        self.assertEqual(json.loads(response.content)['info'], 'Tag already exists')

        self.assertEqual(UserTag.objects.filter(user=self.user1, name='CollegeBuddy').count(), 1)
        self.assertEqual(UserTag.objects.filter(user=self.user1, name='classmate').count(), 0)
        self.assertEqual([tag.name for tag in Friendship.objects.get(from_user=self.user1, to_user=self.user2).tags.all()], ['CollegeBuddy'])

    def test_add_delete_add_friend_tag(self):
        # 测试删除标签后再添加的情况
        data = self.correct_data.copy()
        data['tag'] = 'classmate'
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/friend/fix/tag/delete/', data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(UserTag.objects.filter(user=self.user1, name='classmate').count(), 1)
        self.assertEqual([tag.name for tag in Friendship.objects.get(from_user=self.user1, to_user=self.user2).tags.all()], ['CollegeBuddy'])
        self.assertNotIn('classmate', [tag.name for tag in Friendship.objects.get(from_user=self.user1, to_user=self.user2).tags.all()])

        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 200)



    def test_add_friend_tag_empty_tag(self):
        # 测试新增空标签的情况
        data = self.correct_data.copy()
        data['tag'] = ''
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content)['code'], 3)
        self.assertEqual(json.loads(response.content)['info'], 'Tag empty')

        self.assertEqual(UserTag.objects.filter(user=self.user1, name='CollegeBuddy').count(), 1)
        self.assertEqual([tag.name for tag in Friendship.objects.get(from_user=self.user1, to_user=self.user2).tags.all()], ['CollegeBuddy'])

class FriendProfileFixTagDeleteTestCase(TestCase):
    def setUp(self):
        # 设置测试用户和朋友
        self.user1 = User.objects.create(name='john_doe', password='password')
        self.user2 = User.objects.create(name='jane_doe', password='password')
        self.friendship = Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        self.user_tag = UserTag.objects.create(user=self.user1,  name='CollegeBuddy')
        self.user_tag.friendships.set([self.friendship])
        self.friendship.tags.set([self.user_tag])
        self.url = '/friend/fix/tag/delete/'
        self.correct_data = {
            "userName": "john_doe",
            "friendName": "jane_doe",
            "tag": "CollegeBuddy"
        }
        self.headers = {
            "Authorization": generate_jwt_token(self.user1.name),
            "Content-Type": "application/json"
        }
        self.token=generate_jwt_token(self.user1.name)

    def test_delete_friend_tag_success(self):
        response = self.client.post(self.url, data=json.dumps(self.correct_data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(UserTag.objects.filter(user=self.user1, name='CollegeBuddy').count(), 1)
        self.assertEqual([tag.name for tag in Friendship.objects.get(from_user=self.user1, to_user=self.user2).tags.all()], [])
        self.assertEqual(Friendship.objects.get(from_user=self.user1, to_user=self.user2).tags.count(), 0)
        self.assertEqual(UserTag.objects.filter(user=self.user1, name='CollegeBuddy').exists(), True)

    def test_delete_friend_tag_bad_method(self):
        # 测试非POST请求
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_delete_friend_tag_missing_fields(self):
        # 测试缺少字段的请求
        data = self.correct_data.copy()
        del data['tag']  # 删除一个必需字段
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Bad parameters', json.loads(response.content)['info'])

    def test_delete_friend_tag_friend_not_found(self):
        # 测试找不到朋友的情况
        data = self.correct_data.copy()
        data['friendName'] = 'unknown_person'
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, 404)
        self.assertIn('User not found', json.loads(response.content)['info'])

    def test_delete_friend_tag_tag_not_found(self):
        # 测试找不到标签的情况
        data = self.correct_data.copy()
        data['tag'] = 'unknown_tag'
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content)['code'], 2)
        self.assertEqual(json.loads(response.content)['info'], 'Tag not exist')

        self.assertEqual(UserTag.objects.filter(user=self.user1, name='CollegeBuddy').count(), 1)
        self.assertEqual([tag.name for tag in Friendship.objects.get(from_user=self.user1, to_user=self.user2).tags.all()], ['CollegeBuddy'])
        
    def test_delete_friend_tag_tag_empty(self):
        # 测试删除不属于自己的标签的情况
        data = self.correct_data.copy()
        data['tag'] = ''
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION=self.token)
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content)['code'], 3)
        self.assertEqual(json.loads(response.content)['info'], 'Tag empty')
        self.assertEqual(UserTag.objects.filter(user=self.user1, name='CollegeBuddy').exists(), True)


