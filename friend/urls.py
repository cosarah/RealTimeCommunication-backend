from django.urls import path, include
import friend.views as views
urlpatterns = [
    path('add/', views.add_friend), # 添加好友
    path('delete/', views.delete_friend), # 删除好友
    path('', views.get_friend_list), # 获取好友列表
    path('accept/', views.accept_friend_request), # 接受好友请求
    path('reject/', views.reject_friend_request), # 拒绝好友请求
    # path('search', views.get_friend_list), # 搜索用户
    path('profile/', views.get_friend_profile), # 获取好友资料
    path('request/', views.get_friend_request_list), # 显示好友请求列表
    
]