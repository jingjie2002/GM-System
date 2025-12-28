from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. 自动刷新工具 (Tailwind 必需)
    # 2. 把所有访问请求“转接”给 game_core 应用
    # 注意：这里用 include，绝对不要写 views.index
    path('', include('game_core.urls')),
]