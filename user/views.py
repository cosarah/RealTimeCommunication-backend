import json
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from user.models import User
from friend.models import FriendRequest, Friendship
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp
from utils.utils_jwt import generate_jwt_token, check_jwt_token

# return_field函数根据提供的字段列表过滤出所需数据


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
            return request_success({"token": generate_jwt_token(user_name)})
        else:
            return request_failed(2, "Wrong password", 401)
    else: # 否则新建用户（注册）
        return request_failed(1, "User do not exist", 401)
    
    return request_failed(-2, "Not implemented", 501)
# 重定位到聊天列表页

# 注册
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
    return request_failed(-2, "Not implemented", 501)
# 重定位到聊天列表页

# 获取用户个人信息
def get_user_info(req: HttpRequest):
    if req.method != "GET":
        return BAD_METHOD
    
    body = json.loads(req.body.decode("utf-8"))
    user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
    
    if not User.objects.filter(name=user_name).exists():
        return request_failed(1, "User do not exist", 401)
    
    # 查找数据库中对应用户，并返回其信息
    user = User.objects.get(name=user_name)
    
    # 返回用户信息
    user_info = {
        "userName": user.name,
        "nickName": user.nick_name,
        "gender": user.gender,
        "createTime": user.create_time,
        "phone": user.phone,
        "email": user.email,
        "portrait": user.portrait,
        "introduction": user.introduction,
        "birthday": user.birthday,
        "age": user.age,
        "location": user.location
    }
    return request_success(user_info)

# 修改用户个人信息
### TODO:修改用户密码
"""若为空，则不变，若有输入，则改变"""
def fix_user_info(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    # 请求体示例：{"userName": "Ashitemaru", "nickname": "Ashitemaru", "password": "123456", "phone": "12345678901", "email": "ashitemaru@gmail.com"}
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
    
    # 查找数据库中对应用户，并进行修改
    if not User.objects.filter(name=user_name).exists():
        return request_failed(1, "User do not exist", 401)
    user = User.objects.get(name=user_name)
    user.nick_name = nick_name
    user.phone = phone
    user.email = email
    user.gender = gender
    user.portrait = portrait
    user.introduction = introduction
    user.birthday = birthday
    user.age = age
    user.location = location
    user.save()
    return request_success({"token": generate_jwt_token(user_name)})

# 注销
def close(request: HttpRequest):
    if request.method != "POST":
        return BAD_METHOD
    else:
        body = json.loads(request.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        
        if not User.objects.filter(name=user_name).exists():
            return request_failed(1, "User do not exist", 401)
        user = User.objects.get(name=user_name)
        user.delete()
        return request_success({"info": "User closed","token": generate_jwt_token(user_name)})
# 重定位到登录页
    