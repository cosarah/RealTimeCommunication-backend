from django.db import models
from user.models import User
from django.utils import timezone


# Create your models here.
# 好友关系表
class Friendship(models.Model):
    from_user = models.ForeignKey(User, related_name='me', on_delete=models.CASCADE, db_index=True) # 该用户
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
    update_message = models.CharField(max_length=250, null=True) # 最后一条申请消息
    status = models.CharField(max_length=10, choices=((0, 'Pending'), (1, 'Accepted'), (2, 'Declined'))) # 申请状态：等待、成功、被拒绝

    def from_user_profile(self): # 申请用户信息
        return {
            self.from_user.__info__(),
        }
    
    def to_user_profile(self): # 被申请用户信息
        return {
            self.to_user.__info__(),
        }
    
    def __str__(self):
        return{
            "fromUser": self.from_user_profile(),
            "toUser": self.to_user_profile(),
            "updateTime": self.update_time.strftime("%Y-%m-%d %H:%M:%S"),
            "updateMessage": self.update_message,
            "status": self.status
        }

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

    def reject(self): # 拒绝申请
        if self.status == 0:   
            self.status = 2
            self.save()
            return True
        return False # 已经被接受或拒绝，不能再次拒绝
    ## Q:拒绝申请之后，还可以再次申请，但不记录"申请曾被拒绝"这条消息

    def _update_message_(self, message):
        self.update_message = message
        self.update_time = timezone.now()
        self.save()


# 好友申请信息
class FriendRequestMessage(models.Model):
    request = models.ForeignKey(FriendRequest, related_name='messages', on_delete=models.CASCADE) # 好友申请
    message = models.CharField(max_length=250) # 消息内容
    message_time = models.DateTimeField(default=timezone.now) # 消息时间