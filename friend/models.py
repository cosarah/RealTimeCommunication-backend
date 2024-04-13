from django.db import models
from user.models import User

# Create your models here.
# 好友关系表
class Friendship(models.Model):
    from_user = models.ForeignKey(User, related_name='friendship_creator', on_delete=models.CASCADE, db_index=True) # 该用户的所有好友
    to_user = models.ForeignKey(User, related_name='friend', on_delete=models.CASCADE, db_index=True) # 好友用户
    remark = models.CharField(max_length=100, blank=True, help_text='好友备注') # 好友备注
    tag = models.CharField(max_length=100, blank=True) # 用户标签
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