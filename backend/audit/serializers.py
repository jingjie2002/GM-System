"""审计日志序列化器"""
from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """
    审计日志序列化器
    """
    # 增加一个只读字段，显示管理员的用户名 (例如 "admin")
    # 注意：前端代码里已经兼容了 admin_name 和 admin_username
    admin_username = serializers.CharField(source='admin.username', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'action',
            'admin',            # 管理员 ID
            'admin_username',   # 管理员名字
            'app_label',
            'model_name',
            'target',
            'details',
            'ip_address',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']