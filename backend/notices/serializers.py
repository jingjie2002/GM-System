"""公告序列化器"""

from rest_framework import serializers
from .models import Notice


class NoticeSerializer(serializers.ModelSerializer):
    """公告序列化器"""
    
    # 显示类型的中文名称
    notice_type_display = serializers.CharField(source='get_notice_type_display', read_only=True)
    
    class Meta:
        model = Notice
        fields = [
            'id', 'title', 'content',
            'notice_type', 'notice_type_display',
            'priority', 'status',
            'start_time', 'end_time', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
