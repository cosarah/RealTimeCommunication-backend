from django.db import models
from user.models import User

# Create your models here.
# 聊天表
class Conversation(models.Model):
    id = models.BigAutoField(primary_key=True) # 主键
    title = models.CharField(max_length=255, blank=True, null=True) # 对于群聊，可以有标题
    is_group = models.BooleanField(default=False) # False 表示私聊，True 表示群聊
    participants = models.ManyToManyField(User, through='Participant')
    created_at = models.DateTimeField(auto_now_add=True) # 创建时间
    updated_at = models.DateTimeField(auto_now=True) # 最新消息时间

# 聊天参与者
class Participant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True) # 进群时间
    is_admin = models.BooleanField(default=False) # 是否为群管理员
    
    class Meta:
        unique_together = ('user', 'conversation')

# 信息表
class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE) # 对应聊天
    sender = models.ForeignKey(User, on_delete=models.CASCADE) # 发送者
    text = models.TextField() # 文本
    quote = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE) # 引用消息
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
    conversation = models.ForeignKey(Conversation, related_name='announcements', on_delete=models.CASCADE)
    message = models.TextField()
    announced_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [models.Index(fields=["conversation"])]