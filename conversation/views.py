from django.shortcuts import render
import json
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from user.models import User
from friend.models import Friendship
from conversation.models import PrivateConversation, PrivateMessage ,GroupConversation
from utils.utils_request import request_failed, request_success, return_field
from utils.utils_request import BAD_METHOD, BAD_PARAMS, USER_NOT_FOUND, ALREADY_EXIST, CREATE_SUCCESS, DELETE_SUCCESS, UPDATE_SUCCESS, FRIENDSHIP_NOT_FOUND
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp
from utils.utils_jwt import generate_jwt_token, check_jwt_token

# Create your views here.

def send_private_message(req: HttpRequest):
    if req.method != 'POST':
        return BAD_METHOD
    
    try:
        user_name = req.GET.get('userName')
        friend_name = req.GET.get('friendName')
        message_text = req.GET.get('message')
        quote_id = req.GET.get('quote')
    except:
        return BAD_PARAMS
    
    if not User.objects.filter(name=user_name).exists() or not User.objects.filter(name=friend_name).exists():
        return USER_NOT_FOUND
    user = User.objects.get(name=user_name)
    friend = User.objects.get(name=friend_name)

    # check the friendship
    if not Friendship.objects.filter(from_user=user, to_user=friend):
        return FRIENDSHIP_NOT_FOUND

    if PrivateConversation.objects.filter(user1=user,user2=friend).exists():
        private_conversation = PrivateConversation.objects.get(user1=user,user2=friend)
    elif PrivateConversation.objects.filter(user1=friend,user2=user).exists():
        private_conversation = PrivateConversation.objects.get(user1=friend,user2=user)
    else: # create it
        private_conversation = PrivateConversation(user1=user,user2=friend)
        private_conversation.save()
    
    message = PrivateMessage(sender=user,text=message_text,conversation=private_conversation,quote=quote_id)
    message.save()
            
    
    
