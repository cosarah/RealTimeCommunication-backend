from django.urls import path, include
import friend.views as views
urlpatterns = [
    path('', views.get_friend_list), # 获取好友列表
    path('search/', views.get_user_profile), # 获取用户资料/搜索用户
    path('profile/', views.get_friend_profile), # 获取好友资料

    path('add/', views.add_friend), # 添加好友
    path('delete/', views.delete_friend), # 删除好友
    path('accept/', views.accept_friend_request), # 接受好友请求
    path('reject/', views.reject_friend_request), # 拒绝好友请求
    path('request/', views.get_friend_request_list), # 显示好友请求列表
    
    path('fix/alias/', views.fix_friend_alias), # 修改好友备注
    path('fix/description/', views.fix_friend_description), # 修改好友描述
    path('fix/',views.fix_friend_profile), # 修改好友资料（包括备注、描述、标签，若标签存在，则删除之，若不存在，则添加之）
    path('fix/tag/add/', views.add_friend_tag), # 添加好友标签
    path('fix/tag/delete/', views.delete_friend_tag), # 删除好友标签

    path('usertag/',views.get_user_tag), # 获取标签列表
    path('tags/', views.get_friend_all_tag_list), # 获取以标签分类的好友列表
    # path('tag/', views.get_friend_list_by_tag) # 获取某标签的全部好友
]