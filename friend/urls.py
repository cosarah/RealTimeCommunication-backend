from django.urls import path, include
import friend.views as views
urlpatterns = [
    path('', views.get_friend_list), # 获取好友列表
    path('add/', views.add_friend), # 添加好友
    path('delete/', views.delete_friend), # 删除好友
    path('accept/', views.accept_friend_request), # 接受好友请求
    path('reject/', views.reject_friend_request), # 拒绝好友请求
    path('profile/', views.get_friend_profile), # 获取好友资料
    path('fix/alias', views.fix_friend_alias), #修改好友备注
    path('fix/tag', views.fix_friend_tag), #修改好友标签
    path('fix/description', views.fix_friend_description), #修改好友描述
    path('fix',views.fix_friend_profile), #修改好友资料
    path('request/', views.get_friend_request_list), # 显示好友请求列表
    path('search/', views.get_user_profile), # 获取用户资料/搜索用户
    path('group/', views.get_friend_group_list), # 获取群组列表
]