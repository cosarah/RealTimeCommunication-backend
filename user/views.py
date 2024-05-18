import json
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from user.models import User
from friend.models import FriendRequest, Friendship
from utils.utils_request import request_failed, request_success, return_field
from utils.utils_request import BAD_METHOD, BAD_PARAMS, USER_NOT_FOUND, ALREADY_EXIST, CREATE_SUCCESS, DELETE_SUCCESS, UPDATE_SUCCESS, ALREADY_CLOSED
from utils.utils_require import  CheckRequire, require, MAX_CHAR_LENGTH, MAX_NAME_LENGTH, MAX_INFO_LENGTH
from utils.utils_time import get_timestamp
from datetime import datetime
from utils.utils_jwt import generate_jwt_token, check_jwt_token
import bcrypt

# return_field函数根据提供的字段列表过滤出所需数据
### TODO:验证数据格式
import re
PORTRAIT_TYPE = list(range(-1,11))
EMPTY_PORTRAIT = 0
SELF_DEFINED_PORTRAIT = -1
def validate_portrait_type(portrait_type):
    return portrait_type in PORTRAIT_TYPE

GENDER_TYPE = [0,1,2]
def validate_gender_type(gender_type):
    return gender_type in GENDER_TYPE

def validate_name(name): # 用户名密码都是只能有字母、数字、下划线、连字符组成的长度在[3,16]的字符串
    return re.match(r'^[a-zA-Z0-9_-]{3,16}$', name)

def validate_nick_name(nick_name):
    # 群名、群昵称、个人昵称、好友备注名限制
    return len(nick_name) <= MAX_NAME_LENGTH

def validate_password(password):
    return re.match(r'^[a-zA-Z0-9_-]{3,16}$', password)

def validate_phone(phone):
    # 期望的电话号码格式为以1开头的11位数字
    return re.match(r'^1\d{10}$', phone)

def validate_email(email):
    # var: 单词字符、点、连字符、下划线
    # 简单的电子邮件格式验证：var@var.var
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

def validate_birthday(birthday):
    # 期望的出生日期格式为YYYY-MM-DD
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', birthday):
        return False
    
    try:
        # 尝试将字符串转换为日期对象，这也会检查月份和日期的有效性
        date_obj = datetime.strptime(birthday, '%Y-%m-%d')
    except ValueError:
        # 如果转换失败，则说明日期无效
        return False
    
    if datetime.strptime(birthday, "%Y-%m-%d") > datetime.now():
        return False
    
    return True

def validate_age(age):
    # 年龄应该是一个正整数
    return int(age) > 0

# 位置、个人简介、好友申请、群申请消息长度
def validate_info_length(introduction):
    # 一个简单的非空字符串
    return len(introduction) <= MAX_INFO_LENGTH


# 登录
@CheckRequire
def login(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD # request_failed(-3, "Bad method", 405)
    
    # Request body example: {"username": "Ashitemaru", "password": "123456"}
    body = json.loads(req.body.decode("utf-8"))
    user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
    password = require(body, "password", "string", err_msg="Missing or error type of [password]")

    # 若用户不存在或已注销
    if not User.objects.filter(name=user_name).exists() or User.objects.filter(name=user_name, is_closed=True).exists(): 
        return USER_NOT_FOUND

    user = User.objects.get(name=user_name) # 获取用户名对应的用户实例
    if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')): # 核验密码正确性
        user.login()
        return request_success({"token": generate_jwt_token(user_name)})
    else:
        return request_failed(2, "Wrong password", 401)
    
# 重定位到聊天列表页

# 注册
@CheckRequire
def register(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        password = require(body, "password", "string", err_msg="Missing or error type of [password]")
    except:
        return BAD_PARAMS
    
    if not validate_name(user_name) or not validate_password(password):
        return BAD_PARAMS
    
    if User.objects.filter(name=user_name).exists():
        return ALREADY_EXIST
    else:
        # 密码加密
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        hashed_password = hashed.decode('utf-8')

        user = User(name=user_name, password=hashed_password, nick_name=user_name)
        user.save()
        return request_success() # 注册成功并不返回token，因为token需要登录后才能获取


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
        return USER_NOT_FOUND
    if User.objects.filter(name=user_name, is_closed=True).exists():
        return ALREADY_CLOSED
    
    # 查找数据库中对应用户，并返回其信息
    user = User.objects.get(name=user_name)
    
    # 返回用户信息与令牌
    return_data = user.__all_info__()
    return_data["token"] = generate_jwt_token(user_name)
    return request_success(return_data)

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
        
        portrait = require(body, "portrait", "string", err_msg="Missing or error type of [portrait]")
        introduction = require(body, "introduction", "string", err_msg="Missing or error type of [introduction]")
        birthday = require(body, "birthday", "string", err_msg="Missing or error type of [birthday]")
        age = require(body, "age", "int", err_msg="Missing or error type of [age]")
        location = require(body, "location", "string", err_msg="Missing or error type of [location]")
    except:
        return BAD_PARAMS
    
    # 查找数据库中对应用户，并进行修改
    if not User.objects.filter(name=user_name).exists():
        return USER_NOT_FOUND
    user = User.objects.get(name=user_name)
    if user.is_closed == True:
        return ALREADY_CLOSED

    # 核验数据格式
    if nick_name:
        if validate_nick_name(nick_name): # 若有输入，则改变昵称
            user.nick_name = nick_name
        else:
            return request_failed(1, "Invalid nickname")
    if phone: 
        if validate_phone(phone): # 若有输入，则改变手机号
            user.phone = phone
        else:
            return request_failed(2, "Invalid phone number")
            
    if email:
        if validate_email(email): # 若有输入，则改变邮箱
            user.email = email
        else:
            return request_failed(3, "Invalid email address")
    
    if gender_info == "male":
        gender = 1
    elif gender_info == "female":
        gender = 2
    elif gender_info == "":
        gender = ""
    else:
        gender = 0
    if gender:
        user.gender = gender

    if introduction:
        if validate_info_length(introduction): # 若有输入，则改变简介
            user.introduction = introduction
        else:
            return request_failed(4, "Invalid introduction")

    if birthday:
        if validate_birthday(birthday): # 若有输入，则改变生日
            user.birthday = birthday
        else:
            return request_failed(5, "Invalid birthday")
    if age:
        if validate_age(age): # 若有输入，则改变年龄
            user.age = age
        else:    
            return request_failed(6, "Invalid age")
    if location:
        if validate_info_length(location): # 若有输入，则改变位置
            user.location = location
        else:
            return request_failed(7, "Invalid location")
    user.save()
    return request_success({"token": generate_jwt_token(user_name)})

def fix_password(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        old_password = require(body, "oldPassword", "string", err_msg="Missing or error type of [oldPassword]")
        new_password = require(body, "newPassword", "string", err_msg="Missing or error type of [newPassword]")
    except:
        return request_failed(0, "Missing or error type of [userName]", 400)

    if not validate_password(new_password):
        return request_failed(1, "Invalid password", 400)
    # 查找数据库中对应用户，并进行修改
    if not User.objects.filter(name=user_name).exists():
        return USER_NOT_FOUND
    user = User.objects.get(name=user_name)
    if user.is_closed == True:
        return ALREADY_CLOSED
    if bcrypt.checkpw(old_password.encode('utf-8'), user.password.encode('utf-8')):
        # 修改密码
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        hashed_password = hashed.decode('utf-8')
        user.password = hashed_password
        user.save()
        return request_success({"token": generate_jwt_token(user_name)})
    else:
        return request_failed(2, "Wrong password", 401)

def fix_portrait(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        portrait_type = require(body, "portraitType", "int", err_msg="Missing or error type of [portraitType]")
        portrait_code = require(body, "portraitCode", "string", err_msg="Missing or error type of [portraitCode]")
    except:
        return BAD_PARAMS

    if not User.objects.filter(name=user_name).exists() or User.objects.get(name=user_name).is_closed == True:
        return USER_NOT_FOUND
    
    user = User.objects.get(name=user_name)
    if not validate_portrait_type(portrait_type): # 不允许为空
        return BAD_PARAMS
    
    user.portrait_type = portrait_type
    if portrait_type == -1:
        if len(portrait_code) >= MAX_CHAR_LENGTH:
            return BAD_PARAMS
        user.portrait = portrait_code
    user.save()
    return request_success({"token": generate_jwt_token(user_name), "portraitType": portrait_type, "portraitCode": portrait_code})

# 注销
@CheckRequire
def close(request: HttpRequest):
    if request.method != "POST":
        return BAD_METHOD
    try:
        body = json.loads(request.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists():
        return USER_NOT_FOUND
    user = User.objects.get(name=user_name)
    if user.is_closed == True:
        return ALREADY_CLOSED
    user.close()
    return request_success(info="User closed")
# 重定位到登录页

@CheckRequire
def logout(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists():
        return USER_NOT_FOUND
    user = User.objects.get(name=user_name)
    if user.is_closed == True:
        return ALREADY_CLOSED
    if user.logout():
        return request_success(info="Logout succeed")
    else:
        return request_failed(1, "User not logged in", 401)
