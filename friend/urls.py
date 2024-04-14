from django.urls import path, include
import friend.views as views
urlpatterns = [
    path('', views.get_friend_list), # 获取好友列表
    # path('search', views.get_friend_list), # 搜索用户
    path('profile/', views.get_friend_profile), # 获取好友资料
    path('request/', views.get_friend_request_list), # 显示好友请求列表
    path('add/', views.add_friend), # 添加好友
    path('delete/', views.delete_friend), # 删除好友
]