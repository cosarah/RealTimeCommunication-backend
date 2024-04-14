from django.db import models
from user.models import User
from django.utils import timezone


# Create your models here.
# 好友关系表
class Friendship(models.Model):
    from_user = models.ForeignKey(User, related_name='friendship_creator', on_delete=models.CASCADE, db_index=True) # 该用户的所有好友
    to_user = models.ForeignKey(User, related_name='friend', on_delete=models.CASCADE, db_index=True) # 好友用户
    remark = models.CharField(max_length=100, null=True, help_text='好友备注') # 好友备注
    tag = models.CharField(max_length=100, null=True) # 用户标签
    created = models.DateTimeField(auto_now_add=True) # 好友关系创建时间
    
    def friend_profile(self): # 好友信息
        return {
            "toUser": self.to_user.name,
            "remark": self.remark,
            "tag": self.tag,
            "created": self.created.strftime("%Y-%m-%d %H:%M:%S"),
            "friend_info": self.to_user.serialize()
        }
    class Meta: # 确保(from_user, to_user)有序对是唯一的
        unique_together = ('from_user', 'to_user')


#好友申请表
class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE) # 申请用户
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE) # 被申请用户
    update_time = models.DateTimeField(default=timezone.now) # 申请时间
    status = models.CharField(max_length=10, choices=((0, 'Pending'), (1, 'Accepted'), (2, 'Declined'))) # 申请状态：等待、成功、被拒绝

    def from_user_profile(self): # 申请用户信息
        return {
            "fromUserInfo": self.from_user.__info__(),
            "applyTime": self.update_time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.status
        }
    
    def to_user_profile(self): # 被申请用户信息
        return {
            "toUserInfo": self.to_user.__info__(),
            "applyTime": self.update_time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.status
        }
    
    def accept(self): # 接受申请
        self.status = 1
        self.save()
        # 建立好友关系
        friendship1 = Friendship(from_user=self.to_user, to_user=self.from_user)
        friendship2 = Friendship(from_user=self.from_user, to_user=self.to_user)
        friendship1.save()
        friendship2.save()

    def decline(self): # 拒绝申请
        self.status = 2
        self.save()


# 好友申请信息
class FriendRequestMessage(models.Model):
    request = models.ForeignKey(FriendRequest, related_name='messages', on_delete=models.CASCADE) # 好友申请
    message = models.CharField(max_length=250) # 消息内容
    message_time = models.DateTimeField(default=timezone.now) # 消息时间