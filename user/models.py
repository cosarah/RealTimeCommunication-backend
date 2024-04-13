from django.utils import timezone
from django.db import models

from utils.utils_require import MAX_CHAR_LENGTH

# 可采用Django REST framework 的序列化器避免手写序列化代码
# 用户表
class User(models.Model):
    id = models.BigAutoField(primary_key=True) # 主键
    name = models.CharField(max_length=MAX_CHAR_LENGTH, unique=True) # 用户名称，唯一
    nick_name = models.CharField(max_length=MAX_CHAR_LENGTH, null=True, blank=True, verbose_name='昵称') # 昵称，可为空
    password = models.CharField(max_length=MAX_CHAR_LENGTH) # 密码
    create_time = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    phone = models.CharField(max_length=11, null=True, verbose_name='手机号码', db_index=True) # 手机号码，可为空
    email = models.EmailField(max_length=100, verbose_name='邮箱', db_index=True, default='') # 邮箱
    portrait = models.URLField(null=True, blank=True, verbose_name='头像') # 头像url
    introduction = models.CharField(max_length=250, null=True, blank=True, verbose_name='个人简介') # 个人简介
    birthday = models.DateField(default=None, null=True, verbose_name='生日') # 生日
    GENDER_CHOICES = ( # 性别
        (0, '女'),
        (1, '男'),
        (2, '保密')
    )
    gender = models.IntegerField(choices=GENDER_CHOICES, default=2, verbose_name='性别')
    class Meta: # 快速搜索
        indexes = [models.Index(fields=["name"])]
        
    def serialize(self): # 序列化
        return {
            "id": self.id, 
            "name": self.name, 
            "nick_name": self.nick_name,
            "create_time": self.create_time,
            "introduction": self.introduction,
            "birthday": self.birthday,
            "phone": self.phone,
            "email": self.email,
            "portrait": self.portrait
        }
    
    def __str__(self) -> str:
        return self.name

# define friendship model, using many to many model
class UserProfile(models.Model): # 扩展用户
    user = models.OneToOneField(User, on_delete=models.CASCADE) # 与User模型一对一关系，一个User有对应的一个UserProfile
    friends = models.ManyToManyField('self', through='Friendship', symmetrical=False, related_name='user_friends') # 好友关系，采用多对多的形式，不同好友之间是多对多关系，同一个好友之间是双向关系
    # 可以直接使用User.freinds.all()获取某个用户的所有好友

# 好友关系表
class Friendship(models.Model):
    from_user = models.ForeignKey(User, related_name='friendship_creator', on_delete=models.CASCADE) # 该用户的所有好友
    to_user = models.ForeignKey(User, related_name='friend', on_delete=models.CASCADE) # 好友用户
    remark = models.CharField(max_length=100, blank=True, help_text='好友备注') # 好友备注
    tags = models.CharField(max_length=100, blank=True) # 用户标签
    created = models.DateTimeField(auto_now_add=True) # 好友关系创建时间
    
    def friend_info(self):
        return {
            "toUser": self.to_user.name,
            "remark": self.remark,
            "tags": self.tags,
            "created": self.created.strftime("%Y-%m-%d %H:%M:%S"),
            "nick_name": self.to_user.nick_name,
            "portrait": self.to_user.portrait
        }
    
    def serialize(self):
        return {
            "fromUser": self.from_user.name,
            "toUser": self.to_user.name,
            "remark": self.remark,
            "tags": self.tags,
            "created": self.created.strftime("%Y-%m-%d %H:%M:%S")
        }

#好友申请表
class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE) # 申请用户
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE) # 被申请用户
    apply_message = models.CharField(max_length=250, blank=True) # 申请消息
    apply_time = models.DateTimeField(auto_now_add=True) # 申请时间
    status = models.CharField(max_length=10, choices=(('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined'))) # 申请状态：等待、成功、被拒绝

    def serialize(self):
        return {
            "fromUser": self.from_user.name,
            "toUser": self.to_user.name,
            "applyMessage": self.apply_message,
            "applyTime": self.apply_time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.status
        }
    
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