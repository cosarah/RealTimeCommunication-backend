from django.shortcuts import render
import json
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from user.models import User
from friend.models import Friendship
from conversation.models import PrivateConversation, PrivateMessage ,GroupConversation, UserPrivateConversation, UserGroupConversation, GroupMessage
from utils.utils_request import request_failed, request_success, return_field
from utils.utils_request import BAD_METHOD, BAD_PARAMS, USER_NOT_FOUND, ALREADY_EXIST, CREATE_SUCCESS, DELETE_SUCCESS, UPDATE_SUCCESS, FRIENDSHIP_NOT_FOUND, CONVERSATION_NOT_FOUND, MESSAGE_NOT_FOUND, PERMISSION_DENIED
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp
from utils.utils_jwt import generate_jwt_token, check_jwt_token
from user.views import validate_name

# Create your views here.
# 每次返回的都是按照更新时间排序的表单
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

###############
"""私聊系统"""
def get_private_conversation_list(req: HttpRequest):
    if req.method != 'GET':
        return BAD_METHOD
    
    try:
        user_name = req.GET.get('userName')
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists() or User.objects.get(name=user_name).is_closed:
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

def get_user_private_message_list(req: HttpRequest):
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
    
    if not Friendship.objects.filter(from_user=user,to_user=friend).exists() or not Friendship.objects.filter(from_user=friend, to_user=user).exists():
        return FRIENDSHIP_NOT_FOUND
    friendship = Friendship.objects.get(from_user=user,to_user=friend)

    if not UserPrivateConversation.objects.filter(user=user,conversation=private_conversation).exists():
        user_private_conversation = UserPrivateConversation.objects.create(user=user,friendship=friendship,conversation=private_conversation)
    else:
        user_private_conversation = UserPrivateConversation.objects.get(user=user,conversation=private_conversation)


    
    user_private_conversation.read()
    return request_success(data={'messageList': user_private_conversation.get_messages()})

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
    friendship2 = Friendship.objects.get(from_user=friend, to_user=user)
    
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
        friend_private_conversation = UserPrivateConversation(user=friend,friendship=friendship2,conversation=private_conversation)
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


    # 更新消息
    friend_private_conversation.add_message(message)
    friend_private_conversation.unread_messages_count += 1
    friend_private_conversation.save()
    user_private_conversation.add_message(message)
    user_private_conversation.save()
    private_conversation.save()
    return request_success({'messageId': message.id})

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
    if not Friendship.objects.filter(from_user=friend,to_user=user).exists() or not Friendship.objects.filter(from_user=user,to_user=friend).exists():
        return FRIENDSHIP_NOT_FOUND
    
    friendship = Friendship.objects.get(from_user=user,to_user=friend)
    user_private_conversation = UserPrivateConversation.objects.get(user=user,friendship=friendship)
    user_private_conversation.delete_message(private_message)
    return request_success()

def withdraw_private_message(req: HttpRequest):
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

###############
"""群聊管理"""
def get_group_conversation_list(req: HttpRequest):
    if req.method != 'GET':
        return BAD_METHOD
    
    try:
        user_name = req.GET.get('userName')
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists():
        return USER_NOT_FOUND
    
    user = User.objects.get(name=user_name)

    group_conversations = UserGroupConversation.objects.filter(user=user)
    group_conversation_list = []
    for group_conversation in group_conversations:
        group_conversation_list.append(group_conversation.serialize())
    return request_success(data={'groupConversationList': group_conversation_list})

def create_group_conversation(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        group_tilte = require(body, "groupTitle", "string", err_msg="Missing or error type of [groupName]")
        group_members = require(body, "groupMembers", "list", err_msg="Missing or error type of [groupMembers]")
    except:
        return BAD_PARAMS
    
    if validate_name(group_tilte) == False:
        return BAD_PARAMS

    # 检验用户有效性
    for member in group_members + [user_name]:
        if not User.objects.filter(name=user_name).exists() or User.objects.get(name=member).is_closed:
            return USER_NOT_FOUND
    
    # 检验好友关系有效性
    user = User.objects.get(name=user_name)
    for member in group_members:
        friend = User.objects.get(name=member)
        if not Friendship.objects.filter(from_user=user, to_user=friend).exists() or not Friendship.objects.filter(from_user=friend, to_user=user).exists():
            return FRIENDSHIP_NOT_FOUND

    # 创建群组
    group_conversation = GroupConversation.objects.create(title=group_tilte,owner=user)
    user_group_conversation = UserGroupConversation.objects.create(user=user, group_conversation=group_conversation, identity=2)
    user_group_conversation.save()
    ## 创建成员群组会话
    for member in group_members:
        group_conversation.add_member(User.objects.get(name=member))
        UserGroupConversation.objects.create(user=User.objects.get(name=member), group_conversation=group_conversation, identity=0)

    group_conversation.save()
    return request_success({'groupId': group_conversation.id})

### TODO:删除群聊是否应当改为标记已删除而非删除数据库
def delete_group_conversation(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        group_id = require(body, "groupId", "string", err_msg="Missing or error type of [groupId]")
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists():
        return USER_NOT_FOUND
    
    user = User.objects.get(name=user_name)
    if not UserGroupConversation.objects.filter(user=user, group_conversation__id=group_id).exists():
        return CONVERSATION_NOT_FOUND
    
    user_group_conversation = UserGroupConversation.objects.get(user=user, group_conversation__id=group_id)
    if user_group_conversation.identity != 2:
        return PERMISSION_DENIED
    
    group_conversation = UserGroupConversation.objects.get(user=user, id=group_id)
    group_conversation.delete()

    return request_success()



###############
"""群聊信息管理"""
def get_group_message_list(req: HttpRequest):
    if req.method != 'GET':
        return BAD_METHOD
    
    try:
        user_name = req.GET.get('userName')
        group_id = req.GET.get('groupId')
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists():
        return USER_NOT_FOUND
    
    user = User.objects.get(name=user_name)
    if not UserGroupConversation.objects.filter(user=user, group_conversation__id=group_id).exists():
        return CONVERSATION_NOT_FOUND
    
    user_group_conversation = UserGroupConversation.objects.get(user=user, group_conversation__id=group_id)
    group_conversation = user_group_conversation.group_conversation
    group_conversation.last_read_time = get_timestamp()
    group_conversation.save()
    return request_success(data={'messageList': group_conversation.get_messages()})

def send_group_message(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        group_id = require(body, "groupId", "string", err_msg="Missing or error type of [groupId]")
        message_text = require(body, "message", "string", err_msg="Missing or error type of [message]")
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists() or User.objects.get(name=user_name).is_closed:
        return USER_NOT_FOUND
    
    user = User.objects.get(name=user_name)
    if not GroupConversation.objects.filter(id=group_id).exists() or not UserGroupConversation.objects.filter(user=user, group_conversation__id=group_id).exists() or UserGroupConversation.objects.get(user=user, group_conversation__id=group_id).is_kicked:
        return CONVERSATION_NOT_FOUND
    
    user_group_conversation = UserGroupConversation.objects.get(user=user, group_conversation__id=group_id)
    group_conversation = GroupConversation.objects.get(id=group_id)
    message = GroupMessage(sender=user,text=message_text,conversation=group_conversation)
    message.save()
    group_conversation.save() # 用于更新时间

    for member in group_conversation.get_all_participants():
        if member == user:
            user_group_conversation.add_message(message)
        else:
            if member.is_closed:
                continue
            if not UserGroupConversation.objects.filter(user=member, group_conversation=group_conversation).exists() or UserGroupConversation.objects.get(user=member, group_conversation=group_conversation).is_kicked:
                continue
            other_member_group_conversation = UserGroupConversation.objects.get(user=member, group_conversation=group_conversation)
            other_member_group_conversation.add_message(message)
            other_member_group_conversation.unread_messages_count += 1
            other_member_group_conversation.save()

    return request_success({'messageId': message.id})

def delete_group_message(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        group_id = require(body, "groupId", "string", err_msg="Missing or error type of [groupId]")
        message_id = require(body, "messageId", "string", err_msg="Missing or error type of [messageId]")
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists():
        return USER_NOT_FOUND
    
    user = User.objects.get(name=user_name)
    if not UserGroupConversation.objects.filter(user=user, group_conversation__id=group_id).exists():
        return CONVERSATION_NOT_FOUND
    
    user_group_conversation = UserGroupConversation.objects.get(user=user, group_conversation__id=group_id)
    if user_group_conversation.is_kicked:
        return PERMISSION_DENIED
    if not GroupMessage.objects.filter(id=message_id).exists():
        return MESSAGE_NOT_FOUND
    group_message = GroupMessage.objects.get(id=message_id)
    user_group_conversation.delete_message(group_message)
    return request_success({'MessageId': group_message.id})



def withdraw_group_message(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        group_id = require(body, "groupId", "string", err_msg="Missing or error type of [groupId]")
        message_id = require(body, "messageId", "string", err_msg="Missing or error type of [messageId]")
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists():
        return USER_NOT_FOUND
    
    user = User.objects.get(name=user_name)
    if not UserGroupConversation.objects.filter(user=user, group_conversation__id=group_id).exists():
        return CONVERSATION_NOT_FOUND
    
    user_group_conversation = UserGroupConversation.objects.get(user=user, group_conversation__id=group_id)
    group_conversation = user_group_conversation.group_conversation
    if not PrivateMessage.objects.filter(id=message_id).exists():
        return MESSAGE_NOT_FOUND
    private_message = PrivateMessage.objects.get(id=message_id)

    if private_message.conversation != group_conversation:
        return request_failed(1, "Not message sender", 403)
    
    private_message.delete()
    return request_success()

###############
"""群聊设置"""
def set_group_title(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        group_id = require(body, "groupId", "string", err_msg="Missing or error type of [groupId]")
        group_title = require(body, "groupTitle", "string", err_msg="Missing or error type of [groupTitle]")
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists():
        return USER_NOT_FOUND
    
    user = User.objects.get(name=user_name)
    if not UserGroupConversation.objects.filter(user=user, group_conversation__id=group_id).exists() or UserGroupConversation.objects.get(user=user, group_conversation__id=group_id).is_kicked:
        return CONVERSATION_NOT_FOUND
    
    user_group_conversation = UserGroupConversation.objects.get(user=user, group_conversation__id=group_id)
    group_conversation = user_group_conversation.group_conversation
    group_conversation.title = group_title
    group_conversation.save()
    return request_success()

def set_announcement(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        group_id = require(body, "groupId", "string", err_msg="Missing or error type of [groupId]")
        announcement = require(body, "announcement", "string", err_msg="Missing or error type of [announcement]")
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists():
        return USER_NOT_FOUND
    
    user = User.objects.get(name=user_name)
    if not UserGroupConversation.objects.filter(user=user, group_conversation__id=group_id).exists():
        return CONVERSATION_NOT_FOUND
    
    user_group_conversation = UserGroupConversation.objects.get(user=user, group_conversation__id=group_id)
    
    if user_group_conversation.identity == 0: # 群成员不可设置群公告
        return PERMISSION_DENIED

    group_conversation = GroupConversation.objects.get(id=group_id)
    group_conversation.add_announcement(user, announcement)
    return request_success()

def set_owner(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        group_id = require(body, "groupId", "string", err_msg="Missing or error type of [groupId]")
        new_owner_name = require(body, "newOwnerName", "string", err_msg="Missing or error type of [newOwnerName]")
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists() or User.objects.get(name=user_name).is_closed:
        return USER_NOT_FOUND
    
    if not User.objects.filter(name=new_owner_name).exists() or User.objects.get(name=new_owner_name).is_closed:
        return USER_NOT_FOUND
    
    user = User.objects.get(name=user_name)
    new_owner = User.objects.get(name=new_owner_name)
    if not UserGroupConversation.objects.filter(user=user, group_conversation__id=group_id).exists() or UserGroupConversation.objects.get(user=user, group_conversation__id=group_id).is_kicked:
        return CONVERSATION_NOT_FOUND
    if not UserGroupConversation.objects.filter(user=new_owner, group_conversation__id=group_id).exists() or UserGroupConversation.objects.get(user=new_owner, group_conversation__id=group_id).is_kicked:
        return CONVERSATION_NOT_FOUND

    user_group_conversation = UserGroupConversation.objects.get(user=user, group_conversation__id=group_id)
    new_owner_group_conversation = UserGroupConversation.objects.get(user=new_owner, group_conversation__id=group_id)

    group_conversation = GroupConversation(id=group_id)

    if not user_group_conversation.identity == 2: # 群主不可转让群主
        return PERMISSION_DENIED
    
    # 删除新群主原群身份
    if new_owner_group_conversation.identity == 0: 
        group_conversation.members.remove(new_owner)
    if new_owner_group_conversation.identity == 1:
        group_conversation.admins.remove(new_owner)

    new_owner_group_conversation.identity = 2
    new_owner_group_conversation.save()

    user_group_conversation.identity = 1
    user_group_conversation.save()
    group_conversation.owner = new_owner

    group_conversation.admins.add(user)
    group_conversation.save()

    return request_success()


def add_admin(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        group_id = require(body, "groupId", "string", err_msg="Missing or error type of [groupId]")
        new_admin_name_list = require(body, "newAdminNameList", "list", err_msg="Missing or error type of [newAdminName]")
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists() or User.objects.get(name=user_name).is_closed:
        return USER_NOT_FOUND
    user = User.objects.get(name=user_name)

    if not UserGroupConversation.objects.filter(user=user, group_conversation__id=group_id).exists() or UserGroupConversation.objects.get(user=user, group_conversation__id=group_id).is_kicked:
        return CONVERSATION_NOT_FOUND
    
    user_group_conversation = UserGroupConversation.objects.get(user=user, group_conversation__id=group_id)
    group_conversation = GroupConversation.objects.get(id=group_id)
    if user_group_conversation.identity != 2: # 只有群主可添加管理员
        return PERMISSION_DENIED

    for new_admin_name in new_admin_name_list:
        if not User.objects.filter(name=new_admin_name).exists() or User.objects.get(name=new_admin_name).is_closed:
            return USER_NOT_FOUND
        new_admin = User.objects.get(name=new_admin_name)
        if not UserGroupConversation.objects.filter(user=new_admin, group_conversation__id=group_id).exists() or UserGroupConversation.objects.get(user=new_admin, group_conversation__id=group_id).is_kicked:
            return CONVERSATION_NOT_FOUND
        new_admin_group_conversation = UserGroupConversation.objects.get(user=new_admin, group_conversation__id=group_id)
    return request_success()

def remove_admin(req: HttpRequest):
    return request_success()

###############
"""群聊成员管理"""
def get_group_members(req: HttpRequest):
    if req.method != 'GET':
        return BAD_METHOD
    
    try:
        user_name = req.GET.get('userName')
        group_id = req.GET.get('groupId')
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists() or User.objects.get(name=user_name).is_closed: # 无效用户
        return USER_NOT_FOUND
    
    user = User.objects.get(name=user_name)
    if not UserGroupConversation.objects.filter(user=user, group_conversation__id=group_id).exists():
        return CONVERSATION_NOT_FOUND
    
    user_group_conversation = UserGroupConversation.objects.get(user=user, group_conversation__id=group_id)
    group_conversation = user_group_conversation.group_conversation
    return request_success(data={'members': group_conversation.serialize()})




def quit_group(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        group_id = require(body, "groupId", "string", err_msg="Missing or error type of [groupId]")
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists():
        return USER_NOT_FOUND
    
    user = User.objects.get(name=user_name)
    if not UserGroupConversation.objects.filter(user=user, group_conversation__id=group_id).exists():
        return CONVERSATION_NOT_FOUND
    
    user_group_conversation = UserGroupConversation.objects.get(user=user, group_conversation__id=group_id)
    group_conversation = user_group_conversation.group_conversation
    group_conversation.remove_member(user)
    user_group_conversation.delete()
    return request_success()

def fix_user_group_conversation(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    
    try:
        body = json.loads(req.body.decode("utf-8"))
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        group_id = require(body, "groupId", "string", err_msg="Missing or error type of [groupId]")
        alias = require(body, "groupAlias", "string", err_msg="Missing or error type of [alias]")
    except:
        return BAD_PARAMS
    
    if not validate_name(alias):
        return BAD_PARAMS

    if not User.objects.filter(name=user_name).exists() or User.objects.get(name=user_name).is_closed: # 存在无效用户
        return USER_NOT_FOUND
    
    user = User.objects.get(name=user_name)
    if not UserGroupConversation.objects.filter(user=user, group_conversation__id=group_id).exists():
        return CONVERSATION_NOT_FOUND
    user_group_conversation = UserGroupConversation.objects.get(user=user, group_conversation__id=group_id)
    user_group_conversation.alias = alias
    user_group_conversation.save()
    return request_success()
################