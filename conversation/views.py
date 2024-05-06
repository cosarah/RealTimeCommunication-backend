from django.shortcuts import render
import json
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from user.models import User
from friend.models import Friendship
from conversation.models import PrivateConversation, PrivateMessage ,GroupConversation, UserPrivateConversation, UserGroupConversation
from utils.utils_request import request_failed, request_success, return_field
from utils.utils_request import BAD_METHOD, BAD_PARAMS, USER_NOT_FOUND, ALREADY_EXIST, CREATE_SUCCESS, DELETE_SUCCESS, UPDATE_SUCCESS, FRIENDSHIP_NOT_FOUND, CONVERSATION_NOT_FOUND, MESSAGE_NOT_FOUND
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp
from utils.utils_jwt import generate_jwt_token, check_jwt_token

# Create your views here.
# 每次返回的都是按照更新时间排序的表单
def get_private_conversation_list(req: HttpRequest):
    if req.method != 'GET':
        return BAD_METHOD
    
    try:
        user_name = req.GET.get('userName')
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists():
        return USER_NOT_FOUND
    
    user = User.objects.get(name=user_name)

    private_conversations = UserPrivateConversation.objects.filter(user=user)
    conversation_list = []
    for private_conversation in private_conversations:
        conversation_list.append(private_conversation.serialize())
    
    return request_success(data={'privateConversationList': conversation_list})

def get_private_message_list(req: HttpRequest):
    if req.method != 'GET':
        return BAD_METHOD
    
    try:
        user_name = req.GET.get('userName')
        friend_name = req.GET.get('friendName')
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists() or not User.objects.filter(name=friend_name).exists():
        return USER_NOT_FOUND
    
    user = User.objects.get(name=user_name)
    friend = User.objects.get(name=friend_name)
    if PrivateConversation.objects.filter(user1=user,user2=friend).exists(): # 若不存在，则创建之
        private_conversation = PrivateConversation.objects.get(user1=user,user2=friend_name)
    elif PrivateConversation.objects.filter(user1=friend,user2=user).exists():
        private_conversation = PrivateConversation.objects.get(user1=friend,user2=user)
    else:
        private_conversation = PrivateConversation.objects.create(user1=user,user2=friend)    
    
    if not UserPrivateConversation.objects.filter(user=user,conversation=private_conversation).exists():
        user_private_conversation = UserPrivateConversation.objects.create(user=user,conversation=private_conversation)
    else:
        user_private_conversation = UserPrivateConversation.objects.get(user=user,conversation=private_conversation)
    user_private_conversation.read()
    return request_success(data={'messageList': private_conversation.get_messages()})

def send_private_message(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        friend_name = require(body, "friendName", "string", err_msg="Missing or error type of [friendName]")
        message_text = require(body, "message", "string", err_msg="Missing or error type of [message]")
        quote_id = require(body, "quote", "string", err_msg="Missing or error type of [quote]")

    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists() or not User.objects.filter(name=friend_name).exists():
        return USER_NOT_FOUND
    user = User.objects.get(name=user_name)
    friend = User.objects.get(name=friend_name)

    # check the friendship
    if not Friendship.objects.filter(from_user=user, to_user=friend).exists() or not Friendship.objects.filter(from_user=friend, to_user=user).exists():
        return FRIENDSHIP_NOT_FOUND
    friendship = Friendship.objects.get(from_user=user, to_user=friend)
    
    # 私聊
    if PrivateConversation.objects.filter(user1=user,user2=friend).exists():
        private_conversation = PrivateConversation.objects.get(user1=user,user2=friend)
    elif PrivateConversation.objects.filter(user1=friend,user2=user).exists():
        private_conversation = PrivateConversation.objects.get(user1=friend,user2=user)
    else: # create it
        private_conversation = PrivateConversation(user1=user,user2=friend)
        private_conversation.save()
    
    # 用户自己的私聊
    if UserPrivateConversation.objects.filter(user=user,conversation=private_conversation).exists():
        user_private_conversation = UserPrivateConversation.objects.get(user=user,conversation=private_conversation)
    else:
        user_private_conversation = UserPrivateConversation(user=user,friendship=friendship,conversation=private_conversation)
        user_private_conversation.save()

    # 好友的私聊
    if UserPrivateConversation.objects.filter(user=friend,conversation=private_conversation).exists():
        friend_private_conversation = UserPrivateConversation.objects.get(user=friend,conversation=private_conversation)
    else:
        friend_private_conversation = UserPrivateConversation(user=friend,friendship=friendship,conversation=private_conversation)
        friend_private_conversation.save()
    # 更新消息
    friend_private_conversation.unread_messages_count += 1
    friend_private_conversation.save()
    
    # 发送消息
    message = PrivateMessage(sender=user,text=message_text,conversation=private_conversation)
    if quote_id == "": quote_id = -1
    if PrivateMessage.objects.filter(id=quote_id).exists():
        quote_message = PrivateMessage.objects.get(id=quote_id)
        message = PrivateMessage(sender=user,text=message_text,conversation=private_conversation,quote=quote_message)
    else:
        message = PrivateMessage(sender=user,text=message_text,conversation=private_conversation)
    message.save()
    private_conversation.last_message = message
    private_conversation.save()
    return request_success()

def delete_private_message(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        friend_name = require(body, "friendName", "string", err_msg="Missing or error type of [friendName]")
        message_id = require(body, "messageId", "string", err_msg="Missing or error type of [messageId]")
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists() or not User.objects.filter(name=friend_name).exists():
        return USER_NOT_FOUND
    
    user = User.objects.get(name=user_name)
    friend = User.objects.get(name=friend_name)
    if not PrivateMessage.objects.filter(id=message_id).exists():
        return MESSAGE_NOT_FOUND
    private_message = PrivateMessage.objects.get(id=message_id)

    # 检查好友关系是否仍然存在
    if not Friendship.objects.filter(from_user=user, to_user=friend).exists() or not Friendship.objects.filter(from_user=friend, to_user=user).exists():
        return FRIENDSHIP_NOT_FOUND
    
    # 检查私聊会话是否存在
    if not PrivateConversation.objects.filter(user1=user,user2=friend).exists() and not PrivateConversation.objects.filter(user1=friend,user2=user).exists():
        return CONVERSATION_NOT_FOUND
    
    if private_message.sender != user:
        return request_failed(1, "Not message sender", 403)
    
    private_message.delete()
    return request_success()

def get_all_conversation_list(req: HttpRequest):
    if req.method != 'GET':
        return BAD_METHOD
    try:
        user_name = req.GET.get('userName')
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists():
        return USER_NOT_FOUND
    
    user = User.objects.get(name=user_name)

    private_conversations = UserPrivateConversation.objects.filter(user=user)
    private_conversation_list = []
    for private_conversation in private_conversations:
        private_conversation_list.append(private_conversation.serialize())
    
    group_conversations = UserGroupConversation.objects.filter(user=user)
    group_conversation_list = []
    for group_conversation in group_conversations:
        group_conversation_list.append(group_conversation.serialize())
    
    return request_success(data={'privateConversationList': private_conversation_list})