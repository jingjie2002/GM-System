"""CDK API 路由"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CDKViewSet

router = DefaultRouter()
router.register(r'cdks', CDKViewSet, basename='cdk')

urlpatterns = [
    path('', include(router.urls)),
]
