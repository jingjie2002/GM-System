"""审计日志视图集"""

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    审计日志 API 视图集 (只读)

    用于前端后台展示操作记录。
    仅支持:
    - GET /api/audit/ : 获取日志列表 (支持分页、搜索、排序)
    - GET /api/audit/{id}/ : 获取单条日志详情
    """

    # 1. 查询集：默认获取所有日志，并按时间倒序排列 (最新的在最前面)
    queryset = AuditLog.objects.all().order_by('-created_at')

    # 2. 序列化器：定义数据返回格式
    serializer_class = AuditLogSerializer

    # 3. 权限：必须登录的管理员才能查看
    permission_classes = [IsAuthenticated]

    # 4. 搜索与排序配置
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    # 支持搜索的字段
    search_fields = ['admin__username', 'target', 'action', 'details']

    # 支持排序的字段
    ordering_fields = ['created_at', 'action']