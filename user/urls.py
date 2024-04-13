from django.urls import path, include
import user.views as views

urlpatterns = [
    path('login', views.login), # 登录页 （初始页面）
    path('register', views.register), # 注册页
    path('logout', views.logout), # 退出登录
    path('user',views.get_user_info),# 获取用户信息
    path('user/fix', views.fix_user_info), # 修改个人资料
    path('user/friend', views.get_friend_list), # 好友列表页，显示好友列表
    path('user/friend/search/<search_str>', views.get_friend_list), # 搜索好友页，搜索好友
    path('user/friend/<friend_id>', views.get_friend_profile), # 好友资料页，显示好友资料

    path('user/friend/request', views.get_friend_request_list), # 好友请求列表页，显示好友请求列表
    
    path('user/friend/add', views.add_friend), # 添加好友
    # path('user/friend/delete', views.delete_friend), # 删除好友

    # path('user/profile', views.get_profile), # 个人资料页
    # path('user/profile/update', views.update_profile), # 更新个人资料

    # path('user/conversations', views.get_conversation_list), # 聊天列表页
    # path('user/conversations/<conversation_id>', views.get_conversation_messages), # 聊天详情页
]
