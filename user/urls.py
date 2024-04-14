from django.urls import path, include
import user.views as views

urlpatterns = [
    path('login', views.login), # 登录页 （初始页面）
    path('register', views.register), # 注册页
    path('user',views.get_user_info),# 获取用户信息
    path('user/fix', views.fix_user_info), # 修改个人资料
    # path('user/fix/password', views.fix_password), # 修改密码
    path('user/close', views.close), # 注销账号
]
