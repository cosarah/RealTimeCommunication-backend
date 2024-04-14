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
############
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

# 获取用户信息
"""先检验是否为好友"""
def get_user_profile(req: HttpRequest):
    if req.method != "GET":
        return BAD_METHOD
    body = json.loads(req.body.decode("utf-8"))
    user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
    user = User.objects.get(name=user_name)
    user_find = User.objects.filter(name=user_name).values_list('id', flat=True)
    

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

def delete_friend(req: HttpRequest):
    return request_success({})