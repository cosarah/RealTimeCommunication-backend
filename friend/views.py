from django.shortcuts import render
import json
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from user.models import User
from friend.models import FriendRequest, Friendship, FriendRequestMessage
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp
from utils.utils_jwt import generate_jwt_token, check_jwt_token

# Create your views here.
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
            friend.friend_profile() for friend in friend_list
        ]
    }
    return request_success(return_data)

# 获取好友请求列表
def get_friend_request_list(req: HttpRequest):
    if req.method != "GET":
        return BAD_METHOD
    body = json.loads(req.body.decode("utf-8"))
    user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
    user = User.objects.get(name=user_name)
    friend_requests = FriendRequest.objects.filter(to_user=user)
    friend_applys = FriendRequest.objects.filter(from_user=user)
    return_data = {
        "requests": [
            return_field(friend_request.__str__(), ["fromUser","updateTime","updateMessage","status"]) for friend_request in friend_requests
        ],
        "applys": [
            return_field(friend_apply.__str__(), ["toUser","updateTime","updateMessage","status"]) for friend_apply in friend_applys
        ]
    }
    return request_success(return_data)

# 发送好友请求
def add_friend(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    # 格式：{"userName": "123", "friendName": "Sam", "message": "Hi"}
    body = json.loads(req.body.decode("utf-8"))
    user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
    friend_name = require(body, "friendName", "string", err_msg="Missing or error type of [friendName]")
    user = User.objects.get(name=user_name)
    friend = User.objects.get(name=friend_name)

    apply_message = require(body, "message", "string", err_msg="Missing or error type of [message]")
    if apply_message == "": apply_message = "你好，我是" + user.nick_name + "，很高兴认识你！" # 缺省值

    if Friendship.objects.filter(from_user=user, to_user=friend).exists(): # 已经是好友
        return request_failed(1, "Already friends", 403)
    
    if FriendRequest.objects.filter(from_user=friend, to_user=user).exists(): # 已经存在
        friend_request = FriendRequest.objects.get(from_user=friend, to_user=user)
        friend_request_message = FriendRequestMessage(request=friend_request, message=apply_message)
        friend_request._update_message_(apply_message)
        friend_request_message.save()
        return request_success({})
    else : # 创建新的好友请求
        friend_request = FriendRequest(from_user=friend, to_user=user, update_message=apply_message)
        friend_request_message = FriendRequestMessage(request=friend_request, message=apply_message)
        friend_request.save()
        friend_request_message.save()
        return request_success({})

# 接受好友请求
def accept_friend_request(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    body = json.loads(req.body.decode("utf-8"))
    user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
    friend_name = require(body, "applierName", "string", err_msg="Missing or error type of [friendName]")
    if FriendRequest.objects.filter(to_user=user_name, from_user=friend_name).exists():
        friend_request = FriendRequest.objects.get(to_user=user_name, from_user=friend_name)
        print(friend_request.accept())
        if friend_request.accept():
            return request_success({})
        else:
            return request_failed(1, "Friend request already accepted", 403)
    else:
        return request_failed(2, "Friend request not found", 403)

# 拒绝好友请求
def reject_friend_request(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    body = json.loads(req.body.decode("utf-8"))
    user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
    friend_name = require(body, "applierName", "string", err_msg="Missing or error type of [friendName]")
    if FriendRequest.objects.filter(to_user=user_name, from_user=friend_name).exists():
        friend_request = FriendRequest.objects.get(to_user=user_name, from_user=friend_name)
        if friend_request.reject():
            return request_success({})
        else:
            return request_failed(1, "Friend request already accepted or rejected", 403)
    else:
        return request_failed(2, "Friend request not found", 403)
    
# 获取好友信息
def get_friend_profile(req: HttpRequest):
    if req.method != "GET":
        return BAD_METHOD
    body = json.loads(req.body.decode("utf-8"))
    user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
    friend_name = require(body, "friendName", "string", err_msg="Missing or error type of [friendName]")
    user = User.objects.get(name=user_name)
    friend = User.objects.get(name=friend_name)
    friendship = Friendship.objects.get(from_user=user, to_user=friend)
    if friendship:
        return request_success(friendship.friend_profile())
    else:
        return request_failed(1, "Friend not foound", 403)

# 修改好友备注
def fix_friend_remark(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    body = json.loads(req.body.decode("utf-8"))
    user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
    friend_name = require(body, "friendName", "string", err_msg="Missing or error type of [friendName]")
    remark = require(body, "remark", "string", err_msg="Missing or error type of [remark]")
    tag = require(body, "tag", "string", err_msg="Missing or error type of [tag]")

    user = User.objects.get(name=user_name)
    friend = User.objects.get(name=friend_name)
    if Friendship.objects.filter(from_user=user, to_user=friend).exists():
        friendship = Friendship.objects.get(from_user=user, to_user=friend)
        if remark != "": friendship.remark = remark
        if tag != "": friendship.tag = tag
        friendship.save()
        return request_success({})
    else:
        return request_failed(1, "Friend not foound", 403)

############
# 删除好友
def delete_friend(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    body = json.loads(req.body.decode("utf-8"))
    user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
    friend_name = require(body, "friendName", "string", err_msg="Missing or error type of [friendName]")
    user = User.objects.get(name=user_name)
    friend = User.objects.get(name=friend_name)
    
    if Friendship.objects.filter(from_user=user, to_user=friend).exists():
        Friendship.objects.filter(from_user=user, to_user=friend).delete()
        return request_success({})
    else:
        return request_failed(1, "Friend not foound", 403)
### TODO:删除好友对聊天信息，好友请求的影响
### note:这是单方向的删除好友，这会对聊天造成影响，聊天时需要先检验对方是否仍是好友

# 搜索用户
### 搜索方式：姓名、邮箱、手机号（在修改个人信息中进行唯一性验证）
def get_user_profile(req: HttpRequest):
    if req.method != "GET":
        return BAD_METHOD
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        user = User.objects.get(name=user_name)

        keyword = require(body, "keyword", "string", err_msg="Missing or error type of [keyword]")
        info = require(body, "info", "string", err_msg="Missing or error type of [info]")
    except:
        return request_failed(0, "Missing or error type of request body", 403)

    if info == "name": # 按用户名搜索
        if User.objects.filter(name=keyword).exists():
            user_find = User.objects.get(name=keyword)
            if Friendship.objects.filter(from_user=user, to_user=user_find).exists():
                friend_profile = Friendship.objects.get(from_user=user, to_user=user_find).friend_profile()
                return_data = {
                    "is_friend": True,
                    "user_info": friend_profile,
                }
            else:
                return_data = {
                    "is_friend": False,
                    "user_info": user_find.__info__(),
                }
            return request_success(return_data)
        else:
            return request_failed(1, "User not found", 403)
    
    elif info == "email": # 按邮箱搜索
        if User.objects.filter(email=keyword).exists():
            user_find = User.objects.get(email=keyword)
            if Friendship.objects.filter(from_user=user, to_user=user_find).exists():
                friend_profile = Friendship.objects.get(from_user=user, to_user=user_find).friend_profile()
                return_data = {
                    "is_friend": True,
                    "user_info": friend_profile,
                }
            else:
                return_data = {
                    "is_friend": False,
                    "user_info": user_find.__info__(),
                }
            return request_success(return_data)
        else:
            return request_failed(1, "User not found", 403)
    
    elif info == "phone": # 按手机号搜索
        if User.objects.filter(phone=keyword).exists():
            user_find = User.objects.get(phone=keyword)
            if Friendship.objects.filter(from_user=user, to_user=user_find).exists():
                friend_profile = Friendship.objects.get(from_user=user, to_user=user_find).friend_profile()
                return_data = {
                    "is_friend": True,
                    "user_info": friend_profile,
                }
            else:
                return_data = {
                    "is_friend": False,
                    "user_info": user_find.__info__(),
                }
            return request_success(return_data)
        else:
            return request_failed(1, "User not found", 403)
    
    else:
        return request_failed(1, "Unknown info type", 403)

"""搜索好友应该在好友列表的前端模块中实现"""