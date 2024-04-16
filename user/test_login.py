import pytest
import json
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.utils import timezone
from user.models import User
from user.views import login, register, get_user_info, fix_user_info, close
from utils.utils_require import MAX_CHAR_LENGTH

# 获取自定义用户模型
User = get_user_model()

# # 测试User模型
# def test_user_model():
#     # 测试字段
#     assert User.name.max_length ==  MAX_CHAR_LENGTH # 假设MAX_CHAR_LENGTH为30
#     assert User.nick_name.max_length == MAX_CHAR_LENGTH
#     assert User.password.max_length == MAX_CHAR_LENGTH
#     assert User.phone.max_length == 11
#     assert User.email.max_length == 100
#     assert User.portrait.max_length == 200
#     assert User.introduction.max_length == 250

#     # 测试默认值
#     assert User.GENDER_CHOICES == [(0, '女'), (1, '男'), (2, '未知')]

# # 测试登录视图
# def test_login():
#     # 测试正常登录
#     request = HttpRequest()
#     request.method = 'POST'
#     request.body = json.dumps({"userName": "testuser", "password": "testpassword"}).encode('utf-8')
#     response = login(request)
#     assert response.status_code == 200
#     token = response.json()['token']
#     assert token

#     # 测试错误的密码
#     request.body = json.dumps({"userName": "testuser", "password": "wrongpassword"}).encode('utf-8')
#     response = login(request)
#     assert response.status_code == 401

#     # 测试用户不存在
#     request.body = json.dumps({"userName": "nonexistent", "password": "testpassword"}).encode('utf-8')
#     response = login(request)
#     assert response.status_code == 401

# # 测试注册视图
# def test_register():
#     # 测试正常注册
#     request = HttpRequest()
#     request.method = 'POST'
#     request.body = json.dumps({"userName": "newuser", "password": "newpassword"}).encode('utf-8')
#     response = register(request)
#     assert response.status_code == 200

#     # 测试用户名已存在
#     request.body = json.dumps({"userName": "testuser", "password": "newpassword"}).encode('utf-8')
#     response = register(request)
#     assert response.status_code == 409

# # 测试获取用户信息视图
# def test_get_user_info():
#     # 测试获取已存在的用户信息
#     request = HttpRequest()
#     request.method = 'GET'
#     request.body = json.dumps({"userName": "testuser"}).encode('utf-8')
#     response = get_user_info(request)
#     assert response.status_code == 200
#     user_info = response.json()
#     assert user_info['userName'] == "testuser"

#     # 测试获取不存在的用户信息
#     request.body = json.dumps({"userName": "nonexistent"}).encode('utf-8')
#     response = get_user_info(request)
#     assert response.status_code == 401

# # 测试修改用户信息视图
# def test_fix_user_info():
#     # 测试修改已存在的用户信息
#     request = HttpRequest()
#     request.method = 'POST'
#     request.body = json.dumps({
#         "userName": "testuser",
#         "nickName": "newnickname",
#         "phone": "12345678901",
#         "email": "testuser@example.com",
#         "gender": "male",
#         "portrait": "http://example.com/portrait.jpg",
#         "introduction": "New introduction",
#         "birthday": "1990-01-01",
#         "age": "30",
#         "location": "New location"
#     }).encode('utf-8')
#     response = fix_user_info(request)
#     assert response.status_code == 200

#     # 测试修改不存在的用户信息
#     request.body = json.dumps({
#         "userName": "nonexistent",
#         "nickName": "newnickname"
#     }).encode('utf-8')
#     response = fix_user_info(request)
#     assert response.status_code == 401

# # 测试注销视图
# def test_close():
#     # 测试注销已存在的用户
#     request = HttpRequest()
#     request.method = 'POST'
#     request.body = json.dumps({"userName": "testuser"}).encode('utf-8')
#     response = close(request)
#     assert response.status_code == 200
#     info = response.json()
#     assert info['info'] == "User closed"

#     # 测试注销不存在的用户
#     request.body = json.dumps({"userName": "nonexistent"}).encode('utf-8')
#     response = close(request)
#     assert response.status_code == 401