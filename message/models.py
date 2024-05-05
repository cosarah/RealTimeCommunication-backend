from django.db import models
from user.models import User

# Create your models here.
<<<<<<< HEAD
class Chat(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(User)



# 聊天表
class Conversation(models.Model):
    id = models.BigAutoField(primary_key=True) # 主键
    title = models.CharField(max_length=255, blank=True, null=True) # 对于群聊，有标题
    is_group = models.BooleanField(default=False) # False 表示私聊，True 表示群聊
    participants = models.ManyToManyField(User, through='Participant')
    created_at = models.DateTimeField(auto_now_add=True) # 创建时间
    updated_at = models.DateTimeField(auto_now=True) # 最新消息时间

# 聊天参与者
class Participant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
=======

# 用户聊天管理

class UserGroupChat(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    chat = models.OneToOneField('GroupChat', on_delete=models.CASCADE)
    IDENTITY_CHOICES = (
        ('owner', '群主'),
        ('admin', '管理员'),
    )
    identity = models.CharField(max_length=255) # 身份，如群主、管理员等

# 聊天表
class Chat(models.Model):
    id = models.BigAutoField(primary_key=True) # 主键
    title = models.CharField(max_length=255, blank=True, null=True) # 对于群聊，有标题
    is_group = models.BooleanField(default=False) # False 表示私聊，True 表示群聊
    last_message = models.ForeignKey('Message', on_delete=models.SET_NULL, null=True, related_name='last_message_of_chat') # 最后一条消息
    created_at = models.DateTimeField(auto_now_add=True) # 创建时间
    updated_at = models.DateTimeField(auto_now=True) # 最新消息时间

class SecretChat(models.Model):
    chat = models.OneToOneField(Chat, on_delete=models.CASCADE)
    
class GroupChat(models.Model):
    chat = models.OneToOneField(Chat, on_delete=models.CASCADE)
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_of_group') # 群主
    admins = models.ManyToManyField(User, related_name='admin_of_group') # 群管理员

# 聊天参与者
class Participant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conversation = models.ForeignKey(Chat, on_delete=models.CASCADE)
>>>>>>> feature/message
    joined_at = models.DateTimeField(auto_now_add=True) # 进群时间
    is_admin = models.BooleanField(default=False) # 是否为群管理员
    
    class Meta:
        unique_together = ('user', 'conversation')

# 信息表
class Message(models.Model):
<<<<<<< HEAD
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE) # 对应聊天
=======
    conversation = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE) # 对应聊天
>>>>>>> feature/message
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) # 发送者，允许为空，即对应用户注销之后保留发送过的信息，但不显示头像
    text = models.TextField() # 文本
    quote = models.ForeignKey('self', on_delete=models.SET_NULL, null=True) # 引用消息
    sent_at = models.DateTimeField(auto_now_add=True) # 发送时间

# 消息状态表
class MessageStatus(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='statuses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('message', 'user')

# 群公告
class Announcement(models.Model): 
<<<<<<< HEAD
    conversation = models.ForeignKey(Conversation, related_name='announcements', on_delete=models.CASCADE)
=======
    conversation = models.ForeignKey(Chat, related_name='announcements', on_delete=models.CASCADE)
>>>>>>> feature/message
    message = models.TextField()
    announced_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [models.Index(fields=["conversation"])]