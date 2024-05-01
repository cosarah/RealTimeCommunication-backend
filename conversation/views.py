from django.shortcuts import render
import json
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from user.models import User
from conversation.models import PrivateConversation, GroupConversation
from utils.utils_request import request_failed, request_success, return_field
from utils.utils_request import BAD_METHOD, BAD_PARAMS, USER_NOT_FOUND, ALREADY_EXIST, CREATE_SUCCESS, DELETE_SUCCESS, UPDATE_SUCCESS
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp
from utils.utils_jwt import generate_jwt_token, check_jwt_token

# Create your views here.
