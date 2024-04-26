import json
from django.test import TestCase
from user.models import User
from friend.models import Friendship, FriendRequest, UserTag
from django.utils import timezone