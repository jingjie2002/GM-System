"""
玩家序列化器

序列化 (Serialization) 是什么？
-----------------------------
通俗来说，序列化就是把 Python 对象"翻译"成 JSON 字符串，让前端能读懂。
"""

from rest_framework import serializers
from .models import Player


class PlayerSerializer(serializers.ModelSerializer):
    """
    玩家序列化器 (完整版)
    用于详情页、创建和更新
    """

    class Meta:
        model = Player
        # 🟢 显式列出所有字段，确保 uuid 被包含
        fields = [
            'id', 'uuid', 'nickname',
            'level', 'gold', 'diamond',
            'status', 'created_at', 'updated_at'
        ]

        # 只读字段（前端不能修改）
        # 注意: uuid 必须是只读的
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']


class PlayerListSerializer(serializers.ModelSerializer):
    """
    玩家列表序列化器 (精简版)
    用于列表接口，减少数据传输
    """

    class Meta:
        model = Player
        # 🟢 在列表页也返回 uuid，方便前端进行某些操作（如复制UUID）
        fields = [
            'id', 'uuid', 'nickname',
            'level', 'gold', 'diamond',
            'status', 'created_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at']