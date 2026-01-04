"""
玩家 API 路由配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# 🟢 引入 BillingAPIView
from .views import PlayerViewSet, DashboardStatsView, BillingAPIView

# 创建路由器
router = DefaultRouter()
router.register(r'players', PlayerViewSet, basename='player')

# URL 配置
urlpatterns = [
    # 仪表盘统计接口
    path('players/dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),

    # 🟢 新增：财务账单接口
    path('players/billing/info/', BillingAPIView.as_view(), name='billing-info'),

    # 自动生成的 ViewSet 路由
    path('', include(router.urls)),
]