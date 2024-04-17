import json
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from user.models import User
from friend.models import FriendRequest, Friendship
from utils.utils_request import request_failed, request_success, return_field
from utils.utils_request import BAD_METHOD, BAD_PARAMS, USER_NOT_FOUND, ALREADY_EXIST, CREATE_SUCCESS, DELETE_SUCCESS, UPDATE_SUCCESS
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp
from utils.utils_jwt import generate_jwt_token, check_jwt_token

# return_field函数根据提供的字段列表过滤出所需数据
### TODO:验证数据格式

# 登录
@CheckRequire
def login(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD # request_failed(-3, "Bad method", 405)
    
    # Request body example: {"username": "Ashitemaru", "password": "123456"}
    body = json.loads(req.body.decode("utf-8"))
    user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
    password = require(body, "password", "string", err_msg="Missing or error type of [password]")

    if User.objects.filter(name=user_name).exists(): # 若用户存在
        user = User.objects.get(name=user_name) # 获取用户名对应的用户实例
        if user.password == password: # 判断密码是否正确
            user.__login__()
            return request_success({"token": generate_jwt_token(user_name)})
        else:
            return request_failed(2, "Wrong password", 401)
    else: # 否则新建用户（注册）
        return request_failed(1, "User not exist", 401)
    
# 重定位到聊天列表页

# 注册
@CheckRequire
def register(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    body = json.loads(req.body.decode("utf-8"))
    user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
    password = require(body, "password", "string", err_msg="Missing or error type of [password]")
    # print(user_name, password)
    if User.objects.filter(name=user_name).exists():
        return request_failed(1, "User already exists", 409)
    else:
        user = User(name=user_name, password=password)
        user.save()
        return request_success({"token": generate_jwt_token(user_name)})
# 重定位到聊天列表页

# 获取用户个人信息
@CheckRequire
def get_user_info(req: HttpRequest):
    if req.method != "GET":
        return BAD_METHOD
    
    try:
        user_name = req.GET.get('userName', None)
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists():
        return request_failed(1, "User not exist", 401)
    
    # 查找数据库中对应用户，并返回其信息
    user = User.objects.get(name=user_name)
    # 返回用户信息
    return request_success(user.__all_info__())

# 修改用户个人信息
### TODO:修改用户密码
# 姓名、邮箱、手机号（在修改个人信息中进行唯一性验证）
"""若为空，则不变，若有输入，则改变"""
"""{
  "userName": "JohnDoe",
  "nickName": "Johnny",
  "password": "password123",
  "phone": "1234567890",
  "email": "john.doe@example.com",
  "gender": "male",
  "portrait": "https://example.com/profile_picture.jpg",
  "introduction": "Hello, I'm John Doe.",
  "birthday": "1990-01-01",
  "age": "34",
  "location": "New York"
}"""
@CheckRequire
def fix_user_info(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    try:
        body = json.loads(req.body.decode("utf-8")) 
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]") # 不可修改
        nick_name = require(body, "nickName", "string", err_msg="Missing or error type of [nickname]")
        phone = require(body, "phone", "string", err_msg="Missing or error type of [phone]")
        email = require(body, "email", "string", err_msg="Missing or error type of [email]")
        gender_info = require(body, "gender", "string", err_msg="Missing or error type of [gender]") # gender为枚举类型
        if gender_info == "male" or gender_info == "男":
            gender = 1
        elif gender_info == "female" or gender_info == "女":
            gender = 2
        else:
            gender = 0
        portrait = require(body, "portrait", "string", err_msg="Missing or error type of [portrait]")
        introduction = require(body, "introduction", "string", err_msg="Missing or error type of [introduction]")
        birthday = require(body, "birthday", "string", err_msg="Missing or error type of [birthday]")
        age = require(body, "age", "string", err_msg="Missing or error type of [age]")
        location = require(body, "location", "string", err_msg="Missing or error type of [location]")
    except:
        return request_failed(0, "Missing or error type of [userName]", 400)

    # 查找数据库中对应用户，并进行修改
    if not User.objects.filter(name=user_name).exists():
        return request_failed(1, "User not exist", 401)
    user = User.objects.get(name=user_name)
    if nick_name: user.nick_name = nick_name
    if phone: user.phone = phone
    if email: user.email = email
    if gender: user.gender = gender
    if portrait: user.portrait = portrait
    if introduction: user.introduction = introduction
    if birthday: user.birthday = birthday
    if age: user.age = age
    if location: user.location = location
    user.save()
    return request_success({"token": generate_jwt_token(user_name)})

# 注销
@CheckRequire
def close(request: HttpRequest):
    if request.method != "POST":
        return BAD_METHOD
    else:
        body = json.loads(request.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        
        if not User.objects.filter(name=user_name).exists():
            return request_failed(1, "User not exist", 401)
        user = User.objects.get(name=user_name)
        user.delete()
        return request_success({"info": "User closed","token": generate_jwt_token(user_name)})
# 重定位到登录页
