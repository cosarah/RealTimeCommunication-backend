from django.shortcuts import render
import json
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from user.models import User
from friend.models import FriendRequest, Friendship, FriendRequestMessage, UserTag
from utils.utils_request import request_failed, request_success, return_field
from utils.utils_request import BAD_METHOD, BAD_PARAMS, USER_NOT_FOUND, ALREADY_EXIST, CREATE_SUCCESS, DELETE_SUCCESS, UPDATE_SUCCESS
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp
from utils.utils_jwt import generate_jwt_token, check_jwt_token

# Create your views here.
# 获取好友列表
def get_friend_list(req: HttpRequest):
    if req.method != "GET":
        return BAD_METHOD
    
    try:
        user_name = req.GET.get("userName")
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists():
        return USER_NOT_FOUND
    
    user = User.objects.get(name=user_name)
    friend_list = Friendship.objects.filter(from_user=user)

    return_data = {
        "friends": [
            friend.friend_profile() for friend in friend_list
        ]
    }
    return request_success(return_data)

# 获取好友请求列表
def get_friend_request_list(req: HttpRequest):
    if req.method != "GET":
        return BAD_METHOD
    try:
        user_name = req.GET.get("userName")
    except:
        return BAD_PARAMS
    if not User.objects.filter(name=user_name).exists():
        return USER_NOT_FOUND
    user = User.objects.get(name=user_name)
    friend_requests = FriendRequest.objects.filter(to_user=user)
    friend_applys = FriendRequest.objects.filter(from_user=user)
    requests_list = [friend_request.from_user_profile() for friend_request in friend_requests]
    applys_list = [friend_apply.to_user_profile() for friend_apply in friend_applys]
    return_data = {
        "requests": requests_list,
        "applys": applys_list
    }
    return request_success(return_data)

# 发送好友请求
def add_friend(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    # 格式：{"userName": "123", "friendName": "Sam", "message": "Hi"}
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        friend_name = require(body, "friendName", "string", err_msg="Missing or error type of [friendName]")
        apply_message = require(body, "message", "string", err_msg="Missing or error type of [message]")
    except:
        return BAD_PARAMS 
    user = User.objects.get(name=user_name)
    friend = User.objects.get(name=friend_name)
    if apply_message == "":
        apply_message = "你好，我是"+user.name+"，很高兴认识你。"

    if Friendship.objects.filter(from_user=user, to_user=friend).exists(): # 已经是好友
        return ALREADY_EXIST
    if FriendRequest.objects.filter(from_user=friend, to_user=user).exists(): # 对方申请已经存在
        return request_failed(1, "Please go to accept friend request", 403)
    if FriendRequest.objects.filter(from_user=user, to_user=friend).exists(): # 好友已经存在，支持继续发送申请
        friend_request = FriendRequest.objects.get(from_user=user, to_user=friend)
        friend_request_message = FriendRequestMessage(request=friend_request, message=apply_message)
        friend_request.update_message(apply_message) # 更新最新申请消息
        friend_request.status = 0 # 更新申请状态
        friend_request_message.save() 
        return request_success({})
    else : # 创建新的好友请求
        friend_request = FriendRequest(from_user=user, to_user=friend, updated_message=apply_message)
        friend_request_message = FriendRequestMessage(request=friend_request, message=apply_message)
        friend_request.save()
        friend_request_message.save()
        return request_success({})

# 接受好友请求
def accept_friend_request(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        friend_name = require(body, "friendName", "string", err_msg="Missing or error type of [friendName]")
    except:
        return BAD_PARAMS
    
    if FriendRequest.objects.filter(to_user=user_name, from_user=friend_name).exists():
        friend_request = FriendRequest.objects.get(to_user=user_name, from_user=friend_name)
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
    
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        friend_name = require(body, "friendName", "string", err_msg="Missing or error type of [friendName]")
    except:
        return BAD_PARAMS
        
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
    
    try:
        user_name = req.GET.get("userName")
        friend_name = req.GET.get("friendName")
    except:
        return BAD_PARAMS    
    
    user = User.objects.get(name=user_name)
    friend = User.objects.get(name=friend_name)
    friendship = Friendship.objects.get(from_user=user, to_user=friend)
    if friendship:
        return request_success(friendship.friend_profile())
    else:
        return request_failed(1, "Friend not found", 403)

# 修改好友备注
def fix_friend_alias(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        friend_name = require(body, "friendName", "string", err_msg="Missing or error type of [friendName]")
        alias = require(body, "alias", "string", err_msg="Missing or error type of [alias]")
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists():
        return USER_NOT_FOUND
    if not User.objects.filter(name=friend_name).exists():
        return USER_NOT_FOUND
    user = User.objects.get(name=user_name)
    friend = User.objects.get(name=friend_name)

    if not Friendship.objects.filter(from_user=user, to_user=friend).exists():
        return request_failed(1, "Friend not found", 403)
    
    friendship = Friendship.objects.get(from_user=user, to_user=friend)
    if alias != "": 
        friendship.set_alias(alias)
        return request_success()
    else: 
        request_success(info="Alias not changed")
        

def fix_friend_description(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        friend_name = require(body, "friendName", "string", err_msg="Missing or error type of [friendName]")
        description = require(body, "description", "string", err_msg="Missing or error type of [description]")
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists():
        return USER_NOT_FOUND
    if not User.objects.filter(name=friend_name).exists():
        return USER_NOT_FOUND
    user = User.objects.get(name=user_name)
    friend = User.objects.get(name=friend_name)

    if not Friendship.objects.filter(from_user=user, to_user=friend).exists():
        return request_failed(1, "Friend not found", 403)
    
    friendship = Friendship.objects.get(from_user=user, to_user=friend)
    if description != "": 
        friendship.set_description(description)
        return request_success()
    else: 
        request_success(info="Description not changed")
    
        

def add_friend_tag(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        friend_name = require(body, "friendName", "string", err_msg="Missing or error type of [friendName]")
        tag = require(body, "tag", "string", err_msg="Missing or error type of [tag]")
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists():
        return USER_NOT_FOUND
    if not User.objects.filter(name=friend_name).exists():
        return USER_NOT_FOUND
    user = User.objects.get(name=user_name)
    friend = User.objects.get(name=friend_name)

    if not Friendship.objects.filter(from_user=user, to_user=friend).exists():
        return request_failed(1, "Friend not found", 403)
    
    friendship = Friendship.objects.get(from_user=user, to_user=friend)
    
    if tag != "":
        if friendship.add_friend_tag(tag):
            return request_success()
        else:
            return request_failed(2, "Tag already exists", 403)
    else:
        return request_failed(3, "Tag empty", 403) # 之后可以改成不合规格式


def delete_friend_tag(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        friend_name = require(body, "friendName", "string", err_msg="Missing or error type of [friendName]")
        tag = require(body, "tag", "string", err_msg="Missing or error type of [tag]")
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists():
        return USER_NOT_FOUND
    if not User.objects.filter(name=friend_name).exists():
        return USER_NOT_FOUND
    user = User.objects.get(name=user_name)
    friend = User.objects.get(name=friend_name)

    if not Friendship.objects.filter(from_user=user, to_user=friend).exists():
        return request_failed(1, "Friend not found", 403)
    
    friendship = Friendship.objects.get(from_user=user, to_user=friend)
    if tag != "":
        if friendship.delete_friend_tag(tag):
            return request_success()
        else:
            return request_failed(2, "Tag not exist", 403)
    else:
        return request_failed(3, "Tag empty", 403) 


def fix_friend_profile(req:HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        friend_name = require(body, "friendName", "string", err_msg="Missing or error type of [friendName]")
        alias = require(body, "alias", "string", err_msg="Missing or error type of [alias]")
        description = require(body, "description", "string", err_msg="Missing or error type of [description]")
        tag = require(body, "tag", "string", err_msg="Missing or error type of [tag]")

    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists():
        return USER_NOT_FOUND
    if not User.objects.filter(name=friend_name).exists():
        return USER_NOT_FOUND
    
    user = User.objects.get(name=user_name)
    friend = User.objects.get(name=friend_name)

    if not Friendship.objects.filter(from_user=user, to_user=friend).exists():
        return request_failed(1, "Friend not found", 403)

    friendship = Friendship.objects.get(from_user=user, to_user=friend)
    if alias:
        friendship.set_alias(alias)
    if description: 
        friendship.set_description(description)
    if tag:
        friendship.delete_friend_tag(tag)
        friendship.add_friend_tag(tag)

    return request_success()

def get_user_tag(req: HttpRequest):
    if req.method != "GET":
        return BAD_METHOD
    
    try:
        user_name = req.GET.get("userName")
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists():
        return USER_NOT_FOUND
    
    user = User.objects.get(name=user_name)
    return_data = {"tags":[tag.__str__() for tag in user.user_tag.all()]}
    return request_success(return_data)

############
# 删除好友
def delete_friend(req: HttpRequest):
    if req.method != "POST":
        return BAD_METHOD
    
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        friend_name = require(body, "friendName", "string", err_msg="Missing or error type of [friendName]")
    except:
        return BAD_PARAMS 
    
    user = User.objects.get(name=user_name)
    friend = User.objects.get(name=friend_name)
    
    if Friendship.objects.filter(from_user=user, to_user=friend).exists():
        Friendship.objects.filter(from_user=user, to_user=friend).delete()
        return request_success({})
    else:
        return request_failed(1, "Friend not found", 403)
### TODO:删除好友对聊天信息，好友请求的影响
### note:这是单方向的删除好友，这会对聊天造成影响，聊天时需要先检验对方是否仍是好友

# 搜索用户
### 搜索方式：姓名、邮箱、手机号（在修改个人信息中进行唯一性验证）
def get_user_profile(req: HttpRequest):
    if req.method != "GET":
        return BAD_METHOD
    
    try:
        user_name = req.GET.get("userName")
        keyword = req.GET.get("keyword")
        info = req.GET.get("info")
    except:
        return request_failed(0, "Missing or error format of request body", 403)
    
    user = User.objects.get(name=user_name)
    if info == "name": # 按用户名搜索
        if User.objects.filter(name=keyword).exists():
            user_find = User.objects.get(name=keyword)
            if Friendship.objects.filter(from_user=user, to_user=user_find).exists():
                friend_profile = Friendship.objects.get(from_user=user, to_user=user_find).friend_profile()
                return_data = {
                    "isFriend": True,
                    "friendshipInfo": friend_profile,
                }
            else:
                return_data = {
                    "isFriend": False,
                    "friendshipInfo": user_find.__info__(),
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
                    "isFriend": True,
                    "friendshipInfo": friend_profile,
                }
            else:
                return_data = {
                    "isFriend": False,
                    "friendshipInfo": user_find.__info__(),
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
                    "isFriend": True,
                    "friendshipInfo": friend_profile,
                }
            else:
                return_data = {
                    "isFriend": False,
                    "friendshipInfo": user_find.__info__(),
                }
            return request_success(return_data)
        else:
            return request_failed(1, "User not found", 403)
    
    else:
        return request_failed(1, "Unknown info type", 403)

"""搜索好友应该在好友列表的前端模块中实现"""

def get_friend_all_tag_list(req: HttpRequest):
    if req.method != "GET":
        return BAD_METHOD
    
    try:
        user_name = req.GET.get("userName")
    except:
        return BAD_PARAMS
    
    if User.objects.filter(name=user_name).exists():
        user = User.objects.get(name=user_name)
        friend_groups = {tag.__str__():tag.__friends_info__() for tag in user.user_tag.all()}
        return request_success(friend_groups)
    else:
        return USER_NOT_FOUND
    
# def get_friend_list_by_tag(req: HttpRequest):
#     if req.method != "GET":
#         return BAD_METHOD
    
#     try:
#         user_name = req.GET.get("userName")
#         tag_name = req.GET.get("tagName")
#     except:
#         return BAD_PARAMS
    
#     if not User.objects.filter(name=user_name).exists():
#         return USER_NOT_FOUND
#     user = User.objects.get(name=user_name)
    
#     if UserTag.objects.filter(name=tag_name,user=user).exists():
#         tag = UserTag.objects.get(name=tag_name,user=user)
#         friend_list = tag.tag_friendship.all()
#         return_data = {
#             "tagName": tag.name,
#             "friends": [friend.friend_profile() for friend in friend_list]
#         }
#         return request_success(return_data)
#     else:
#         return request_failed(1, "Tag not found", 403)

        