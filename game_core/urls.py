from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views  # <--- 只有在这里才能引用 views，因为 views.py 就在旁边

router = DefaultRouter()
# 如果你之前注册了 API，放在这里
# router.register(r'players', views.PlayerViewSet)

urlpatterns = [
    # 1. 首页路径 -> 指向 Dashboard 界面
    path('', views.index, name='index'),

    # 2. API 路径 -> 指向 DRF 接口界面
    # 访问 http://127.0.0.1:8000/api/ 时显示
    path('api/', include(router.urls)),
    path('tables/', views.tables, name='tables'),
    path('billing/', views.billing, name='billing'),
    path('profile/', views.profile, name='profile'),
    path('sign-up/', views.sign_up, name='sign_up'),
]