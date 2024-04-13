import json
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.contrib.auth import logout
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
    user = User.objects.get(name=user_name)
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
    password = require(body, "password", "string", err_msg="Missing or error type of [password]")
    phone = require(body, "phone", "string", err_msg="Missing or error type of [phone]")
    email = require(body, "email", "string", err_msg="Missing or error type of [email]")
    gender_info = require(body, "gender", "string", err_msg="Missing or error type of [gender]") # gender为枚举类型
    if gender_info == "男":
        gender = (1,'男')
    elif gender_info == "女":
        gender = (2,'女')
    else:
        gender = (0,'未知')
    portrait = require(body, "portrait", "string", err_msg="Missing or error type of [portrait]")
    introduction = require(body, "introduction", "string", err_msg="Missing or error type of [introduction]")
    birthday = require(body, "birthday", "string", err_msg="Missing or error type of [birthday]")
    age = require(body, "age", "string", err_msg="Missing or error type of [age]")
    location = require(body, "location", "string", err_msg="Missing or error type of [location]")
    
    # 查找数据库中对应用户，并进行修改
    user = User.objects.get(name=user_name)
    user.nick_name = nick_name
    user.password = password
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

# 登出
def user_logout(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        # TODO:登出
        return redirect('/login/')  # 重定向到登录页
    else:
        return BAD_METHOD
# 重定位到登录页


# 获取好友列表
def get_friend_list(req: HttpRequest):
    if req.method != "GET":
        return BAD_METHOD
    
    body = json.loads(req.body.decode("utf-8")) 
    user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
    
    user = User.objects.get(name=user_name)
    friend_list = Friendship.objects.filter(from_user=user)

    return_data = {
        "friends_info": [
            friend.friend_info() for friend in friend_list
        ]
    }
    return request_success(return_data)

# 发送好友请求
def send_friend_request(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD

    body = json.loads(req.body.decode("utf-8"))
    user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
    friend_name = require(body, "friendName", "string", err_msg="Missing or error type of [friendName]")
    message = require(body, "message", "string", err_msg="Missing or error type of [message]")

    friend_request = FriendRequest(from_user=User.objects.get(name=user_name), to_user=User.objects.get(name=friend_name), apply_message=message, apply_time=get_timestamp(), status = 'pending')
    friend_request.save()
    return request_success({})

# 获取好友请求列表
def get_friend_request_list(req: HttpRequest, user_name: str):
    if req.method != "GET":
        return BAD_METHOD
    user = User.objects.get(name=user_name)
    friend_requests = FriendRequest.objects.filter(to_user=user).values_list('user__name', flat=True)
    return_data = {
        "requests": [
            return_field(user.serialize(), ["id", "name", "createdTime"]) for user in User.objects.filter(name__in=friend_requests)
        ]
    }
    return request_success(return_data)

def add_friend(req: HttpRequest, user_name: str, friend_name: str):
    if req.method != "POST":
        return BAD_METHOD
    user = User.objects.get(name=user_name)
    friend = User.objects.get(name=friend_name)
    apply_message = "你好，我是" + user.nick_name + "，很高兴认识你！"
    add_friend_request = FriendRequest(user=user, friend=friend, created_time=get_timestamp())
    add_friend_request.save()
    return request_success({})

# 接受好友请求
def accept_friend_request(req: HttpRequest, user_name: str):
    if req.method != "POST":
        return BAD_METHOD
    if not 0 < len(user_name) <= 50:
        return request_failed(-1, "Bad param [userName]", 400)
    if not User.objects.filter(name=user_name).exists():
        return request_failed(1, "User not found", 404)
    body = json.loads(req.body.decode("utf-8"))
    friend_name = require(body, "friendName", "string", err_msg="Missing or error type of [friendName]")
    if not 0 < len(friend_name) <= 50:
        return request_failed(-1, "Bad param [friendName]", 400)
    if not User.objects.filter(name=friend_name).exists():
        return request_failed(1, "Friend not found", 404)
    if not FriendRequest.objects.filter(user__name=user_name, friend__name=friend_name).exists():
        return request_failed(1, "Friend request not found", 404)
    friend_request = FriendRequest.objects.get(user__name=user_name, friend__name=friend_name)
    friendship = Friendship(user=User.objects.get(name=user_name), friend=User.objects.get(name=friend_name), created_time=get_timestamp())
    friendship.save()
    friend_request.delete()
    return request_success({})

# 搜索用户
def search_user(req: HttpRequest):
    if req.method != "GET":
        return BAD_METHOD
    params = req.GET
    keyword = require(params, "keyword", "string", err_msg="Missing or error type of [keyword]")
    if not 0 < len(keyword) <= MAX_CHAR_LENGTH:
        return request_failed(-1, "Bad param [keyword]", 400)
    users = User.objects.filter(name__icontains=keyword).order_by('-created_time')
    return_data = {
        "users": [
            return_field(user.serialize(), ["id", "name", "createdTime"]) for user in users
        ]
    }
    return request_success(return_data)

# 其他用户主页
def get_user_profile(req: HttpRequest, user_name: str):
    if req.method != "GET":
        return BAD_METHOD
    if not 0 < len(user_name) <= 50:
        return request_failed(-1, "Bad param [userName]", 400)
    if not User.objects.filter(name=user_name).exists():
        return request_failed(1, "User not found", 404)
    user = User.objects.get(name=user_name)
    profile = UserProfile.objects.filter(user=user).first()
    if profile:
        return request_success(return_field(profile.serialize(), ["id", "phone", "email"]))
    else:
        return request_success({})

# 好友主页
def get_friend_profile(req: HttpRequest, user_name: str, friend_name: str):
    if req.method != "GET":
        return BAD_METHOD
    if not 0 < len(user_name) <= 50: # 主页用户名
        return request_failed(-1, "Bad param [userName]", 400)
    if not User.objects.filter(name=user_name).exists():
        return request_failed(1, "User not found", 404)
    if not 0 < len(friend_name) <= 50: # 好友用户名
        return request_failed(-1, "Bad param [friendName]", 400)
    if not User.objects.filter(name=friend_name).exists():
        return request_failed(1, "Friend not found", 404)
    if not Friendship.objects.filter(user__name=user_name, friend__name=friend_name).exists():
        return request_failed(1, "Not friend", 403)
    user = User.objects.get(name=user_name)
    friend = User.objects.get(name=friend_name)
    friendship = Friendship.objects.get(from_user=user, to_user=friend)
    return request_success(return_field(friendship.serialize(), ["id", "createdTime"]))
    





# 发送消息
def send_message(req: HttpRequest, user_name: str, conversation_id: int):
    if req.method != "POST":
        return BAD_METHOD
    