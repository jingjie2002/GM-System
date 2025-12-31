"""邮件序列化器"""

from rest_framework import serializers
from .models import Mail


class MailSerializer(serializers.ModelSerializer):
    """邮件完整序列化器"""
    
    # 显示发送者用户名而不是 ID
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    # 显示接收者昵称
    receiver_name = serializers.CharField(source='receiver.nickname', read_only=True)
    
    class Meta:
        model = Mail
        fields = [
            'id', 'title', 'content',
            'sender', 'sender_name',
            'receiver', 'receiver_name',
            'is_global', 'item_id', 'item_count',
            'expires_at', 'is_claimed', 'created_at'
        ]
        read_only_fields = ['id', 'sender', 'sender_name', 'is_claimed', 'created_at']


class MailListSerializer(serializers.ModelSerializer):
    """邮件列表序列化器（精简版）"""
    
    class Meta:
        model = Mail
        fields = ['id', 'title', 'is_global', 'is_claimed', 'expires_at', 'created_at']
