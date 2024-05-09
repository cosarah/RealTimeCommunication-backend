from django.db import models
from user.models import User
from friend.models import Friendship
from utils.utils_require import MAX_CHAR_LENGTH, MAX_NAME_LENGTH

# Create your models here.

# 用户聊天管理：用户共友两种聊天会话，私聊对应唯一的好友关系，而群聊则是用户自定义的。

class PrivateConversation(models.Model):
    user1 = models.ForeignKey(User, related_name='user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='user2', on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_time']
        unique_together = ('user1', 'user2')
    
    def get_messages(self):
        messages = self.messages.all().order_by('-created_time')
        return [message.serialize() for message in messages]
    
    def get_last_message(self):
        return PrivateMessage.objects.filter(conversation=self).order_by('-created_time').first()

class PrivateMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sender', on_delete=models.CASCADE)
    text = models.CharField(max_length=MAX_CHAR_LENGTH)
    created_time = models.DateTimeField(auto_now_add=True)
    quote = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='private_quotes')
    conversation = models.ForeignKey(PrivateConversation, on_delete=models.CASCADE, related_name='messages')
    is_read = models.BooleanField(default=False) # 是否已读
    class Meta:
        ordering = ['-created_time']

    def read(self): # 被reciever读后，置为已读
        if self.is_read:
            return False
        else:
            self.is_read = True
            self.save()
            return True
    def serialize(self):
        return {
            'id': self.id,
            'senderName': self.sender.name,
            'sendTime': self.created_time.strftime('%Y-%m-%d %H:%M:%S'),
            'text': self.text,
            'isRead': self.is_read,
            'quoteId': self.quote.id if self.quote else None,
        }
    

class UserPrivateConversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='private_conversations')
    friendship = models.ForeignKey(Friendship, on_delete=models.CASCADE, related_name='private_conversation_friends')
    conversation = models.ForeignKey(PrivateConversation, on_delete=models.CASCADE, related_name='private_conversations')
    # receiver = models.ForeignKey(UserPrivateMessageReicever, on_delete=models.CASCADE, related_name='private_conversations')
    unread_messages_count = models.PositiveIntegerField(default=0) # 未读消息数
    def serialize(self):
        return {
            'id': self.id,
            'userName': self.user.name,
            'friendName': self.friendship.to_user.name,
            'friendNickName': self.friendship.to_user.nick_name,
            'friendAlias': self.friendship.alias,
            'friendPortraitType': self.friendship.to_user.portrait_type,
            'friendPortraitUrl': self.friendship.to_user.portrait,
            'friendIsOnline': self.friendship.to_user.is_online,
            
            'unreadMessageCount': self.unread_messages_count,
            'lastMessage': self.conversation.get_last_message().serialize() if self.conversation.get_last_message() else None,
        }
    def read(self):
        if self.unread_messages_count == 0:
            return False
        else:
            friend = self.friendship.to_user
            self.conversation.messages.filter(sender=friend, is_read=False).update(is_read=True)
            self.unread_messages_count = 0
            self.save()
            return True

class GroupMessage(models.Model):
    sender = models.ForeignKey(User, related_name='group_sender', on_delete=models.DO_NOTHING) # 用户删除之后，对应聊天记录并不删除
    text = models.CharField(max_length=MAX_CHAR_LENGTH)
    created_time = models.DateTimeField(auto_now_add=True)
    quote = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='group_quotes') # 删除引用后，引用对象为空
    conversation = models.ForeignKey('GroupConversation', on_delete=models.CASCADE, related_name='messages')
    read_user_list = models.ManyToManyField(User, related_name='read_group_message_users') # 已读用户列表
    class Meta:
        ordering = ['-created_time']

    def serialize(self):
        return {
            'id': self.id,
            'senderName': self.sender.name,
            'sendTime': self.created_time.strftime('%Y-%m-%d %H:%M:%S'),
            'text': self.text,
            'quoteId': self.quote.id if self.quote else None,
        }

class GroupConversation(models.Model):
    title = models.CharField(max_length=MAX_NAME_LENGTH, blank=True, null=True) # 对于群聊，有标题
    
    owner = models.ForeignKey(User, related_name='owner', on_delete=models.CASCADE) # 群主
    admins = models.ManyToManyField(User, related_name='admins') # 群管理员
    members = models.ManyToManyField(User, related_name='members') # 群成员

    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    def get_messages(self):
        messages = self.messages.all().order_by('-created_time')
        return [message.serialize() for message in messages]
    
    def get_last_message(self):
        return GroupMessage.objects.filter(conversation=self).order_by('-created_time').first()

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'owner': self.owner.__info__(),
            'admins': [admin.__info__() for admin in self.admins.all()],
            'members': [member.__info__() for member in self.members.all()],
            'createdTime': self.created_time.strftime('%Y-%m-%d %H:%M:%S'),
            'lastMessage': self.get_last_message().serialize() if self.get_last_message() else None,
            'announcements': [announcement.serialize() for announcement in self.announcements.all()],
        }
    
    def get_all_participants(self):
        return self.members.all() | self.admins.all() | User.objects.filter(id=self.owner.id)
        
    def transfer_owner(self, from_user, to_user): # 群主转让
        from_user_conversation = UserGroupConversation.objects.get(group_conversation=self, user=from_user)
        to_user_conversation = UserGroupConversation.objects.get(group_conversation=self, user=to_user)
        from_user_conversation.identity = 1
        to_user_conversation.identity = 2
        self.owner = to_user

        self.save()
        from_user_conversation.save()
        to_user_conversation.save()

    def add_admin(self, user): # 群管理员添加
        self.admins.add(user)
        UserGroupConversation.objects.create(group_conversation=self, user=user, identity=1)
        self.save()

    def remove_admin(self, user): # 群管理员移除
        self.admins.remove(user)
        UserGroupConversation.objects.filter(group_conversation=self, user=user).delete()
        self.save()
    
    def add_member(self, user): # 群成员添加，需要提前判断该群成员是否已经存在
        self.members.add(user)
        UserGroupConversation.objects.create(group_conversation=self, user=user, identity=0)
        self.save()
    
    def remove_member(self, user): # 群成员移除
        self.members.remove(user)
        UserGroupConversation.objects.filter(group_conversation=self, user=user).delete()
        self.save()

    def add_request(self, from_user, to_user, message): # 群成员邀请
        if to_user in self.members.all():
            return False
        else:
            GroupConversationRequest.objects.create(group_conversation=self, from_user=from_user, to_user=to_user, message=message)
            return True
        
    def add_announcement(self, from_user, text): # 群公告
        Announcement.objects.create(group_conversation=self, text=text, created_by=from_user)

    def remove_announcement(self, announcement_id): # 删除群公告
        Announcement.objects.filter(id=announcement_id).delete()

class GroupConversationRequest(models.Model):

    group_conversation = models.ForeignKey(GroupConversation, on_delete=models.CASCADE, related_name='requests')
    from_user = models.ForeignKey(User, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='to_user', on_delete=models.CASCADE)
    message = models.CharField(max_length=MAX_CHAR_LENGTH, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = (
        (0, '等待处理'),
        (1, '已同意'),
        (2, '已拒绝'),
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=0) # 0-等待处理，1-已同意，2-已拒绝

    def accept(self):
        if self.status != 1:
            self.status = 1
            self.save()
            self.group_conversation.add_member(self.to_user)
            return True
        else:
            return False
        
    def reject(self):
        if self.status == 0:
            self.status = 2
            self.save()
            return True
        else:
            return False

class Announcement(models.Model): 
    group_conversation = models.ForeignKey(GroupConversation, related_name='announcements', on_delete=models.CASCADE)
    text = models.CharField(max_length=MAX_CHAR_LENGTH)
    created_by = models.ForeignKey(User, related_name='created_by', on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
    def serialize(self):
        return {
            'id': self.id,
            'text': self.text,
            'createdBy': self.created_by.name,
            'createdTime': self.created_time.strftime('%Y-%m-%d %H:%M:%S'),
        }

class UserGroupConversation(models.Model):
    group_conversation = models.ForeignKey(GroupConversation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    alias = models.CharField(max_length=MAX_NAME_LENGTH, null=True)  # 使用lambda获取nick_name    
    join_time = models.DateTimeField(auto_now_add=True) # 用户入群时间
    IDENTITY_CHOICES = (
        (2, '群主'),
        (1, '管理员'),
        (0, '成员'),
    )
    identity = models.IntegerField(choices=IDENTITY_CHOICES, default=0) # 用户群身份，如群主、管理员等
    unread_messages_count = models.PositiveIntegerField(default=0) # 未读消息数

    def get_group_member(self):
        return self.group_conversation.members.all()
    
    def get_owner(self):
        return self.group_conversation.owner
    
    def get_admins(self):
        return self.group_conversation.admins.all()
    
    def get_group_member_info(self):
        return [user.__info__() for user in self.get_group_member()]
    
    def exit(self): # 退出群聊
        if self.identity == 2: # 若为群主，则需要先转让群主
            return False
        self.delete()
        return True

    def serialize(self):
        return {
            'id': self.id,
            'groupName': self.group_conversation.title,
            'userAlias': self.alias,
            'joinTime': self.join_time.strftime('%Y-%m-%d %H:%M:%S'),
            'identity': self.identity,
            'unreadMessageCount': self.unread_messages_count,
            'groupConversation': self.group_conversation.serialize()
        }
    
    def read(self):
        if self.unread_messages_count == 0:
            return False
        else:
            self.group_conversation.messages.exclude(sender=self.user).filter(is_read=False).update(read_user_list=models.F('read_user_list') | User.objects.filter(id=self.user.id))
            self.unread_messages_count = 0
            self.save()
            return True