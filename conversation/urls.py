from django.contrib import admin
from django.urls import path, include
import conversation.views as views

urlpatterns = [
    path('', views.get_all_conversation_list), # 获取全部会话列表

# 私聊系统
    path('private', views.get_private_conversation_list), # 获取私信会话列表
    path('private/message', views.get_private_message_list), # 获取私信消息列表
    path('private/message/send', views.send_private_message), # 发送消息
    path('private//message/delete', views.delete_private_message), # 删除私信消息

# 群聊系统
    ## 群聊管理
    path('group', views.get_group_conversation_list), # 获取群组会话列表
    path('group/create', views.create_group_conversation), # 创建会话
    path('group/delete', views.delete_group_conversation), # 删除会话

    ## 群聊信息管理
    path('group/messages', views.get_group_message_list), # 获取群组消息列表
    path('group/message/send', views.send_group_message), # 发送群组消息
    path('group/message/delete', views.delete_group_message), # 删除群组消息
    
    ## 群聊设置
    path('group/set/title', views.set_group_title), # 设置群名称
    path('group/set/announce', views.set_announcement), # 发布群公告
    path('group/set/owner', views.set_owner), # 转移群主
    path('group/set/admin/add', views.add_admin), # 添加管理员
    path('group/set/admin/remove', views.remove_admin), # 移除管理员
    
    ## 群聊成员管理
    path('group/member', views.get_group_members), # 获取群成员列表
    # path('group/member/invite', views.invite_group_member), # 成员邀请好友
    # path('group/member/accept', views.accept_group_invitation), # 管理员接受邀请
    # path('group/member/reject', views.reject_group_invitation), # 管理员拒绝邀请
    # path('group/member/add', views.add_group_member), # 添加群成员
    # path('group/member/remove', views.remove_group_member), # 移除群成员
    path('group/member/quit', views.quit_group), # 退出群组
    path('group/member/fix', views.fix_user_group_conversation) # 修改会话中用户信息
]