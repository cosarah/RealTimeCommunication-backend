from django.urls import path, include
import friend.views as views
urlpatterns = [
    path('', views.get_friend_list), # 获取好友列表
    path('search/<search_str>', views.get_friend_list), # 搜索用户
    path('<friend_id>', views.get_friend_profile), # 获取好友资料
    path('request', views.get_friend_request_list), # 显示好友请求列表
    path('add/<friend_id>', views.add_friend), # 添加好友
    path('delete/<friend_id>', views.delete_friend), # 删除好友
]