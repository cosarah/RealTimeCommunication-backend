from django.contrib import admin
from django.urls import path, include
import conversation.views as views

urlpatterns = [
    path('', views.get_all_conversation_list), # 获取全部会话列表
    path('private/', views.get_private_message_list), # 获取私信会话列表
    path('private/messages/', views.get_private_message_list), # 获取私信消息列表
    path('private/send/', views.send_private_message), # 发送消息
    path('private/delete/', views.delete_private_message) # 删除私信消息

    # path('group/'), # 获取群组会话列表
    # path('group/create/'), # 创建会话
    # path('group/delete/'), # 删除会话
    # path('group/messages/'), # 获取群组消息列表
    # path('group/send/'), # 发送群组消息
    # path('group/delete/'), # 删除群组消息

    # path('group/quit/'), # 退出群组
    # path('group/user_fix/', views.fix_user_conversation), # 修改会话中用户信息

    # path('group/set/title/', views.set_group_title), # 设置群名称
    # path('group/announce/', views.set_announcement), # 发布群公告
    # path('group/set/owner/', views.set_group_owner), # 转移群主
    # path('group/add/admin/'), # 添加管理员
    # path('group/remove/admin/'), # 移除管理员

    # path('group/invite/'), # 成员邀请好友
    # path('group/accept/'), # 管理员接受邀请
    # path('group/refuse/'), # 管理员拒绝邀请
    # path('group/add/member/'), # 添加群成员
    # path('group/remove/member/'), # 移除群成员
]