from django.db import models
from user.models import User
from django.utils import timezone


# Create your models here.
# 好友关系表
class Friendship(models.Model):
    from_user = models.ForeignKey(User, related_name='me', on_delete=models.CASCADE, db_index=True) # 该用户
    to_user = models.ForeignKey(User, related_name='friend', on_delete=models.CASCADE, db_index=True) # 好友用户
    alias = models.CharField(max_length=100, null=True, help_text='好友备注名') # 好友备注
    tags = models.ManyToManyField("UserTag", related_name="tag_friendship", blank=True, help_text="标签") # 用户标签
    description = models.CharField(max_length=250, null=True, help_text='好友描述') # 好友描述
    created_time = models.DateTimeField(auto_now_add=True) # 好友关系创建时间
    
    def friend_profile(self): # 好友信息
        return_data = {
            "alias": self.alias,
            "description": self.description,
            "tag": [tag.__str__() for tag in self.tags.all()],
            "createdTime": self.created_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        for key,value in self.to_user.__friend_info__().items():
            return_data[key] = value
        return return_data
    
    def set_alias(self, alias): # 修改备注
        self.alias = alias
        self.save()
    def set_description(self, description): # 修改描述
        self.description = description
        self.save()

    def get_tags(self):
        return [tag.__str__() for tag in self.tags.all()]

    def add_tag(self, tag): # 添加标签
        if not UserTag.objects.filter(name=tag, user=self.from_user).exists():
            new_tag = UserTag(name=tag, user=self.from_user)
            new_tag.save()
            self.tags.add(new_tag)
            self.save()
            new_tag.add_friendship(self)
            return True
        else: # 标签已存在
            return False
        
    def delete_tag(self, tag): # 删除标签

        if UserTag.objects.filter(name=tag, user=self.from_user).exists():
            del_tag = UserTag.objects.get(name=tag, user=self.from_user)
            del_tag.delete()
            self.tags.remove(del_tag)
            self.save()
            return True
        else:
            return False
    

    class Meta: # 确保(from_user, to_user)有序对是唯一的
        unique_together = ('from_user', 'to_user')


#好友申请表
class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE) # 申请用户
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE) # 被申请用户
    updated_time = models.DateTimeField(default=timezone.now) # 申请时间
    updated_message = models.CharField(max_length=250, null=True) # 最后一条申请消息
    status = models.IntegerField(choices=((0, 'Pending'), (1, 'Accepted'), (2, 'Declined')), default=0) # 申请状态：等待、成功、被拒绝

    def from_user_profile(self)->dict: # 申请用户信息
        return_data = self.from_user.__info__()
        return_data['updatedTime'] = self.updated_time.strftime("%Y-%m-%d %H:%M:%S")
        return_data['updatedMessage'] = self.updated_message
        return_data['status'] = self.status
        return return_data
    
    def to_user_profile(self)->dict: # 被申请用户信息
        return_data = self.to_user.__info__()
        return_data['updatedTime'] = self.updated_time.strftime("%Y-%m-%d %H:%M:%S")
        return_data['updatedMessage'] = self.updated_message
        return_data['status'] = self.status
        return return_data

    def accept(self)->bool: # 接受申请
        if int(self.status) == 1:  # 在数据库中存储的时为str类型
            return False # 已经被接受，不能再次接受
        else: # 未被接受
            self.status = 1
            self.save()
            # 建立好友关系
            friendship1 = Friendship(from_user=self.to_user, to_user=self.from_user)
            friendship2 = Friendship(from_user=self.from_user, to_user=self.to_user)
            friendship1.save()
            friendship2.save()
            return True

    def reject(self)->bool: # 拒绝申请
        if int(self.status) == 0:   
            self.status = 2
            self.save()
            return True
        return False # 已经被接受或拒绝，不能再次拒绝
    ## Q:拒绝申请之后，还可以再次申请，但不记录"申请曾被拒绝"这条消息

    def update_message(self, message):
        if message == "":
            message = "你好，我是"+self.from_user.name+"，很高兴认识你。"
        self.updated_message = message
        self.updated_time = timezone.now()
        self.save()


# 好友申请信息
class FriendRequestMessage(models.Model):
    request = models.ForeignKey(FriendRequest, related_name='messages', on_delete=models.CASCADE) # 好友申请
    message = models.CharField(max_length=250) # 消息内容
    message_time = models.DateTimeField(default=timezone.now) # 消息时间

class UserTag(models.Model): # 用户定义的标签集
    name = models.CharField(max_length=100) # 标签名称
    user = models.ForeignKey(User, related_name='user_tag', on_delete=models.CASCADE) # 标签所属用户
    friendships = models.ManyToManyField(Friendship, related_name='friendship_tag', blank=True) # 标签下的好友
    def __str__(self):
        return self.name
    def get_tag_friends(self): # 标签下的好友
        return self.friendships.all()
    
    def __friends_info__(self): # 标签下的好友信息
        print(self.tag_friendship.all())
        return [friendship.friend_profile() for friendship in self.tag_friendship.all()]
    
    def add_friendship(self, friendship): # 添加好友关系到标签
        self.friendships.add(friendship)
        self.save()
    
    def remove_friendship(self, friendship): # 从标签移除好友关系
        self.friendships.remove(friendship)
        self.save()
        
