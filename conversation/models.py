from django.db import models
from user.models import User

# Create your models here.

# 用户聊天管理：用户共友两种聊天会话，私聊对应唯一的好友关系，而群聊则是用户自定义的。

class PrivateConversation(models.Model):
    user1 = models.ForeignKey(User, related_name='user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='user2', on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    last_message_text = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-created_time']
        unique_together = ('user1', 'user2')

class PrivateMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sender', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    created_time = models.DateTimeField(auto_now_add=True)
    quote = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='quote')
    conversation = models.ForeignKey(PrivateConversation, on_delete=models.CASCADE, related_name='messages')
    is_read = models.BooleanField(default=False) # 是否已读
    class Meta:
        ordering = ['-created_time']

class UserPrivateMessageReicever(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='private_message_receiver')
    def read(conversation_name):
        user = private_message_receiver
        user_private_conversation = UserPrivateConversation.objects.get(user=self.user, conversation__name=conversation_name)
        user_private_conversation.read = True
        user_private_conversation.save()

class UserPrivateConversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='private_conversations')
    conversation = models.ForeignKey(PrivateConversation, on_delete=models.CASCADE, related_name='private_participants')
    receiver = models.ForeignKey(UserPrivateMessageReicever, on_delete=models.CASCADE, related_name='private_conversations')
    unread_messages_count = models.PositiveIntegerField(default=0) # 未读消息数




class GroupConversation(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True) # 对于群聊，有标题
    participants = models.ManyToManyField(User, through='Participant')
    owner = models.ForeignKey(User, related_name='owner', on_delete=models.CASCADE)
    admins = models.ManyToManyField(User, related_name='admins', blank=True)

    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

class Announcement(models.Model): 
    group_conversation = models.ForeignKey(GroupConversation, related_name='announcements', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, related_name='created_by', on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["group_chat"])]

    def __str__(self):
        return self.text

class UserGroupConversation(models.Model):
    group_conversation = models.ForeignKey(GroupConversation, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    IDENTITY_CHOICES = (
        ('owner', '群主'),
        ('admin', '管理员'),
        ('member', '成员'),
    )
    identity = models.CharField(max_length=255) # 身份，如群主、管理员等
