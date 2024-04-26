from django.utils import timezone
from django.db import models

from utils.utils_require import MAX_CHAR_LENGTH

# 可采用Django REST framework 的序列化器避免手写序列化代码
# 一般外键链接主键
# related_name 反向查询时使用的别名
# db_index 索引
# null=True 允许为空
# blank=True 允许为空白字符
# verbose_name 字段名
# default 默认值
# on_delete=models.CASCADE 级联删除
# unique=True 唯一约束
# auto_now_add=True 创建时间（只读）
# auto_now=True 更新时间（只读）
# choices 选项

# 用户表
class User(models.Model):
    # 隐私信息，可用于认证
    name = models.CharField(max_length=MAX_CHAR_LENGTH, primary_key=True) # 用户名，作为主键
    password = models.CharField(max_length=MAX_CHAR_LENGTH) # 密码 TODO: 加密
    phone = models.CharField(max_length=11, null=True, verbose_name='手机号码', db_index=True, unique=True) # 手机号码，可为空
    email = models.EmailField(max_length=100, null=True, verbose_name='邮箱', db_index=True, unique=True) # 邮箱

    # 状态信息
    create_time = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    is_online = models.BooleanField(default=False, verbose_name='是否在线') # 是否在线
    logout_time = models.DateTimeField(default=None, null=True, verbose_name='登出时间') # 登出时间，可为空
    
    # 个性化信息
    nick_name = models.CharField(max_length=MAX_CHAR_LENGTH, default=name, null=True, verbose_name='昵称') # 昵称，可为空
    portrait = models.URLField(null=True, blank=True, verbose_name='头像') # 头像url
    PORTRAIT_CHOICES = ( # 头像类型
        (0, '空'),
        (-1, '自定义'),
        (1, '默认1'), (2, '默认2'), (3, '默认3'), (4, '默认4'), (5, '默认5'), (6, '默认6'), (7, '默认7'), (8, '默认8'), (9, '默认9'), (10, '默认10')
    )
    portrait_type = models.IntegerField(choices=PORTRAIT_CHOICES, default=0, verbose_name='头像类型') # 头像类型
    introduction = models.CharField(max_length=250, null=True, blank=True, verbose_name='个人简介') # 个人简介
    birthday = models.DateField(default=None, null=True, verbose_name='生日') # 生日
    GENDER_CHOICES = ( # 性别
        (0, '未知'),
        (1, '男'),
        (2, '女')
    )
    gender = models.IntegerField(choices=GENDER_CHOICES, default=0, verbose_name='性别')
    age = models.IntegerField(null=True, blank=True, verbose_name='年龄') # 年龄，可为空
    location = models.CharField(max_length=100, null=True, blank=True, verbose_name='所在地') # 所在地，可为空


    class Meta: # 快速搜索
        indexes = [models.Index(fields=["name"])]
        
    def __all_info__(self):
        return {
            "userName": self.name, 
            "nickName": self.nick_name,
            "createTime": self.create_time,
            "introduction": self.introduction,
            "birthday": self.birthday,
            "portraitType": self.portrait_type,
            "portrait": self.portrait,
            "gender": self.gender,
            "age": self.age,
            "location": self.location,
            "isOnline":self.is_online,
            "logoutTime":self.logout_time,
            "phone": self.phone,
            "email": self.email,
            "password": self.password
        }

    def __friend_info__(self): # 序列化，不含密码、电话、邮箱等隐私信息
        return {
            "userName": self.name, 
            "nickName": self.nick_name,
            "introduction": self.introduction,
            "birthday": self.birthday,
            "portrait": self.portrait,
            "portraitType": self.portrait_type,
            "gender": self.gender,
            "age": self.age,
            "location": self.location,
            "isOnline":self.is_online,
            "logoutTime":self.logout_time
        }
    
    def __info__(self): # 不认识的人可以用这个方法查看用户信息
        return {
            "userName": self.name,
            "nickName": self.nick_name,
            "introduction": self.introduction,
            "portrait": self.portrait,
            "portraitType": self.portrait_type,
            "gender": self.gender,
            "age": self.age,
            "location": self.location,
            "isOnline":self.is_online,
            "logoutTime":self.logout_time
        }
    
    def __str__(self) -> str:
        return self.name
    
    def __logout__(self):
        self.is_online = False
        self.logout_time = timezone.now()
        self.save()

    def __login__(self):
        self.is_online = True
        self.save()

    ## TODO:数据校验：如邮箱格式、电话号码格式等
    ## TODO:密码加密
    ## TODO:用户设置