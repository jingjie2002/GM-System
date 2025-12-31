"""
玩家 API 路由配置

Router 的工作原理
----------------
DRF 的 Router 会自动为 ViewSet 生成 URL 路由：

    router.register('players', PlayerViewSet)
    
自动生成:
    GET    /players/          → list()
    POST   /players/          → create()
    GET    /players/{id}/     → retrieve()
    PUT    /players/{id}/     → update()
    DELETE /players/{id}/     → destroy()
    
自定义 @action 也会自动注册:
    POST   /players/{id}/add_gold/  → add_gold()
    POST   /players/{id}/ban/       → ban()
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlayerViewSet


# 创建路由器
router = DefaultRouter()

# 注册 ViewSet
# 'players' 是 URL 前缀，最终 URL 会是 /api/players/
router.register(r'players', PlayerViewSet, basename='player')

# URL 配置
urlpatterns = [
    path('', include(router.urls)),
]
