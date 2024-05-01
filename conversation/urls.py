from django.contrib import admin
from django.urls import path, include
import conversation.views as views

urlpatterns = [
    path(''), # 获取会话列表
    path('search/', views.search_conversation),


    path('create/'), # 创建会话
    path('delete/'), # 删除会话
    path('fix/', views.fix_conversation), # 修改会话信息
    path('exit/'), # 退出会话

    path('invite/'), # 邀请好友
    path('accept/'), # 管理员接受邀请
    path('refuse/'), # 管理员拒绝邀请
    path('kick/'), #  管理员将成员踢出会话

    path('send/'), # 发送消息
    path('delete/'), # 删除消息
    path('read/'), # 标记消息为已读
    path('history/') # 获取指定会话详情

]