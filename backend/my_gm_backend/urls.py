"""
URL configuration for my_gm_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Admin 后台
    path("admin/", admin.site.urls),
    
    # ========== JWT 认证 ==========
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    # ========== API 路由 ==========
    path("api/", include("players.urls")),   # 玩家 API: /api/players/
    path("api/", include("mails.urls")),     # 邮件 API: /api/mails/
    path("api/", include("notices.urls")),   # 公告 API: /api/notices/
    path("api/", include("cdks.urls")),      # CDK API:  /api/cdks/
]


