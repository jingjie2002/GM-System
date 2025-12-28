"""公告视图集"""

from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.utils import timezone
from .models import Notice
from .serializers import NoticeSerializer


class NoticeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    公告 API 视图集（只读）
    
    自动过滤：只返回当前有效的公告
    - status = 'published' (已发布)
    - start_time <= 当前时间 <= end_time
    """
    
    serializer_class = NoticeSerializer
    permission_classes = [AllowAny]  # 公告对所有人可见
    
    def get_queryset(self):
        """
        获取当前有效的公告列表
        
        过滤条件:
        1. 状态为"已发布"
        2. 当前时间在生效时间范围内
        """
        now = timezone.now()
        return Notice.objects.filter(
            status=Notice.Status.PUBLISHED,
            start_time__lte=now,
            end_time__gte=now
        ).order_by('-priority', '-created_at')
